"""
Chat Orchestrator Agent - Unified chat interface for all trading functions
Uses OpenAI GPT-4 to understand intent and route to appropriate agents
"""
import json
import logging
import asyncio
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from openai import OpenAI

# Flexible imports
try:
    from ..utils.clients import get_groq_client
    from ..agents.recommend import recommendation_agent
    from ..agents.explainer import ExplainerAgent
    from ..sentiment.aggregator import sentiment_aggregator
    from ..backtesting.engine import BacktestEngine
    from ..backtesting.builder import strategy_builder
    from ..agents.strategy_translator import strategy_translator
    from ..agents.backtest_explainer import backtest_explainer
except ImportError:
    from utils.clients import get_groq_client
    from agents.recommend import recommendation_agent
    from agents.explainer import ExplainerAgent
    from sentiment.aggregator import sentiment_aggregator
    from backtesting.engine import BacktestEngine
    from backtesting.builder import strategy_builder
    from agents.strategy_translator import strategy_translator
    from agents.backtest_explainer import backtest_explainer

logger = logging.getLogger(__name__)

CHAT_ORCHESTRATOR_SYSTEM_PROMPT = """You are an intelligent trading assistant orchestrator. Your job is to analyze user messages and determine:

1. **Intent Classification** - What does the user want?
   - BACKTEST: User wants to test a trading strategy on historical data
   - RECOMMEND: User wants trading recommendations or advice on whether to buy/sell
   - RESEARCH: User wants market research, news, or sentiment analysis
   - EXPLAIN: User wants to learn about trading concepts
   - PORTFOLIO: User wants to see their portfolio or positions
   - GENERAL: General conversation or unclear intent

2. **Entity Extraction** - Extract relevant information:
   - Stock symbols (handle variations: AAPL, Apple, multiple tickers)
   - Strategy descriptions (for backtests)
   - Topics (for explanations)

3. **Parameters** - Extract specific parameters if mentioned:
   - Time periods (convert to days, default: 730 days = 2 years)
   - Any other relevant details

**Intent Detection Rules:**
- BACKTEST: Keywords like "backtest", "test strategy", "apply strategy", "run strategy", mentions of trading strategies (mean reversion, RSI, moving average, etc.)
- RECOMMEND: Keywords like "should I buy", "should I sell", "recommend", "trade idea", "what do you think about"
- RESEARCH: Keywords like "what's happening", "news about", "sentiment", "market analysis"
- EXPLAIN: Keywords like "what is", "how does", "explain", "teach me", "learn about"
- PORTFOLIO: Keywords like "my portfolio", "my positions", "my holdings", "show my"

**Symbol Extraction:**
- Look for stock tickers (1-5 letters, case-insensitive: aapl = AAPL, tsla = TSLA)
- Convert company names to symbols (Apple → AAPL, Tesla → TSLA, Microsoft → MSFT, Nvidia → NVDA, etc.)
- Handle multiple symbols separated by commas, "and", "or"
- Always return symbols in uppercase format

**Strategy Extraction (for BACKTEST):**
- Extract the full strategy description in natural language
- Examples: "mean reversion strategy", "RSI oversold", "buy when price crosses above 50-day moving average"

Return ONLY valid JSON in this exact format:
{
  "intent": "BACKTEST|RECOMMEND|RESEARCH|EXPLAIN|PORTFOLIO|GENERAL",
  "symbols": ["AAPL", "TSLA"],
  "strategy_description": "mean reversion strategy using RSI",
  "topic": "RSI indicator",
  "confidence": 0.95,
  "reasoning": "User explicitly mentioned backtesting a strategy"
}

**Examples:**

User: "backtest mean reversion on AAPL"
{
  "intent": "BACKTEST",
  "symbols": ["AAPL"],
  "strategy_description": "mean reversion",
  "topic": null,
  "confidence": 0.98,
  "reasoning": "Explicit backtest request with strategy and symbol"
}

User: "backtest mean reversion on aapl"
{
  "intent": "BACKTEST",
  "symbols": ["AAPL"],
  "strategy_description": "mean reversion",
  "topic": null,
  "confidence": 0.98,
  "reasoning": "Explicit backtest request with strategy and symbol (case-insensitive)"
}

User: "apply RSI oversold strategy to Apple, Tesla, and Nvidia"
{
  "intent": "BACKTEST",
  "symbols": ["AAPL", "TSLA", "NVDA"],
  "strategy_description": "RSI oversold strategy",
  "topic": null,
  "confidence": 0.97,
  "reasoning": "Multiple symbols with strategy mention"
}

User: "should I buy Microsoft?"
{
  "intent": "RECOMMEND",
  "symbols": ["MSFT"],
  "strategy_description": null,
  "topic": null,
  "confidence": 0.95,
  "reasoning": "Asking for trading advice"
}

User: "what's the sentiment on tech stocks?"
{
  "intent": "RESEARCH",
  "symbols": ["TECH"],
  "strategy_description": null,
  "topic": null,
  "confidence": 0.90,
  "reasoning": "Requesting sentiment analysis"
}

User: "what is RSI?"
{
  "intent": "EXPLAIN",
  "symbols": [],
  "strategy_description": null,
  "topic": "RSI",
  "confidence": 0.98,
  "reasoning": "Educational question"
}
"""

class ChatOrchestratorAgent:
    """
    Unified chat orchestrator that intelligently routes user messages
    to appropriate trading functions
    """
    
    def __init__(self):
        self.name = "chat_orchestrator"
        self.client = get_groq_client()
        self.model = "llama-3.3-70b-versatile"  # Fast and cost-effective
        self.backtest_engine = BacktestEngine()
        self.explainer = ExplainerAgent()
        logger.info("Initialized Chat Orchestrator Agent")
    
    async def handle_message(
        self,
        message: str,
        user_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for chat messages
        
        Args:
            message: User's message
            user_id: User ID
            user_context: Optional user context (portfolio, preferences, etc.)
        
        Returns:
            {
                'short_response': str,  # Spoken response
                'detailed_response': str,  # Full text response
                'metadata': {...},  # Additional data (charts, etc.)
                'intent': str
            }
        """
        logger.info(f"Processing message: '{message[:100]}...'")
        
        try:
            # Step 1: Analyze message with GPT-4
            analysis = await self._analyze_message(message)
            
            intent = analysis.get('intent', 'GENERAL')
            symbols = analysis.get('symbols', [])
            strategy_desc = analysis.get('strategy_description')
            topic = analysis.get('topic')
            confidence = analysis.get('confidence', 0)
            reasoning = analysis.get('reasoning', 'No reasoning provided')
            
            logger.info(f"Message Analysis - Intent: {intent}, Symbols: {symbols}, Strategy: {strategy_desc}, Confidence: {confidence}")
            logger.info(f"Reasoning: {reasoning}")
            
            # Step 2: Route to appropriate handler
            if intent == "BACKTEST":
                return await self._handle_backtest(symbols, strategy_desc, user_id)
            
            elif intent == "RECOMMEND":
                return await self._handle_recommend(symbols, user_id, user_context)
            
            elif intent == "RESEARCH":
                return await self._handle_research(symbols, user_id)
            
            elif intent == "EXPLAIN":
                return await self._handle_explain(topic, user_id)
            
            elif intent == "PORTFOLIO":
                return await self._handle_portfolio(user_id, user_context)
            
            else:
                return await self._handle_general(message, user_id)
        
        except Exception as e:
            logger.error(f"Chat orchestrator error: {e}", exc_info=True)
            return {
                'short_response': f"Sorry partner, I hit a snag processin' that request: {str(e)}",
                'detailed_response': f"Error: {str(e)}\n\nPlease try rephrasing your question or contact support if this persists.",
                'metadata': {},
                'intent': 'ERROR'
            }
    
    async def _analyze_message(self, message: str) -> Dict:
        """Use GPT-4 to analyze user message and extract intent/entities"""
        try:
            # Using Groq client (OpenAI-compatible)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CHAT_ORCHESTRATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            analysis = json.loads(content)
            
            logger.info(f"Message analysis: {analysis}")
            return analysis
        
        except Exception as e:
            logger.error(f"Message analysis failed: {e}", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}, Details: {str(e)}")
            # Fallback to simple keyword matching
            return self._fallback_analysis(message)
    
    def _convert_markdown_to_html(self, text: str) -> str:
        """Convert any markdown syntax to HTML using regex"""
        if not text:
            return text
            
        # Convert headers ### -> <h3>, ## -> <h2>, # -> <h1>
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Convert bold **text** -> <b>text</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        
        # Convert italic *text* -> <i>text</i>
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        
        # Convert bullet points • -> <li>
        text = re.sub(r'^• (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        
        # Wrap consecutive <li> elements in <ul>
        text = re.sub(r'(<li>.*?</li>(?:\s*<li>.*?</li>)*)', r'<ul>\1</ul>', text, flags=re.DOTALL)
        
        # Convert line breaks \n\n -> <br><br>
        text = re.sub(r'\n\n', '<br><br>', text)
        
        # Convert single line breaks \n -> <br> (but not after headers or lists)
        text = re.sub(r'\n(?!</h[1-3]>|</ul>|</li>)', '<br>', text)
        
        return text
    
    def _fallback_analysis(self, message: str) -> Dict:
        """Simple keyword-based fallback if GPT-4 fails"""
        message_lower = message.lower()
        
        # Detect intent
        if any(word in message_lower for word in ["backtest", "test strategy", "apply strategy", "run strategy"]):
            intent = "BACKTEST"
        elif any(word in message_lower for word in ["should i buy", "should i sell", "recommend", "trade idea"]):
            intent = "RECOMMEND"
        elif any(word in message_lower for word in ["what's happening", "sentiment", "news about", "research"]):
            intent = "RESEARCH"
        elif any(word in message_lower for word in ["what is", "how does", "explain", "teach me"]):
            intent = "EXPLAIN"
        elif any(word in message_lower for word in ["portfolio", "positions", "holdings"]):
            intent = "PORTFOLIO"
        else:
            intent = "GENERAL"
        
        # Extract symbols (case-insensitive regex and normalize to uppercase)
        import re
        symbols = re.findall(r'\b[A-Za-z]{1,5}\b', message)
        symbols = [s.upper() for s in symbols if s.upper() in [
            # Common stock symbols
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM',
            'AMD', 'INTC', 'ORCL', 'CSCO', 'IBM', 'UBER', 'LYFT', 'SNAP', 'TWTR', 'SQ',
            'PYPL', 'V', 'MA', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'XOM', 'CVX', 'KO',
            'PEP', 'WMT', 'HD', 'PG', 'JNJ', 'UNH', 'VZ', 'T', 'DIS', 'NKE', 'MCD', 'BA',
            # Add more as needed
        ]]
        
        # Extract strategy description for backtest
        strategy_description = None
        if intent == "BACKTEST":
            strategy_keywords = ["mean reversion", "rsi", "moving average", "momentum", "trend", "support", "resistance"]
            for keyword in strategy_keywords:
                if keyword in message_lower:
                    strategy_description = keyword
                    break
            if not strategy_description:
                # Try to extract the strategy from context
                words = message_lower.split()
                if "mean" in words and "reversion" in words:
                    strategy_description = "mean reversion"
                elif "rsi" in words:
                    strategy_description = "RSI strategy"
                elif "moving" in words and "average" in words:
                    strategy_description = "moving average strategy"
        
        # Extract topic for explain intent
        topic = None
        if intent == "EXPLAIN":
            # Common trading terms to recognize
            trading_terms = [
                "rsi", "macd", "bollinger bands", "moving average", "vwap", "support", "resistance",
                "candlestick patterns", "volume", "volatility", "sharpe ratio", "mean reversion", 
                "momentum", "trend following", "backtesting", "pivot points", "fibonacci", "stochastic",
                "williams %r", "cci", "atr", "adx", "parabolic sar", "ichimoku", "keltner channels"
            ]
            
            # Pattern 1: "what is X" or "what's X"
            import re
            what_pattern = r'what\s+(?:is|s)\s+(.+?)(?:\?|$)'
            match = re.search(what_pattern, message_lower)
            if match:
                potential_topic = match.group(1).strip()
                # Check if it's a known trading term
                for term in trading_terms:
                    if term in potential_topic or potential_topic in term:
                        topic = term
                        break
                if not topic:
                    topic = potential_topic
            
            # Pattern 2: "explain X" or "tell me about X"
            if not topic:
                explain_pattern = r'(?:explain|tell me about|teach me about)\s+(.+?)(?:\?|$)'
                match = re.search(explain_pattern, message_lower)
                if match:
                    potential_topic = match.group(1).strip()
                    for term in trading_terms:
                        if term in potential_topic or potential_topic in term:
                            topic = term
                            break
                    if not topic:
                        topic = potential_topic
            
            # Pattern 3: "how does X work"
            if not topic:
                how_pattern = r'how does\s+(.+?)\s+work'
                match = re.search(how_pattern, message_lower)
                if match:
                    potential_topic = match.group(1).strip()
                    for term in trading_terms:
                        if term in potential_topic or potential_topic in term:
                            topic = term
                            break
                    if not topic:
                        topic = potential_topic
            
            # Fallback: check if any trading term is mentioned in the message
            if not topic:
                for term in trading_terms:
                    if term in message_lower:
                        topic = term
                        break
        
        return {
            'intent': intent,
            'symbols': symbols,
            'strategy_description': strategy_description,
            'topic': topic,
            'confidence': 0.6,  # Higher confidence since we're being more specific
            'reasoning': 'Fallback analysis with improved symbol, strategy, and topic extraction'
        }
    
    async def _handle_backtest(
        self,
        symbols: List[str],
        strategy_description: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle backtest requests
        - Translate strategy to JSON
        - Run backtest for each symbol (parallel)
        - Generate conversational narrative + PNG charts
        """
        if not symbols:
            return {
                'short_response': "Hold on there, partner! I need a stock symbol to backtest.",
                'detailed_response': "Please specify which stock(s) you'd like to test the strategy on. For example: 'backtest mean reversion on AAPL'",
                'metadata': {},
                'intent': 'BACKTEST'
            }
        
        if not strategy_description:
            return {
                'short_response': "I need more details about the strategy you want to test.",
                'detailed_response': "Please describe the trading strategy you'd like to backtest. For example: 'mean reversion', 'RSI oversold', or 'buy when price crosses above 50-day moving average'",
                'metadata': {},
                'intent': 'BACKTEST'
            }
        
        try:
            # Set default time period (2 years) and capital ($100k)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)
            initial_capital = 100000.0
            
            logger.info(f"Backtesting {len(symbols)} symbol(s): {symbols}")
            
            # Translate strategy once (same strategy for all symbols)
            logger.info(f"Translating strategy: '{strategy_description}'")
            strategy_def = await strategy_translator.translate_strategy(
                natural_language=strategy_description,
                symbol=symbols[0]  # Use first symbol as reference
            )
            
            # ADD: Log the generated strategy for debugging
            logger.info(f"Generated strategy JSON: {json.dumps(strategy_def, indent=2)}")
            logger.info(f"Strategy name: {strategy_def.get('name')}")
            logger.info(f"Entry rules: {strategy_def.get('entry_rules')}")
            logger.info(f"Exit rules: {strategy_def.get('exit_rules')}")
            
            # Build strategy function
            strategy_func = await strategy_builder.build_strategy(strategy_def)
            
            # Run backtests in parallel for all symbols
            backtest_tasks = [
                self.backtest_engine.run_backtest(
                    symbol=symbol,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    strategy_fn=strategy_func,
                    initial_capital=initial_capital,
                    include_visuals=True
                )
                for symbol in symbols
            ]
            
            results = await asyncio.gather(*backtest_tasks, return_exceptions=True)
            
            # Filter out errors
            successful_results = []
            failed_symbols = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Backtest failed for {symbols[i]}: {result}")
                    failed_symbols.append(symbols[i])
                else:
                    successful_results.append((symbols[i], result))
            
            if not successful_results:
                return {
                    'short_response': "Sorry partner, the backtest didn't work out.",
                    'detailed_response': f"I couldn't run the backtest for {', '.join(symbols)}. This might be due to insufficient historical data or invalid symbols.",
                    'metadata': {},
                    'intent': 'BACKTEST'
                }
            
            # Generate conversational narrative for each result
            narratives = []
            all_chart_data = []
            
            for symbol, backtest_result in successful_results:
                # Generate narrative explanation
                narrative = await backtest_explainer.explain(
                    backtest_result=backtest_result,
                    strategy_name=strategy_def['name'],
                    symbol=symbol,
                    conversational=True  # New parameter we'll add
                )
                
                # Format narrative with TL;DR
                formatted_narrative = self._format_backtest_narrative(
                    symbol, backtest_result, narrative
                )
                narratives.append(formatted_narrative)
                
                # Collect chart data
                if 'visuals' in backtest_result and 'equity_curve' in backtest_result['visuals']:
                    all_chart_data.append({
                        'symbol': symbol,
                        'equity_curve': backtest_result['visuals']['equity_curve'],
                        'backtest_result': backtest_result  # Include full backtest result for metrics
                    })
            
            # Combine narratives
            if len(successful_results) == 1:
                detailed_response = self._convert_markdown_to_html(narratives[0])
                short_response = f"I've backtested that {strategy_def['name']} strategy on {symbols[0]}. Check out the charts and results below!"
            else:
                detailed_response = self._convert_markdown_to_html("\n\n---\n\n".join(narratives))
                short_response = f"I've backtested that {strategy_def['name']} strategy on {len(successful_results)} stocks. Charts and results below!"
                
            if failed_symbols:
                short_response += f" (Note: {', '.join(failed_symbols)} failed)"
            
            return {
                'short_response': short_response,
                'detailed_response': detailed_response,
                'metadata': {
                    'chart_data': all_chart_data,
                    'strategy_name': strategy_def['name'],
                    'time_period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    'symbols': [s for s, _ in successful_results],
                    'failed_symbols': failed_symbols
                },
                'intent': 'BACKTEST'
            }
        
        except Exception as e:
            logger.error(f"Backtest handler error: {e}", exc_info=True)
            return {
                'short_response': f"Hit a snag runnin' that backtest, partner: {str(e)}",
                'detailed_response': f"Error running backtest: {str(e)}\n\nPlease try rephrasing your strategy or using a different symbol.",
                'metadata': {},
                'intent': 'BACKTEST'
            }
    
    def _format_backtest_narrative(
        self, symbol: str, backtest_result: Dict, narrative: str
    ) -> str:
        """Format backtest results as conversational narrative with TL;DR"""
        
        # Extract key metrics
        total_return_pct = backtest_result.get('total_return_pct', 0) * 100
        win_rate = backtest_result.get('win_rate', 0) * 100
        sharpe = backtest_result.get('sharpe_ratio', 0)
        max_dd = abs(backtest_result.get('max_drawdown', 0)) * 100
        num_trades = backtest_result.get('num_trades', 0)
        profit_factor = backtest_result.get('profit_factor', 0)
        
        # Create TL;DR section
        tldr = f"""
<h3>TL;DR for {symbol}</h3>
• Total Return: {total_return_pct:+.1f}%
• Win Rate: {win_rate:.0f}%
• Sharpe Ratio: {sharpe:.2f} {"(excellent)" if sharpe > 2 else "(good)" if sharpe > 1 else "(needs work)" if sharpe > 0 else "(poor)"}
• Max Drawdown: -{max_dd:.1f}%
• Trade Count: {num_trades} trades
• Profit Factor: {profit_factor:.2f}
• Verdict: {"Strong performer" if total_return_pct > 15 and win_rate > 55 else "Solid strategy" if total_return_pct > 0 and win_rate > 50 else "Needs optimization"}
"""
        
        # Combine narrative with TL;DR
        return f"<h2>{symbol}</h2>\n\n{narrative}\n\n{tldr}"
    
    async def _handle_recommend(
        self,
        symbols: List[str],
        user_id: str,
        user_context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Handle recommendation requests"""
        if not symbols:
            return {
                'short_response': "Which stock are you interested in, partner?",
                'detailed_response': "Please specify a stock symbol for me to analyze. For example: 'should I buy AAPL?'",
                'metadata': {},
                'intent': 'RECOMMEND'
            }
        
        try:
            # Get recommendations for all symbols (parallel)
            recommendation_tasks = [
                recommendation_agent.generate_recommendation(
                    symbol=symbol,
                    user_id=user_id,
                    user_context=user_context
                )
                for symbol in symbols
            ]
            
            recommendations = await asyncio.gather(*recommendation_tasks, return_exceptions=True)
            
            # Format responses
            responses = []
            for i, rec in enumerate(recommendations):
                if isinstance(rec, Exception):
                    logger.error(f"Recommendation failed for {symbols[i]}: {rec}")
                    continue
                
                symbol = symbols[i]
                action = rec.get('action', 'HOLD')
                confidence = rec.get('confidence', 0) * 100
                reasoning = rec.get('reasoning', 'No reasoning provided')
                
                response = f"<b>{symbol}:</b> {action} (Confidence: {confidence:.0f}%)\n{reasoning}"
                responses.append(response)
            
            if not responses:
                return {
                    'short_response': "Sorry partner, I couldn't generate recommendations right now.",
                    'detailed_response': "There was an issue analyzing those stocks. Please try again.",
                    'metadata': {},
                    'intent': 'RECOMMEND'
                }
            
            detailed_response = self._convert_markdown_to_html("\n\n".join(responses))
            
            if len(symbols) == 1:
                short_response = f"Here's my take on {symbols[0]}..."
            else:
                short_response = f"Here are my recommendations for {len(symbols)} stocks..."
            
            return {
                'short_response': short_response,
                'detailed_response': detailed_response,
                'metadata': {'symbols': symbols},
                'intent': 'RECOMMEND'
            }
        
        except Exception as e:
            logger.error(f"Recommend handler error: {e}", exc_info=True)
            return {
                'short_response': f"Hit a snag with that recommendation: {str(e)}",
                'detailed_response': f"Error: {str(e)}",
                'metadata': {},
                'intent': 'RECOMMEND'
            }
    
    async def _handle_research(
        self,
        symbols: List[str],
        user_id: str
    ) -> Dict[str, Any]:
        """Handle research/sentiment requests"""
        if not symbols:
            return {
                'short_response': "What would you like me to research, partner?",
                'detailed_response': "Please specify a stock symbol or sector for market research.",
                'metadata': {},
                'intent': 'RESEARCH'
            }
        
        try:
            # Get sentiment for all symbols (parallel)
            sentiment_tasks = [
                sentiment_aggregator.get_sentiment(symbol=symbol, user_id=user_id)
                for symbol in symbols
            ]
            
            sentiments = await asyncio.gather(*sentiment_tasks, return_exceptions=True)
            
            # Format responses
            responses = []
            for i, sentiment in enumerate(sentiments):
                if isinstance(sentiment, Exception):
                    logger.error(f"Sentiment failed for {symbols[i]}: {sentiment}")
                    continue
                
                symbol = symbols[i]
                overall_score = sentiment.get('overall_score', 0)
                sentiment_label = "Bullish" if overall_score > 0.2 else "Bearish" if overall_score < -0.2 else "Neutral"
                
                news_count = sentiment.get('volume', {}).get('news_articles', 0)
                
                response = f"<b>{symbol}:</b> {sentiment_label} sentiment (Score: {overall_score:+.2f})\nBased on {news_count} news articles."
                responses.append(response)
            
            if not responses:
                return {
                    'short_response': "Sorry partner, I couldn't fetch sentiment data right now.",
                    'detailed_response': "There was an issue analyzing market sentiment. Please try again.",
                    'metadata': {},
                    'intent': 'RESEARCH'
                }
            
            detailed_response = self._convert_markdown_to_html("\n\n".join(responses))
            short_response = f"Here's the market sentiment analysis..."
            
            return {
                'short_response': short_response,
                'detailed_response': detailed_response,
                'metadata': {'symbols': symbols},
                'intent': 'RESEARCH'
            }
        
        except Exception as e:
            logger.error(f"Research handler error: {e}", exc_info=True)
            return {
                'short_response': f"Hit a snag with that research: {str(e)}",
                'detailed_response': f"Error: {str(e)}",
                'metadata': {},
                'intent': 'RESEARCH'
            }
    
    async def _handle_explain(
        self,
        topic: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle explanation requests"""
        if not topic:
            return {
                'short_response': "What would you like me to explain, partner?",
                'detailed_response': "Ask me about any trading concept, indicator, or strategy!",
                'metadata': {},
                'intent': 'EXPLAIN'
            }
        
        try:
            explanation = await self.explainer.explain(
                topic=topic,
                user_id=user_id
            )
            
            return {
                'short_response': f"Let me explain {topic}...",
                'detailed_response': self._convert_markdown_to_html(explanation.get('explanation', 'Explanation not available')),
                'metadata': {'topic': topic},
                'intent': 'EXPLAIN'
            }
        
        except Exception as e:
            logger.error(f"Explain handler error: {e}", exc_info=True)
            return {
                'short_response': f"I'm not quite sure about {topic}, partner.",
                'detailed_response': f"Error: {str(e)}",
                'metadata': {},
                'intent': 'EXPLAIN'
            }
    
    async def _handle_portfolio(
        self,
        user_id: str,
        user_context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Handle portfolio requests"""
        # TODO: Integrate with portfolio manager
        return {
            'short_response': "Portfolio tracking is comin' soon, partner!",
            'detailed_response': "The portfolio feature is currently under development. Stay tuned!",
            'metadata': {},
            'intent': 'PORTFOLIO'
        }
    
    async def _handle_general(
        self,
        message: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle general conversation"""
        return {
            'short_response': "Howdy! I'm here to help with trading, backtesting, and market analysis.",
            'detailed_response': "I can help you with:\n• Backtesting trading strategies\n• Stock recommendations\n• Market sentiment analysis\n• Trading education\n• Portfolio tracking\n\nWhat would you like to explore?",
            'metadata': {},
            'intent': 'GENERAL'
        }

# Global instance
chat_orchestrator = ChatOrchestratorAgent()

