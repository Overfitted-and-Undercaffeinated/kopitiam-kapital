"""
Backtest Explainer Agent - Generates natural language explanations of backtest results
Uses Groq for fast, detailed performance analysis
"""
import logging
import time
import json
from typing import Dict, Optional
from openai import OpenAI

# Flexible imports
try:
    from ..utils.clients import get_groq_client
except ImportError:
    from utils.clients import get_groq_client

logger = logging.getLogger(__name__)

# System prompt for backtest explanation
BACKTEST_EXPLAINER_SYSTEM_PROMPT = """You are an expert trading analyst and educator. Your role is to explain backtest results in a clear, insightful, and conversational manner suitable for voice narration.

**Your audience**: Traders ranging from beginners to intermediates who want to understand if a strategy is worth using.

**Your tone**: Conversational, educational, and honest. Don't oversell or undersell - be realistic.

**Structure your explanation to cover:**

1. **Strategy Overview** (30 seconds)
   - Briefly explain what the strategy does in plain English
   - Who might use this strategy (trend followers, mean reversion traders, etc.)

2. **Performance Assessment** (60 seconds)
   - Overall verdict: Was it profitable? How profitable?
   - Win rate and what it means
   - Sharpe ratio and what it indicates about risk-adjusted returns
   - Total return vs buy-and-hold context

3. **Risk Analysis** (45 seconds)
   - Maximum drawdown and what it means for capital preservation
   - VaR (Value at Risk) - explain the worst-case loss in simple terms
   - Number of trades (is it too frequent? too infrequent?)
   - Average win vs average loss

4. **Key Insights** (30 seconds)
   - When did it work best? When did it struggle?
   - Any notable patterns or concerns
   - Profit factor context

5. **Recommendation** (15 seconds)
   - Should the user consider this strategy?
   - Any modifications they might explore
   - When to use it vs when to avoid it

**Guidelines:**
- Use simple language - avoid jargon or explain it when necessary
- Compare metrics to industry standards when relevant (Sharpe > 1 is good, > 2 is excellent)
- Be honest about limitations
- Make it conversational, like you're talking to a friend
- Keep it under 3 minutes when read aloud (aim for 400-500 words)
- Use natural transitions between sections
- Include specific numbers but round them for clarity (67% not 66.67%)

**Avoid:**
- Being overly technical
- Making promises about future performance
- Saying "in conclusion" or "to summarize" (just flow naturally)
- Listing bullet points (make it narrative)"""

# System prompt for strategy building from natural language
STRATEGY_BUILDER_SYSTEM_PROMPT = """You are an expert trading strategy designer and developer. Your role is to convert natural language strategy descriptions into precise, executable JSON-based trading rules.

**Your task**: Analyze what the user describes, extract the core strategy logic, and convert it into a structured format that can be backtested.

**Strategy JSON Format** (return ONLY valid JSON, no explanations):
{
    "name": "Human-readable strategy name",
    "description": "Clear description of what this strategy does",
    "category": "Trend Following|Mean Reversion|Momentum|Breakout|Technical|Other",
    "difficulty": "Beginner|Intermediate|Advanced",
    "indicators": [
        {"type": "rsi", "period": 14},
        {"type": "sma", "period": 20},
        {"type": "macd"},
        {"type": "bollinger_bands", "period": 20, "std_dev": 2},
        {"type": "atr", "period": 14}
    ],
    "entry_rules": [
        {"indicator": "rsi", "condition": "<", "value": "sma_20"},
        {"indicator": "price", "condition": "crosses_above", "value": "sma_20"}
    ],
    "exit_rules": [
        {"indicator": "rsi", "condition": ">", "value": 70}
    ],
    "position_sizing": {
        "type": "fixed_percent",
        "value": 0.1
    },
    "risk_management": {
        "stop_loss_percent": 0.05,
        "take_profit_percent": 0.10
    }
}

**Available Indicators**:
- rsi (period: 5-50)
- sma (period: 5-200)
- ema (period: 5-200)
- macd (fast: 12, slow: 26, signal: 9)
- bollinger_bands (period: 10-50, std_dev: 1-3)
- atr (period: 5-20)
- stochastic (period: 14)
- adx (period: 14)

**Conditions**:
- Comparison: <, >, ==, <=, >=
- Crossovers: crosses_above, crosses_below

**Guidelines**:
- Infer the most reasonable values if user doesn't specify
- Use RSI 14 as default RSI period
- Use SMA 20 for trend, SMA 50 for longer trends
- Stop loss typically 3-5%, take profit 10-15% for trend following
- Stop loss 2-3%, take profit 5-10% for mean reversion
- Only include indicators that are actually used in the rules
- Be realistic - suggest beginner difficulty for simple rules (1-2 indicators), intermediate for 2-3, advanced for 4+
- If the description is too vague or illogical, respond with an error object:
  {
    "error": true,
    "message": "Why this strategy doesn't work or is unclear",
    "suggestion": "What clarification or change is needed"
  }

**Examples**:
- "Buy when RSI is below 30" → RSI oversold, mean reversion
- "Buy when price breaks above 20-day moving average" → Momentum breakout, trend following
- "MACD crossover strategy" → MACD crosses above signal line for entry
- "Bollinger band squeeze with breakout" → Use Bollinger bands, enter on breakout"""

class BacktestExplainerAgent:
    """
    Generates natural language explanations of backtest results
    
    Produces detailed, conversational analysis suitable for voice narration
    """
    
    def __init__(self, client: Optional[OpenAI] = None):
        self.name = "backtest_explainer"
        self.client = client or get_groq_client()
        self.model = "llama-3.3-70b-versatile"
        logger.info(f"Initialized BacktestExplainerAgent with model: {self.model}")
    
    async def generate_explanation(
        self,
        strategy_name: str,
        strategy_description: str,
        metrics: Dict,
        symbol: str,
        period: str
    ) -> str:
        """
        Generate detailed explanation of backtest results
        
        Args:
            strategy_name: Name of the strategy
            strategy_description: Description of strategy logic
            metrics: Backtest metrics dict
            symbol: Stock symbol
            period: Time period tested
        
        Returns:
            Detailed explanation text (suitable for voice narration)
        """
        logger.info(f"Generating explanation for {strategy_name} on {symbol}")
        start_time = time.time()
        
        try:
            # Calculate risk/reward using MCP
            from utils.mcp_client import mcp_risk_client
            
            risk_reward_text = ""
            if mcp_risk_client.enabled:
                avg_win = metrics.get('avg_win', 0)
                avg_loss = abs(metrics.get('avg_loss', 0))
                
                if avg_win > 0 and avg_loss > 0:
                    risk_reward = await mcp_risk_client.calculate_risk_reward(
                        entry_price=100,  # Normalized
                        stop_loss=100 - avg_loss,
                        take_profit=100 + avg_win,
                        win_rate=metrics['win_rate'],
                        position_size=1
                    )
                    
                    if not risk_reward:
                        raise RuntimeError("MCP risk/reward calculation failed")
                    
                    risk_reward_text = f"""
Risk/Reward Analysis (MCP-Powered):
- Risk/Reward Ratio: {risk_reward['risk_reward_ratio']}
- Expected Value: ${risk_reward['expected_value']}
- Assessment: {risk_reward['recommendation']}
"""
            else:
                raise RuntimeError("MCP Risk Tools required for professional analysis")
            
            # Format metrics for prompt
            formatted_metrics = self._format_metrics(metrics)
            
            # Add risk/reward to formatted metrics
            if risk_reward_text:
                formatted_metrics += f"\n\n{risk_reward_text}"
            
            # Generate explanation using Groq
            explanation = await self._call_groq(
                strategy_name=strategy_name,
                strategy_description=strategy_description,
                metrics_text=formatted_metrics,
                symbol=symbol,
                period=period
            )
            
            # Log success
            latency = time.time() - start_time
            word_count = len(explanation.split())
            logger.info(
                f"Explanation generated: {word_count} words "
                f"(latency: {latency*1000:.0f}ms)"
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            # Return basic fallback explanation
            return self._generate_fallback_explanation(
                strategy_name, metrics, symbol, period
            )
    
    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics into readable text for LLM"""
        # Extract key metrics with safe defaults
        win_rate = metrics.get('win_rate', 0) * 100
        sharpe = metrics.get('sharpe_ratio', 0)
        total_return_pct = metrics.get('total_return_pct', 0) * 100
        max_drawdown = metrics.get('max_drawdown', 0) * 100
        num_trades = metrics.get('num_trades', 0)
        profit_factor = metrics.get('profit_factor', 0)
        avg_win = metrics.get('avg_win', 0)
        avg_loss = metrics.get('avg_loss', 0)
        
        # Format as readable text
        return f"""Win Rate: {win_rate:.1f}%
Sharpe Ratio: {sharpe:.2f}
Total Return: {total_return_pct:.1f}%
Maximum Drawdown: {max_drawdown:.1f}%
Number of Trades: {num_trades}
Profit Factor: {profit_factor:.2f}
Average Win: ${avg_win:.2f}
Average Loss: ${avg_loss:.2f}
Winning Trades: {metrics.get('winning_trades', 0)}
Losing Trades: {metrics.get('losing_trades', 0)}"""
    
    async def _call_groq(
        self,
        strategy_name: str,
        strategy_description: str,
        metrics_text: str,
        symbol: str,
        period: str,
        retry: bool = True
    ) -> str:
        """Call Groq API to generate explanation"""
        try:
            # Create user prompt
            user_prompt = f"""Analyze this backtest and provide a detailed explanation:

**Strategy**: {strategy_name}
**Description**: {strategy_description}
**Symbol**: {symbol}
**Period Tested**: {period}

**Performance Metrics**:
{metrics_text}

Please provide a comprehensive 2-3 minute explanation covering:
1. What this strategy does
2. How it performed overall
3. Risk considerations
4. Key insights
5. Your recommendation

Remember: Be conversational, educational, and honest. This will be read aloud."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": BACKTEST_EXPLAINER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,  # Moderate temperature for natural language
                max_tokens=800  # ~500-600 words
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from Groq")
            
            return content.strip()
            
        except Exception as e:
            if retry:
                logger.warning(f"Groq call failed, retrying: {e}")
                return await self._call_groq(
                    strategy_name, strategy_description, metrics_text,
                    symbol, period, retry=False
                )
            else:
                raise
    
    def _generate_fallback_explanation(
        self,
        strategy_name: str,
        metrics: Dict,
        symbol: str,
        period: str
    ) -> str:
        """Generate simple fallback explanation if LLM fails"""
        win_rate = metrics.get('win_rate', 0) * 100
        total_return = metrics.get('total_return_pct', 0) * 100
        sharpe = metrics.get('sharpe_ratio', 0)
        max_dd = metrics.get('max_drawdown', 0) * 100
        num_trades = metrics.get('num_trades', 0)
        
        # Simple template-based explanation
        performance = "profitable" if total_return > 0 else "unprofitable"
        quality = "good" if sharpe > 1 else "moderate" if sharpe > 0.5 else "poor"
        
        return f"""Let me walk you through the results of testing the {strategy_name} strategy on {symbol} from {period}.

This strategy generated {num_trades} trades over the period, with a win rate of {win_rate:.0f}%. Overall, it was {performance}, delivering a total return of {total_return:.1f}%.

From a risk-adjusted perspective, the Sharpe ratio of {sharpe:.2f} indicates {quality} risk-adjusted returns. The maximum drawdown was {abs(max_dd):.1f}%, meaning at worst, you would have seen your capital decline by that amount from peak.

{'This strategy shows promise and may be worth considering with proper risk management.' if total_return > 0 and sharpe > 1 else 'This strategy may need refinement or may not be suitable for current market conditions.'}

Remember, past performance does not guarantee future results. Always test strategies thoroughly and use appropriate position sizing."""

    async def build_strategy_from_description(
        self,
        description: str,
        symbol: str = None
    ) -> Dict:
        """
        Convert natural language strategy description to backtestable JSON rules
        
        Args:
            description: Natural language strategy description (e.g., "Buy when RSI below 30")
            symbol: Optional stock symbol for context
        
        Returns:
            Strategy JSON dict ready for backtesting or error dict
            {
                "name": "...",
                "description": "...",
                "category": "...",
                "indicators": [...],
                "entry_rules": [...],
                "exit_rules": [...],
                "position_sizing": {...},
                "risk_management": {...}
            }
            
            OR error response:
            {
                "error": true,
                "message": "Why this failed",
                "suggestion": "How to fix it"
            }
        """
        logger.info(f"Building strategy from description: {description[:100]}...")
        start_time = time.time()
        
        try:
            # Call Groq to convert description to JSON rules
            strategy_json = await self._call_groq_strategy_builder(description, symbol)
            
            # Validate the JSON
            if strategy_json.get("error"):
                logger.warning(f"Strategy validation failed: {strategy_json.get('message')}")
                return strategy_json  # Return error object as-is
            
            # Log success
            latency = time.time() - start_time
            logger.info(
                f"Strategy built successfully: '{strategy_json.get('name')}' "
                f"(latency: {latency*1000:.0f}ms)"
            )
            
            return strategy_json
            
        except Exception as e:
            logger.error(f"Failed to build strategy: {e}")
            return {
                "error": True,
                "message": f"Failed to interpret strategy: {str(e)}",
                "suggestion": "Please try rephrasing your strategy description with more specific indicators or entry/exit rules."
            }
    
    async def _call_groq_strategy_builder(
        self,
        description: str,
        symbol: str = None,
        retry: bool = True
    ) -> Dict:
        """Call Groq to convert natural language to strategy JSON"""
        try:
            # Build context
            context = f"Stock symbol: {symbol}" if symbol else "No specific symbol context"
            
            # Create user prompt
            user_prompt = f"""Convert this trading strategy description into precise JSON rules:

{context}

**Strategy Description**: {description}

Return ONLY valid JSON that matches the required format. No explanations, no markdown, just the JSON object."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": STRATEGY_BUILDER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent JSON
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from Groq")
            
            # Parse JSON from response
            content = content.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            strategy_dict = json.loads(content)
            
            return strategy_dict
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}. Content: {content[:200]}")
            if retry:
                logger.warning("Retrying strategy build...")
                return await self._call_groq_strategy_builder(description, symbol, retry=False)
            else:
                return {
                    "error": True,
                    "message": "Strategy description resulted in invalid rules. Please be more specific.",
                    "suggestion": "Try describing specific indicators (RSI, MACD, SMA) and clear entry/exit conditions."
                }
        except Exception as e:
            if retry:
                logger.warning(f"Groq call failed, retrying: {e}")
                return await self._call_groq_strategy_builder(description, symbol, retry=False)
            else:
                raise

# Global instance
backtest_explainer = BacktestExplainerAgent()

