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
    
    async def run_backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy_fn: Callable,
        initial_capital: float = 100000.0
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
            
            # Run strategy
            trades = await self._simulate_trades(data, strategy_fn, initial_capital)
            
            # Calculate metrics
            metrics = self._calculate_metrics(trades, initial_capital)
            
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
        
        for i in range(20, len(data)):  # Start after indicator warmup
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
            
            elif current_position:
                # Check for exit conditions
                high = data['High'].iloc[i]
                low = data['Low'].iloc[i]
                
                # Stop hit
                if current_position.direction == "BUY" and low <= current_position.stop:
                    current_position.exit_price = current_position.stop
                    current_position.exit_date = current_date
                    current_position.outcome = 'loss'
                
                # Target hit
                elif current_position.direction == "BUY" and high >= current_position.target:
                    current_position.exit_price = current_position.target
                    current_position.exit_date = current_date
                    current_position.outcome = 'win'
                
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
                    
                    trades.append(current_position)
                    current_position = None
        
        return trades
    
    def _calculate_metrics(self, trades: List[Trade], initial_capital: float) -> Dict:
        """Calculate performance metrics"""
        if not trades:
            return {
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
        
        return {
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

