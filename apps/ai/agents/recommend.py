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
    from ..memory.mem0_service import mem0_service
    from ..utils.mcp_client import mcp_risk_client
    from ..utils.config import settings
    from ..data.indicators import calculate_atr
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
    from memory.mem0_service import mem0_service
    from utils.mcp_client import mcp_risk_client
    from utils.config import settings
    from data.indicators import calculate_atr

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
        self.mem0_enabled = settings.use_mem0
        self.mcp_enabled = settings.use_mcp_risk_tools
        
        logger.info(
            f"Initialized Recommendation Agent "
            f"(Mem0: {self.mem0_enabled}, MCP: {self.mcp_enabled})"
        )
    
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
            
            # Step 4: Get user policy from Mem0
            user_policy = await mem0_service.get_policy(user_id)
            logger.info(f"User policy: {user_policy['risk_tolerance']} trader, {user_policy['default_position_size_pct']:.1%} position size")
            
            # Step 5: Quick backtest validation
            backtest_result = await self._run_quick_backtest(symbol, user_id)
            
            # Step 6: Calculate risk parameters (with Mem0 + MCP)
            risk_params = await self._calculate_risk_parameters_advanced(
                symbol=symbol,
                current_price=latest_price,
                sentiment_score=sentiment['overall_score'],
                user_policy=user_policy,
                backtest_result=backtest_result,
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
            strategy_func = await strategy_builder.build_strategy(strategy_def)
            
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
    
    async def _calculate_risk_parameters_advanced(
        self,
        symbol: str,
        current_price: float,
        sentiment_score: float,
        user_policy: Dict,
        backtest_result: Dict,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate risk parameters using Mem0 + MCP
        
        With Mem0: Uses user's personalized risk tolerance
        With MCP: Uses Kelly Criterion / ATR-based stops
        Without: Falls back to simple fixed percentages
        
        Args:
            symbol: Stock symbol
            current_price: Current price
            sentiment_score: Sentiment score 0-1
            user_policy: User policy from Mem0
            backtest_result: Backtest metrics
            user_context: Optional additional context
        
        Returns:
            {stop_loss, take_profit, position_size_percent, position_size_shares, method}
        """
        # Start with user policy from Mem0
        position_size_percent = user_policy.get('default_position_size_pct', 0.025)
        stop_loss_percent = user_policy.get('default_stop_loss_pct', 0.05)
        take_profit_percent = user_policy.get('default_take_profit_pct', 0.10)
        risk_tolerance = user_policy.get('risk_tolerance', 'moderate')
        
        logger.info(f"Using Mem0 policy: {risk_tolerance}, {position_size_percent:.1%} position")
        
        # If MCP available, use advanced calculations
        if self.mcp_enabled and mcp_risk_client.enabled:
            logger.info("Using MCP Risk Tools for advanced calculations")
            
            try:
                # Get ATR for stop optimization
                historical_data = await market_data_service.get_ohlcv(symbol, period="1mo", interval="1d")
                
                if not historical_data.empty:
                    # Normalize columns
                    historical_data.columns = historical_data.columns.str.lower()
                    atr_values = calculate_atr(
                        historical_data['high'],
                        historical_data['low'],
                        historical_data['close'],
                        period=14
                    )
                    current_atr = atr_values.iloc[-1] if not atr_values.empty else current_price * 0.02
                else:
                    current_atr = current_price * 0.02  # Fallback: 2% of price
                
                # Use MCP to optimize stop loss
                stop_result = await mcp_risk_client.optimize_stop_loss(
                    entry_price=current_price,
                    atr=current_atr,
                    risk_tolerance=risk_tolerance,
                    direction='BUY'
                )
                
                if stop_result:
                    stop_loss = stop_result['stop_loss']
                    logger.info(f"MCP optimized stop: ${stop_loss:.2f} ({stop_result['atr_multiplier']}x ATR)")
                else:
                    # Fallback to percentage
                    stop_loss = current_price * (1 - stop_loss_percent)
                
                # Calculate take profit
                take_profit = current_price * (1 + take_profit_percent)
                
                # Use MCP for position sizing (Kelly Criterion if we have backtest data)
                if backtest_result.get('num_trades', 0) > 10:  # Need enough sample size
                    win_rate = backtest_result.get('win_rate', 0.5)
                    avg_win = backtest_result.get('avg_win', 0.08)
                    avg_loss = abs(backtest_result.get('avg_loss', -0.04))
                    
                    portfolio_value = user_context.get('portfolio_value', 100000) if user_context else 100000
                    
                    position_result = await mcp_risk_client.calculate_position_size(
                        method='kelly',
                        capital=portfolio_value,
                        current_price=current_price,
                        win_rate=win_rate,
                        avg_win=avg_win,
                        avg_loss=avg_loss,
                        stop_loss=stop_loss
                    )
                    
                    if position_result:
                        position_size_shares = position_result['shares']
                        position_size_percent = position_result['position_value'] / portfolio_value
                        logger.info(f"MCP Kelly sizing: {position_size_shares} shares ({position_size_percent:.1%})")
                    else:
                        # Fallback
                        portfolio_value = 100000
                        position_value = portfolio_value * position_size_percent
                        position_size_shares = int(position_value / current_price)
                else:
                    # Not enough backtest data for Kelly, use fixed percent
                    portfolio_value = 100000
                    position_value = portfolio_value * position_size_percent
                    position_size_shares = int(position_value / current_price)
                
                # Calculate risk/reward
                risk_reward_result = await mcp_risk_client.calculate_risk_reward(
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    win_rate=backtest_result.get('win_rate', 0.5),
                    position_size=position_size_shares
                )
                
                if risk_reward_result:
                    logger.info(
                        f"MCP Risk/Reward: {risk_reward_result['risk_reward_ratio']:.2f}, "
                        f"Expected Value: ${risk_reward_result['expected_value']:.2f}"
                    )
                
            except Exception as e:
                logger.error(f"MCP calculations failed, using simple fallback: {e}")
                # Fallback to simple calculations
                stop_loss = current_price * (1 - stop_loss_percent)
                take_profit = current_price * (1 + take_profit_percent)
                portfolio_value = 100000
                position_value = portfolio_value * position_size_percent
                position_size_shares = int(position_value / current_price)
        
        else:
            # Simple calculations without MCP
            logger.info("Using simple risk calculations (MCP disabled)")
            stop_loss = current_price * (1 - stop_loss_percent)
            take_profit = current_price * (1 + take_profit_percent)
            portfolio_value = 100000
            position_value = portfolio_value * position_size_percent
            position_size_shares = int(position_value / current_price)
        
        return {
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'position_size_percent': round(position_size_percent, 4),
            'position_size_shares': max(1, position_size_shares),
            'method': 'kelly_mcp' if self.mcp_enabled else 'fixed_percent_mem0'
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
- News Articles: {sentiment['volume']['news_articles']}

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
