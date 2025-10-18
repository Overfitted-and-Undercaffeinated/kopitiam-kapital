"""
Example trading strategies for backtesting
"""
from typing import Optional, Dict
import pandas as pd

# Flexible imports
try:
    from ..data.indicators import calculate_atr
except ImportError:
    from data.indicators import calculate_atr

async def momentum_breakout_strategy(data: pd.DataFrame) -> Optional[Dict]:
    """
    Simple momentum breakout strategy
    
    Entry: Price breaks above 20-day high
    Stop: 2x ATR below entry
    Target: 3x ATR above entry
    """
    if len(data) < 20:
        return None
    
    current_price = data['Close'].iloc[-1]
    high_20d = data['High'].iloc[-20:].max()
    
    # Breakout condition
    if current_price > high_20d:
        atr = calculate_atr(data['Close'].values, period=14)
        
        return {
            'direction': 'BUY',
            'entry': current_price,
            'stop': current_price - (2 * atr),
            'target': current_price + (3 * atr)
        }
    
    return None

async def rsi_oversold_strategy(data: pd.DataFrame) -> Optional[Dict]:
    """
    RSI oversold mean reversion strategy
    
    Entry: RSI < 30
    Stop: 5% below entry
    Target: RSI > 70 or +10%
    """
    if len(data) < 20:
        return None
    
    # TODO: Implement RSI calculation in indicators.py
    # For now, simple placeholder
    current_price = data['Close'].iloc[-1]
    recent_low = data['Low'].iloc[-5:].min()
    
    # Simple oversold proxy: price near recent low
    if current_price <= recent_low * 1.02:
        return {
            'direction': 'BUY',
            'entry': current_price,
            'stop': current_price * 0.95,
            'target': current_price * 1.10
        }
    
    return None

