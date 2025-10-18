"""
Pre-run backtest results for demo
🚨 WARNING: This is demo data from historical runs
"""
import logging

logger = logging.getLogger(__name__)

# Pre-run backtest results for popular stocks
DEMO_BACKTEST_RESULTS = {
    ("NVDA", "rsi_oversold"): {
        "win_rate": 0.67,
        "total_return_pct": 0.23,
        "sharpe_ratio": 1.85,
        "num_trades": 45,
        "max_drawdown": -0.12,
        "avg_win": 0.08,
        "avg_loss": -0.04
    },
    
    ("TSLA", "rsi_oversold"): {
        "win_rate": 0.58,
        "total_return_pct": 0.15,
        "sharpe_ratio": 1.42,
        "num_trades": 52,
        "max_drawdown": -0.18,
        "avg_win": 0.09,
        "avg_loss": -0.05
    },
    
    ("AAPL", "rsi_oversold"): {
        "win_rate": 0.71,
        "total_return_pct": 0.19,
        "sharpe_ratio": 1.98,
        "num_trades": 38,
        "max_drawdown": -0.08,
        "avg_win": 0.07,
        "avg_loss": -0.03
    },
    
    ("NVDA", "momentum_breakout"): {
        "win_rate": 0.62,
        "total_return_pct": 0.31,
        "sharpe_ratio": 1.67,
        "num_trades": 34,
        "max_drawdown": -0.15,
        "avg_win": 0.12,
        "avg_loss": -0.06
    },
    
    ("TSLA", "momentum_breakout"): {
        "win_rate": 0.55,
        "total_return_pct": 0.08,
        "sharpe_ratio": 1.15,
        "num_trades": 42,
        "max_drawdown": -0.22,
        "avg_win": 0.11,
        "avg_loss": -0.07
    },
    
    ("AAPL", "macd_crossover"): {
        "win_rate": 0.64,
        "total_return_pct": 0.17,
        "sharpe_ratio": 1.73,
        "num_trades": 28,
        "max_drawdown": -0.10,
        "avg_win": 0.08,
        "avg_loss": -0.04
    },
    
    ("AMD", "rsi_oversold"): {
        "win_rate": 0.69,
        "total_return_pct": 0.28,
        "sharpe_ratio": 1.91,
        "num_trades": 41,
        "max_drawdown": -0.14,
        "avg_win": 0.10,
        "avg_loss": -0.05
    },
    
    ("PLTR", "momentum_breakout"): {
        "win_rate": 0.73,
        "total_return_pct": 0.42,
        "sharpe_ratio": 2.12,
        "num_trades": 37,
        "max_drawdown": -0.11,
        "avg_win": 0.13,
        "avg_loss": -0.04
    },
    
    ("SPY", "sma_crossover"): {
        "win_rate": 0.60,
        "total_return_pct": 0.12,
        "sharpe_ratio": 1.55,
        "num_trades": 15,
        "max_drawdown": -0.07,
        "avg_win": 0.06,
        "avg_loss": -0.03
    },
    
    ("MSFT", "rsi_macd_combo"): {
        "win_rate": 0.75,
        "total_return_pct": 0.26,
        "sharpe_ratio": 2.08,
        "num_trades": 32,
        "max_drawdown": -0.09,
        "avg_win": 0.09,
        "avg_loss": -0.03
    }
}

def get_demo_backtest(symbol: str, strategy_id: str) -> dict:
    """
    Get pre-run backtest results
    
    🚨 WARNING: This returns pre-computed demo data
    
    Args:
        symbol: Stock ticker
        strategy_id: Strategy template ID
    
    Returns:
        Backtest results dict or None
    """
    key = (symbol, strategy_id)
    if key in DEMO_BACKTEST_RESULTS:
        logger.warning(f"🚨 DEMO MODE - Returning pre-run backtest for {symbol} / {strategy_id}")
        data = DEMO_BACKTEST_RESULTS[key].copy()
        data['demo_mode'] = True
        data['note'] = f"Pre-run backtest from 2024-01-01 to 2025-01-01"
        return data
    
    return None

def list_demo_backtests() -> list:
    """Get list of available demo backtests"""
    return [
        {'symbol': symbol, 'strategy': strategy}
        for symbol, strategy in DEMO_BACKTEST_RESULTS.keys()
    ]

demo_backtest_results = DEMO_BACKTEST_RESULTS

