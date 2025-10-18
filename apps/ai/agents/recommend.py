"""
Recommendation Agent - Generates trading recommendations
Integrates sentiment analysis + backtest validation + RAG insights
"""
from typing import Dict, Optional
import logging
from datetime import datetime

# Flexible imports
try:
    from ..utils.clients import get_openai_client
    from ..sentiment.aggregator import sentiment_aggregator
    from ..data.market_data import market_data_service
    from ..backtesting.templates import get_template
    from ..backtesting.builder import strategy_builder
    from ..backtesting.engine import BacktestEngine
    from ..utils.disclaimers import add_disclaimer_to_recommendation
    from ..utils.versioning import versioning
    from ..utils.cost_tracker import cost_tracker
except ImportError:
    from utils.clients import get_openai_client
    from sentiment.aggregator import sentiment_aggregator
    from data.market_data import market_data_service
    from backtesting.templates import get_template
    from backtesting.builder import strategy_builder
    from backtesting.engine import BacktestEngine
    from utils.disclaimers import add_disclaimer_to_recommendation
    from utils.versioning import versioning
    from utils.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)

class RecommendationAgent:
    """
    Generates trading recommendations with sentiment + backtest validation
    
    Process:
    1. Get sentiment analysis
    2. Run quick backtest validation
    3. Calculate risk parameters (simple 2% position sizing)
    4. Generate recommendation with GPT-4o-mini
    5. Add disclaimers and versioning
    """
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = "gpt-4o-mini"  # Fast and cost-effective
        logger.info("Initialized Recommendation Agent")
    
    async def generate_recommendation(
        self,
        symbol: str,
        user_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate a trading recommendation
        
        Args:
            symbol: Stock ticker
            user_id: User ID
            user_context: Optional context (risk tolerance, portfolio, etc.)
        
        Returns:
            Complete recommendation with:
            - Sentiment score
            - Backtest validation
            - Entry/stop/target prices
            - Position sizing
            - AI reasoning
        """
        logger.info(f"Generating recommendation for {symbol} (user: {user_id})")
        
        try:
            # Step 1: Get sentiment
            sentiment = await sentiment_aggregator.get_sentiment(
                symbol=symbol,
                user_id=user_id
            )
            
            # Step 2: Get current price
            latest_price = await market_data_service.get_latest_price(symbol)
            
            # Step 3: Handle invalid symbol (price is None)
            if latest_price is None or latest_price == 0:
                logger.warning(f"Invalid price for {symbol}, cannot generate recommendation")
                raise ValueError(f"Unable to get price for {symbol}")
            
            # Step 4: Quick backtest validation
            backtest_result = await self._run_quick_backtest(symbol, user_id)
            
            # Step 5: Calculate risk parameters
            risk_params = self._calculate_risk_parameters(
                current_price=latest_price,
                sentiment_score=sentiment['overall_score'],
                user_context=user_context
            )
            
            # Step 5: Generate AI recommendation
            ai_recommendation = await self._generate_ai_recommendation(
                symbol=symbol,
                sentiment=sentiment,
                backtest=backtest_result,
                risk_params=risk_params,
                current_price=latest_price,
                user_id=user_id
            )
            
            # Step 6: Assemble complete recommendation
            recommendation = {
                'symbol': symbol,
                'action': ai_recommendation['action'],
                'entry_price': latest_price,
                'stop_loss': risk_params['stop_loss'],
                'take_profit': risk_params['take_profit'],
                'position_size_percent': risk_params['position_size_percent'],
                'position_size_shares': risk_params['position_size_shares'],
                'sentiment': {
                    'score': sentiment['overall_score'],
                    'direction': sentiment['direction'],
                    'confidence': sentiment['confidence'],
                    'trending': sentiment['trending']
                },
                'backtest_validation': {
                    'win_rate': backtest_result.get('win_rate', 0),
                    'total_return_pct': backtest_result.get('total_return_pct', 0),
                    'sharpe_ratio': backtest_result.get('sharpe_ratio', 0),
                    'sample_size': backtest_result.get('num_trades', 0)
                },
                'reasoning': ai_recommendation['reasoning'],
                'created_at': datetime.now().isoformat()
            }
            
            # Step 7: Add versioning
            prompt_template = f"Generate recommendation for {symbol} with sentiment {sentiment['overall_score']}"
            recommendation = versioning.add_version_info(
                recommendation,
                agent_name='recommendation',
                prompt_template=prompt_template
            )
            
            # Step 8: Add disclaimer
            recommendation = add_disclaimer_to_recommendation(recommendation)
            
            logger.info(
                f"Recommendation generated for {symbol}: {recommendation['action']} "
                f"(sentiment: {sentiment['overall_score']:.2f}, win_rate: {backtest_result.get('win_rate', 0):.2%})"
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}", exc_info=True)
            raise
    
    async def _run_quick_backtest(self, symbol: str, user_id: str) -> Dict:
        """
        Run a quick backtest for validation
        
        Uses RSI oversold strategy (simple and reliable)
        """
        try:
            # Get template strategy
            strategy_def = get_template('rsi_oversold')
            
            if not strategy_def:
                logger.warning("RSI oversold template not found, skipping backtest")
                return self._default_backtest_result()
            
            # Build strategy function  
            strategy_func = strategy_builder.build_strategy(strategy_def)
            
            # Run backtest
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            engine = BacktestEngine()
            results = await engine.run_backtest(
                symbol=symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                strategy_fn=strategy_func,
                initial_capital=100000
            )
            
            # BacktestEngine returns metrics directly
            return {
                'win_rate': results.get('win_rate', 0),
                'total_return_pct': results.get('total_return_pct', 0),
                'sharpe_ratio': results.get('sharpe_ratio', 0),
                'num_trades': results.get('num_trades', 0)
            }
            
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return self._default_backtest_result()
    
    def _default_backtest_result(self) -> Dict:
        """Return default backtest result when unavailable"""
        return {
            'win_rate': 0.0,
            'total_return_pct': 0.0,
            'sharpe_ratio': 0.0,
            'num_trades': 0
        }
    
    def _calculate_risk_parameters(
        self,
        current_price: float,
        sentiment_score: float,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate risk parameters (simple MVP version)
        
        Rules:
        - Position size: 2.5% of capital (conservative)
        - Stop loss: 5% below entry
        - Take profit: 10% above entry (2:1 reward:risk)
        
        Future: Use MCP risk tools for advanced calculations
        """
        # Simple fixed percentages for MVP
        position_size_percent = 0.025  # 2.5% of capital
        stop_loss_percent = 0.05  # 5% stop loss
        take_profit_percent = 0.10  # 10% take profit
        
        # Adjust based on sentiment (simple version)
        if sentiment_score > 0.75:
            # Very bullish: slightly larger position
            position_size_percent = 0.03
        elif sentiment_score < 0.35:
            # Bearish: smaller position or skip
            position_size_percent = 0.01
        
        # Calculate prices
        stop_loss = current_price * (1 - stop_loss_percent)
        take_profit = current_price * (1 + take_profit_percent)
        
        # Calculate shares (assume $100k portfolio for MVP)
        portfolio_value = 100000
        position_value = portfolio_value * position_size_percent
        position_size_shares = int(position_value / current_price)
        
        return {
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'position_size_percent': position_size_percent,
            'position_size_shares': max(1, position_size_shares)  # At least 1 share
        }
    
    async def _generate_ai_recommendation(
        self,
        symbol: str,
        sentiment: Dict,
        backtest: Dict,
        risk_params: Dict,
        current_price: float,
        user_id: str
    ) -> Dict:
        """
        Generate AI-powered recommendation text
        
        Uses GPT-4o-mini with structured prompt
        """
        system_prompt = """You are a professional trading advisor. Generate clear, actionable trading recommendations.

Format:
- Start with clear action: BUY, SELL, or HOLD
- Provide 2-3 bullet points of reasoning
- Reference sentiment and backtest data
- Keep it concise (under 100 words)

Be professional but conversational."""
        
        user_prompt = f"""Generate a recommendation for {symbol}:

Current Price: ${current_price:.2f}

Sentiment Analysis:
- Overall Score: {sentiment['overall_score']:.2f} ({sentiment['direction']})
- Confidence: {sentiment['confidence']:.2f}
- Trending: {sentiment['trending']}
- News: {sentiment['sentiment_breakdown']['news']:.2f}
- Social: {sentiment['sentiment_breakdown']['reddit']:.2f}

Backtest Validation (RSI Oversold Strategy, 1 year):
- Win Rate: {backtest['win_rate']:.1%}
- Total Return: {backtest['total_return_pct']:.1%}
- Sharpe Ratio: {backtest['sharpe_ratio']:.2f}
- Sample Size: {backtest['num_trades']} trades

Risk Parameters:
- Stop Loss: ${risk_params['stop_loss']:.2f}
- Take Profit: ${risk_params['take_profit']:.2f}
- Position Size: {risk_params['position_size_percent']:.1%} of capital

Provide your recommendation:"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.3  # Lower temperature for consistency
            )
            
            reasoning = response.choices[0].message.content
            
            # Track cost
            await cost_tracker.log_cost(
                user_id=user_id,
                service="openai-recommendation",
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens
            )
            
            # Extract action from reasoning (simple heuristic)
            reasoning_lower = reasoning.lower()
            if 'buy' in reasoning_lower and 'not' not in reasoning_lower:
                action = 'BUY'
            elif 'sell' in reasoning_lower:
                action = 'SELL'
            else:
                action = 'HOLD'
            
            return {
                'action': action,
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.error(f"Error generating AI recommendation: {e}")
            # Fallback to simple logic
            if sentiment['overall_score'] > 0.65 and backtest['win_rate'] > 0.55:
                return {
                    'action': 'BUY',
                    'reasoning': f"Positive sentiment ({sentiment['overall_score']:.2f}) and strong backtest performance ({backtest['win_rate']:.1%} win rate)."
                }
            else:
                return {
                    'action': 'HOLD',
                    'reasoning': "Insufficient conviction for a trade at this time."
                }

# Global instance
recommendation_agent = RecommendationAgent()
