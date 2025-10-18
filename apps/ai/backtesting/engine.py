"""
Backtesting engine for strategy validation
Tests recommendations against historical data
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
import logging

logger = logging.getLogger(__name__)

class Trade:
    """Represents a single trade"""
    def __init__(
        self,
        symbol: str,
        entry_price: float,
        entry_date: datetime,
        stop: float,
        target: float,
        direction: str = "BUY",
        shares: int = 1
    ):
        self.symbol = symbol
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.stop = stop
        self.target = target
        self.direction = direction
        self.shares = shares  # Number of shares in position
        
        self.exit_price: Optional[float] = None
        self.exit_date: Optional[datetime] = None
        self.pnl: Optional[float] = None  # Total P&L in dollars
        self.pnl_pct: Optional[float] = None  # Percentage return
        self.outcome: Optional[str] = None  # 'win', 'loss', 'breakeven'

class BacktestEngine:
    """Simple backtesting for trading strategies"""
    
    def __init__(self):
        """Initialize engine with optional explainer"""
        self.explainer = None
        # Try to import explainer but don't fail if unavailable
        try:
            from ..agents.backtest_explainer import backtest_explainer
            self.explainer = backtest_explainer
        except ImportError:
            try:
                from agents.backtest_explainer import backtest_explainer
                self.explainer = backtest_explainer
            except ImportError:
                logger.warning("BacktestExplainerAgent not available - explanations disabled")
    
    async def generate_explanation(
        self,
        strategy_name: str,
        strategy_description: str,
        metrics: Dict,
        symbol: str,
        period: str
    ) -> str:
        """
        Generate natural language explanation of backtest results
        
        Args:
            strategy_name: Name of the strategy
            strategy_description: Description of what strategy does
            metrics: Backtest metrics dict
            symbol: Stock symbol tested
            period: Time period tested
        
        Returns:
            Explanation text suitable for voice narration
        """
        if not self.explainer:
            logger.warning("Explainer not available, returning basic explanation")
            return self._generate_basic_explanation(strategy_name, metrics, symbol, period)
        
        try:
            explanation = await self.explainer.generate_explanation(
                strategy_name=strategy_name,
                strategy_description=strategy_description,
                metrics=metrics,
                symbol=symbol,
                period=period
            )
            return explanation
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return self._generate_basic_explanation(strategy_name, metrics, symbol, period)
    
    def _generate_basic_explanation(
        self,
        strategy_name: str,
        metrics: Dict,
        symbol: str,
        period: str
    ) -> str:
        """Generate simple template-based explanation"""
        win_rate = metrics.get('win_rate', 0) * 100
        total_return = metrics.get('total_return_pct', 0) * 100
        sharpe = metrics.get('sharpe_ratio', 0)
        max_dd = metrics.get('max_drawdown', 0) * 100
        num_trades = metrics.get('num_trades', 0)
        
        performance = "profitable" if total_return > 0 else "unprofitable"
        quality = "good" if sharpe > 1 else "moderate" if sharpe > 0.5 else "poor"
        
        return f"""The {strategy_name} strategy on {symbol} from {period} generated {num_trades} trades with a {win_rate:.0f}% win rate. Overall, it was {performance}, delivering a total return of {total_return:.1f}%. The Sharpe ratio of {sharpe:.2f} indicates {quality} risk-adjusted returns. The maximum drawdown was {abs(max_dd):.1f}%, meaning at worst, you would have seen your capital decline by that amount from peak. {'This strategy shows promise and may be worth considering with proper risk management.' if total_return > 0 and sharpe > 1 else 'This strategy may need refinement or may not be suitable for current market conditions.'} Remember, past performance does not guarantee future results."""
    
    async def run_backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy_fn: Callable,
        initial_capital: float = 100000.0,
        include_visuals: bool = True
    ) -> Dict:
        """
        Test a strategy on historical data
        
        Args:
            symbol: Ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strategy_fn: Function that generates signals
            initial_capital: Starting capital
        
        Returns:
            Performance metrics dict
        """
        logger.info(f"Backtesting {symbol} from {start_date} to {end_date}")
        
        try:
            # Import market data service
            try:
                from ..data.market_data import market_data_service
            except ImportError:
                from data.market_data import market_data_service
            
            # Fetch historical data
            data = await market_data_service.get_ohlcv(
                symbol=symbol,
                period="max"  # Get all available data
            )
            
            if data is None or data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Filter by date range
            data = data.loc[start_date:end_date]
            
            # ADD: Log data info
            logger.info(f"Backtesting {symbol}: {len(data)} days of data")
            
            # Run strategy
            trades = await self._simulate_trades(data, strategy_fn, initial_capital)
            
            # Calculate metrics
            metrics = self._calculate_metrics(trades, initial_capital, include_visuals)
            
            logger.info(
                f"Backtest complete: {metrics['num_trades']} trades, "
                f"{metrics['win_rate']*100:.1f}% win rate, "
                f"{metrics['total_return_pct']*100:.1f}% return"
            )
            
            return metrics
        
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            raise
    
    async def _simulate_trades(
        self,
        data: pd.DataFrame,
        strategy_fn: Callable,
        initial_capital: float
    ) -> List[Trade]:
        """Simulate trades based on strategy signals"""
        trades = []
        current_position = None
        capital = initial_capital
        
        # Start after indicator warmup (RSI needs 14 periods)
        # Always start after at least 20 days to ensure RSI and other indicators are valid
        start_index = 20
        
        if len(data) < start_index:
            logger.warning(f"Not enough data for backtest: {len(data)} days (need at least {start_index})")
            logger.info(f"Backtest complete: 0 trades generated (insufficient data)")
            return []
        
        logger.info(f"Starting simulation from index {start_index} of {len(data)} total days")
        
        for i in range(start_index, len(data)):
            current_date = data.index[i]
            current_price = data['Close'].iloc[i]
            
            # Get historical window for strategy
            window = data.iloc[:i+1]
            
            # Get signal from strategy
            signal = await strategy_fn(window)
            
            if signal and not current_position:
                # Calculate position size based on signal
                position_size_pct = signal.get('position_size_pct', 0.10)  # Default 10%
                position_value = capital * position_size_pct
                shares = int(position_value / current_price)
                shares = max(1, shares)  # At least 1 share
                
                # Open new position
                current_position = Trade(
                    symbol=data.index.name or 'UNKNOWN',
                    entry_price=current_price,
                    entry_date=current_date,
                    stop=signal.get('stop', current_price * 0.95),
                    target=signal.get('target', current_price * 1.10),
                    direction=signal.get('direction', 'BUY'),
                    shares=shares
                )
                logger.debug(f"Opened position: Entry=${current_price:.2f}, Stop=${current_position.stop:.2f}, Target=${current_position.target:.2f}")
            
            elif current_position:
                # Check for exit conditions
                high = data['High'].iloc[i]
                low = data['Low'].iloc[i]
                
                # Stop hit
                if current_position.direction == "BUY" and low <= current_position.stop:
                    current_position.exit_price = current_position.stop
                    current_position.exit_date = current_date
                    current_position.outcome = 'loss'
                    logger.debug(f"Stop loss hit: ${low:.2f} <= ${current_position.stop:.2f}")
                
                # Target hit
                elif current_position.direction == "BUY" and high >= current_position.target:
                    current_position.exit_price = current_position.target
                    current_position.exit_date = current_date
                    current_position.outcome = 'win'
                    logger.debug(f"Target hit: ${high:.2f} >= ${current_position.target:.2f}")
                
                # Calculate P&L if exited
                if current_position.exit_price:
                    # Per-share P&L
                    pnl_per_share = current_position.exit_price - current_position.entry_price
                    
                    # Total P&L (multiply by shares)
                    current_position.pnl = pnl_per_share * current_position.shares
                    
                    # Percentage return (same regardless of shares)
                    current_position.pnl_pct = pnl_per_share / current_position.entry_price
                    
                    # Update capital with P&L
                    capital += current_position.pnl
                    
                    logger.info(f"Trade closed: P&L=${current_position.pnl:.2f} ({current_position.pnl_pct:.2%})")
                    
                    trades.append(current_position)
                    current_position = None
        
        # Close any remaining open position at market close
        if current_position:
            logger.info(f"Closing open position at end of backtest")
            final_price = data['Close'].iloc[-1]
            current_position.exit_price = final_price
            current_position.exit_date = data.index[-1]
            current_position.outcome = 'win' if final_price > current_position.entry_price else 'loss'
            
            # Calculate P&L
            pnl_per_share = current_position.exit_price - current_position.entry_price
            current_position.pnl = pnl_per_share * current_position.shares
            current_position.pnl_pct = pnl_per_share / current_position.entry_price
            
            logger.info(f"Trade closed at market: P&L=${current_position.pnl:.2f} ({current_position.pnl_pct:.2%})")
            trades.append(current_position)
        
        # ADD: Log simulation results
        logger.info(f"Backtest complete: {len(trades)} trades generated")
        
        return trades
    
    def _calculate_metrics(self, trades: List[Trade], initial_capital: float, include_visuals: bool = True) -> Dict:
        """Calculate performance metrics"""
        if not trades:
            metrics = {
                'total_return': 0.0,
                'total_return_pct': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'num_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'trades': []
            }
            if include_visuals:
                metrics['visuals'] = {
                    'equity_curve': [],
                    'drawdown_series': [],
                    'monthly_returns': {},
                    'trade_distribution': {'wins': 0, 'losses': 0}
                }
            return metrics
        
        # Basic metrics
        total_pnl = sum(t.pnl for t in trades if t.pnl)
        winning_trades = [t for t in trades if t.outcome == 'win']
        losing_trades = [t for t in trades if t.outcome == 'loss']
        
        win_rate = len(winning_trades) / len(trades) if trades else 0.0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades if t.pnl)
        gross_loss = abs(sum(t.pnl for t in losing_trades if t.pnl))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Returns
        returns = [t.pnl_pct for t in trades if t.pnl_pct]
        
        # Sharpe ratio
        # Note: This is a simplified calculation using per-trade returns
        # For proper Sharpe, we'd need daily portfolio returns
        if returns and len(returns) > 1:
            avg_return = sum(returns) / len(returns)
            std_return = pd.Series(returns).std()
            # Calculate Sharpe based on per-trade returns (no annualization)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Max drawdown
        equity_curve = [initial_capital]
        for trade in trades:
            equity_curve.append(equity_curve[-1] + (trade.pnl or 0))
        
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min()
        
        metrics = {
            'total_return': total_pnl,
            'total_return_pct': total_pnl / initial_capital,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'num_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': gross_profit / len(winning_trades) if winning_trades else 0,
            'avg_loss': gross_loss / len(losing_trades) if losing_trades else 0,
            'trades': [self._trade_to_dict(t) for t in trades]
        }
        
        # Add visual data if requested
        if include_visuals:
            equity_curve_data = self._generate_equity_curve(trades, initial_capital)
            metrics['visuals'] = {
                'equity_curve': equity_curve_data,
                'drawdown_series': self._generate_drawdown_series(equity_curve_data),
                'monthly_returns': self._generate_monthly_returns(trades),
                'trade_distribution': {
                    'wins': len(winning_trades),
                    'losses': len(losing_trades)
                }
            }
        
        return metrics
    
    def _generate_equity_curve(self, trades: List[Trade], initial_capital: float) -> List[Dict]:
        """
        Generate equity curve data for visualization
        
        Returns list of {date, equity, trade_pnl} for charting
        """
        equity_curve = []
        current_equity = initial_capital
        
        # Add starting point
        if trades:
            equity_curve.append({
                'date': trades[0].entry_date.isoformat() if trades[0].entry_date else None,
                'equity': current_equity,
                'trade_pnl': 0
            })
            
            # Add each trade exit
            for trade in trades:
                if trade.exit_date and trade.pnl is not None:
                    current_equity += trade.pnl
                    equity_curve.append({
                        'date': trade.exit_date.isoformat(),
                        'equity': current_equity,
                        'trade_pnl': trade.pnl
                    })
        else:
            # No trades - create flat line at initial capital
            # Use current date for two points to show flat line
            from datetime import datetime
            today = datetime.now().isoformat()
            equity_curve = [
                {
                    'date': today,
                    'equity': initial_capital,
                    'trade_pnl': 0
                },
                {
                    'date': today,
                    'equity': initial_capital,
                    'trade_pnl': 0
                }
            ]
        
        return equity_curve
    
    def _generate_drawdown_series(self, equity_curve: List[Dict]) -> List[Dict]:
        """
        Calculate drawdown over time for visualization
        
        Drawdown shows the decline from peak equity
        """
        if not equity_curve:
            return []
        
        drawdown_series = []
        peak_equity = equity_curve[0]['equity']
        
        for point in equity_curve:
            equity = point['equity']
            
            # Update peak
            if equity > peak_equity:
                peak_equity = equity
            
            # Calculate drawdown as percentage from peak
            drawdown = (equity - peak_equity) / peak_equity if peak_equity > 0 else 0
            
            drawdown_series.append({
                'date': point['date'],
                'drawdown': drawdown,
                'equity': equity,
                'peak': peak_equity
            })
        
        return drawdown_series
    
    def _generate_monthly_returns(self, trades: List[Trade]) -> Dict:
        """
        Group returns by month for heatmap visualization
        
        Returns dict with 'YYYY-MM' keys and percentage returns
        """
        monthly_returns = {}
        
        for trade in trades:
            if trade.exit_date and trade.pnl_pct is not None:
                # Format as YYYY-MM
                month_key = trade.exit_date.strftime('%Y-%m')
                
                # Accumulate returns for the month
                if month_key not in monthly_returns:
                    monthly_returns[month_key] = 0
                monthly_returns[month_key] += trade.pnl_pct
        
        return monthly_returns
    
    def _trade_to_dict(self, trade: Trade) -> Dict:
        """Convert Trade object to dict"""
        return {
            'symbol': trade.symbol,
            'entry_price': trade.entry_price,
            'entry_date': trade.entry_date.isoformat() if trade.entry_date else None,
            'exit_price': trade.exit_price,
            'exit_date': trade.exit_date.isoformat() if trade.exit_date else None,
            'stop': trade.stop,
            'target': trade.target,
            'shares': trade.shares,
            'pnl': trade.pnl,
            'pnl_pct': trade.pnl_pct,
            'outcome': trade.outcome
        }

# Global instance
backtest_engine = BacktestEngine()

