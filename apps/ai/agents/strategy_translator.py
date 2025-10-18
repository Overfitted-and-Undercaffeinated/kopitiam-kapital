"""
Strategy Translator Agent - Converts natural language to strategy JSON
Uses Groq Llama 3.3 70B for fast, accurate translation
"""
import json
import logging
import time
from typing import Dict, Optional
from openai import OpenAI

# Flexible imports
try:
    from ..utils.clients import get_groq_client
    from ..backtesting.builder import strategy_builder
except ImportError:
    from utils.clients import get_groq_client
    from backtesting.builder import strategy_builder

logger = logging.getLogger(__name__)

# System prompt for strategy translation
STRATEGY_TRANSLATOR_SYSTEM_PROMPT = """You are an expert trading strategy translator. Convert natural language trading strategies into structured JSON format.

**Available Indicators:**
- RSI (Relative Strength Index): {"type": "rsi", "period": 14}
- SMA (Simple Moving Average): {"type": "sma", "period": 20}
- EMA (Exponential Moving Average): {"type": "ema", "period": 20}
- MACD: {"type": "macd"} (uses default 12/26/9)
- Bollinger Bands: {"type": "bollinger", "period": 20, "std_dev": 2.0}
- ATR (Average True Range): {"type": "atr", "period": 14}
- Stochastic: {"type": "stochastic", "k_period": 14, "d_period": 3}
- ADX (Trend Strength): {"type": "adx", "period": 14}

**Available Conditions:**
- Comparisons: ">", "<", ">=", "<=", "==", "!="
- Crossovers: "crosses_above", "crosses_below"

**Rule Structure:**
Entry/Exit rules must specify:
- "indicator": name of indicator (or "price" for current price)
- "condition": comparison operator
- "value": number or another indicator name

**Examples:**

1. "buy when RSI is below 30"
{
  "name": "RSI Oversold",
  "description": "Buy when RSI drops below 30 (oversold condition)",
  "category": "Mean Reversion",
  "indicators": [{"type": "rsi", "period": 14}],
  "entry_rules": [{"indicator": "rsi", "condition": "<", "value": 30}],
  "exit_rules": [{"indicator": "rsi", "condition": ">", "value": 70}],
  "position_sizing": {"type": "fixed_percent", "value": 0.1},
  "risk_management": {"stop_loss_percent": 0.05, "take_profit_percent": 0.10}
}

2. "buy when price crosses above 50-day moving average"
{
  "name": "50-Day SMA Breakout",
  "description": "Buy when price breaks above 50-day moving average",
  "category": "Trend Following",
  "indicators": [{"type": "sma", "period": 50}],
  "entry_rules": [{"indicator": "price", "condition": "crosses_above", "value": "sma_50"}],
  "exit_rules": [{"indicator": "price", "condition": "crosses_below", "value": "sma_50"}],
  "position_sizing": {"type": "fixed_percent", "value": 0.1},
  "risk_management": {"stop_loss_percent": 0.05, "take_profit_percent": 0.15}
}

3. "buy when price is below the 2 week low"
{
  "name": "2-Week Low Breakout",
  "description": "Buy when price drops below the 2-week (10-day) low",
  "category": "Mean Reversion",
  "indicators": [{"type": "sma", "period": 10}],
  "entry_rules": [{"indicator": "price", "condition": "<", "value": "sma_10"}],
  "exit_rules": [{"indicator": "price", "condition": ">", "value": "sma_10"}],
  "position_sizing": {"type": "fixed_percent", "value": 0.1},
  "risk_management": {"stop_loss_percent": 0.05, "take_profit_percent": 0.10}
}

4. "buy on MACD bullish crossover"
{
  "name": "MACD Bullish Crossover",
  "description": "Buy when MACD line crosses above signal line",
  "category": "Momentum",
  "indicators": [{"type": "macd"}],
  "entry_rules": [{"indicator": "macd", "condition": "crosses_above", "value": "macd_signal"}],
  "exit_rules": [{"indicator": "macd", "condition": "crosses_below", "value": "macd_signal"}],
  "position_sizing": {"type": "fixed_percent", "value": 0.12},
  "risk_management": {"stop_loss_percent": 0.04, "take_profit_percent": 0.12}
}

5. "mean reversion"
{
  "name": "Mean Reversion",
  "description": "Buy when RSI is oversold, sell when RSI is overbought",
  "category": "Mean Reversion",
  "indicators": [{"type": "rsi", "period": 14}],
  "entry_rules": [
    {"indicator": "rsi", "condition": "<", "value": 30}
  ],
  "exit_rules": [
    {"indicator": "rsi", "condition": ">", "value": 70}
  ],
  "position_sizing": {"type": "fixed_percent", "value": 0.10},
  "risk_management": {"stop_loss_percent": 0.05, "take_profit_percent": 0.10}
}

**Important Rules:**
1. Always include reasonable exit rules (opposite of entry or standard profit targets)
2. Use 10% position sizing as default
3. Use 5% stop loss and 10% take profit as defaults
4. For time-based indicators (2 weeks, 1 month), convert to trading days (5 days/week)
5. Indicator names in rules must match the format: "indicator_period" (e.g., "sma_50", "rsi", "macd")
6. Be conservative with risk management

Return ONLY valid JSON matching the structure above. No explanations outside the JSON."""

class StrategyTranslatorAgent:
    """
    Translates natural language trading strategies to executable JSON format
    
    Uses Groq Llama 3.3 70B for fast, accurate translation
    """
    
    def __init__(self, client: Optional[OpenAI] = None):
        self.name = "strategy_translator"
        self.client = client or get_groq_client()
        self.model = "llama-3.3-70b-versatile"
        logger.info(f"Initialized StrategyTranslatorAgent with model: {self.model}")
    
    async def translate_strategy(
        self,
        natural_language: str,
        symbol: str
    ) -> Dict:
        """
        Translate natural language strategy description to JSON
        
        Args:
            natural_language: Strategy description (e.g., "buy when RSI is below 30")
            symbol: Stock symbol for context
        
        Returns:
            Strategy JSON dict compatible with StrategyBuilder
            
        Raises:
            ValueError: If translation fails or produces invalid JSON
        """
        if not natural_language or not natural_language.strip():
            raise ValueError("Strategy description cannot be empty")
        
        logger.info(f"Translating strategy: '{natural_language}' for {symbol}")
        start_time = time.time()
        
        try:
            # Call Groq to translate
            strategy_json_str = await self._call_groq(natural_language, symbol)
            
            # Parse JSON
            strategy_def = json.loads(strategy_json_str)
            
            # Validate structure
            is_valid, error_msg = strategy_builder.validate_strategy(strategy_def)
            if not is_valid:
                raise ValueError(f"Invalid strategy structure: {error_msg}")
            
            # Log success
            latency = time.time() - start_time
            logger.info(
                f"Strategy translated successfully: '{strategy_def['name']}' "
                f"(latency: {latency*1000:.0f}ms)"
            )
            
            return strategy_def
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse strategy JSON: {e}")
            raise ValueError(
                f"Could not translate strategy to valid JSON. "
                f"Please rephrase your strategy description."
            )
        except Exception as e:
            logger.error(f"Strategy translation failed: {e}")
            raise ValueError(
                f"Could not translate strategy: {str(e)}. "
                f"Please try rephrasing your description."
            )
    
    async def _call_groq(
        self,
        natural_language: str,
        symbol: str,
        retry: bool = True
    ) -> str:
        """Call Groq API to translate strategy"""
        try:
            # Create user prompt with context
            user_prompt = f"""Translate this trading strategy to JSON:

Strategy: "{natural_language}"
Symbol: {symbol}

Remember to:
1. Create a clear, descriptive name
2. Include detailed description
3. Specify all required indicators
4. Define clear entry and exit rules
5. Use sensible risk management defaults

Return only valid JSON."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": STRATEGY_TRANSLATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistency
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from Groq")
            
            return content
            
        except Exception as e:
            if retry:
                logger.warning(f"Groq call failed, retrying: {e}")
                return await self._call_groq(natural_language, symbol, retry=False)
            else:
                raise
    
    def get_example_strategies(self) -> list:
        """
        Get list of example natural language strategies for user guidance
        
        Returns:
            List of example strategy descriptions
        """
        return [
            "buy when RSI is below 30",
            "buy when price crosses above 50-day moving average",
            "buy when price is below the 2 week low",
            "buy on MACD bullish crossover",
            "buy when Bollinger Bands touch lower band",
            "buy when price crosses above 200-day moving average",
            "buy when RSI is below 40 and MACD is positive",
            "buy when stochastic is oversold",
            "buy on golden cross (50 SMA crosses above 200 SMA)"
        ]

# Global instance
strategy_translator = StrategyTranslatorAgent()

