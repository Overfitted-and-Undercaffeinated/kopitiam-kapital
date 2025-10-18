"""
Technical indicators for backtesting
Implements: ATR, RSI, SMA/EMA, MACD
"""
import pandas as pd
import numpy as np
from typing import Union, Tuple
import logging

logger = logging.getLogger(__name__)

def calculate_sma(prices: Union[pd.Series, np.ndarray], period: int) -> pd.Series:
    """
    Calculate Simple Moving Average
    
    Args:
        prices: Price series
        period: SMA period (e.g. 20, 50, 200)
    
    Returns:
        pd.Series: SMA values
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    return prices.rolling(window=period).mean()

def calculate_ema(prices: Union[pd.Series, np.ndarray], period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average
    
    Args:
        prices: Price series
        period: EMA period
    
    Returns:
        pd.Series: EMA values
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    return prices.ewm(span=period, adjust=False).mean()

def calculate_rsi(prices: Union[pd.Series, np.ndarray], period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: Price series
        period: RSI period (default: 14)
    
    Returns:
        pd.Series: RSI values (0-100)
    
    Example:
        rsi = calculate_rsi(df['close'], period=14)
        oversold = rsi < 30  # Oversold signal
        overbought = rsi > 70  # Overbought signal
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(
    prices: Union[pd.Series, np.ndarray],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: Price series
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)
    
    Returns:
        Tuple of (macd_line, signal_line, histogram)
    
    Example:
        macd, signal, histogram = calculate_macd(df['close'])
        buy_signal = (macd > signal) & (macd.shift(1) <= signal.shift(1))  # MACD crosses above signal
        sell_signal = (macd < signal) & (macd.shift(1) >= signal.shift(1))  # MACD crosses below signal
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)
    
    # MACD line = Fast EMA - Slow EMA
    macd_line = ema_fast - ema_slow
    
    # Signal line = EMA of MACD line
    signal_line = calculate_ema(macd_line, signal_period)
    
    # Histogram = MACD - Signal
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calculate_atr(
    high: Union[pd.Series, np.ndarray],
    low: Union[pd.Series, np.ndarray],
    close: Union[pd.Series, np.ndarray],
    period: int = 14
) -> pd.Series:
    """
    Calculate Average True Range (ATR)
    Measures market volatility
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ATR period (default: 14)
    
    Returns:
        pd.Series: ATR values
    
    Example:
        atr = calculate_atr(df['high'], df['low'], df['close'])
        # Use ATR for stop loss: stop_loss = entry_price - (2 * atr)
    """
    if isinstance(high, np.ndarray):
        high = pd.Series(high)
        low = pd.Series(low)
        close = pd.Series(close)
    
    # Calculate True Range components
    tr1 = high - low  # Current high - low
    tr2 = abs(high - close.shift(1))  # Current high - previous close
    tr3 = abs(low - close.shift(1))  # Current low - previous close
    
    # True Range is the max of the three
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR is the moving average of TR
    atr = tr.rolling(window=period).mean()
    
    return atr

def calculate_bollinger_bands(
    prices: Union[pd.Series, np.ndarray],
    period: int = 20,
    std_dev: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: Price series
        period: Period for moving average (default: 20)
        std_dev: Number of standard deviations (default: 2)
    
    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    if isinstance(prices, np.ndarray):
        prices = pd.Series(prices)
    
    # Middle band is SMA
    middle_band = calculate_sma(prices, period)
    
    # Standard deviation
    std = prices.rolling(window=period).std()
    
    # Upper and lower bands
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band

def calculate_stochastic(
    high: Union[pd.Series, np.ndarray],
    low: Union[pd.Series, np.ndarray],
    close: Union[pd.Series, np.ndarray],
    k_period: int = 14,
    d_period: int = 3
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate Stochastic Oscillator
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)
    
    Returns:
        Tuple of (%K, %D)
    """
    if isinstance(high, np.ndarray):
        high = pd.Series(high)
        low = pd.Series(low)
        close = pd.Series(close)
    
    # Calculate %K
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    
    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    
    # %D is SMA of %K
    d = k.rolling(window=d_period).mean()
    
    return k, d

def calculate_adx(
    high: Union[pd.Series, np.ndarray],
    low: Union[pd.Series, np.ndarray],
    close: Union[pd.Series, np.ndarray],
    period: int = 14
) -> pd.Series:
    """
    Calculate Average Directional Index (ADX)
    Measures trend strength (0-100)
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ADX period (default: 14)
    
    Returns:
        pd.Series: ADX values
        
    Interpretation:
        ADX < 20: Weak trend
        ADX 20-40: Strong trend
        ADX > 40: Very strong trend
    """
    if isinstance(high, np.ndarray):
        high = pd.Series(high)
        low = pd.Series(low)
        close = pd.Series(close)
    
    # Calculate directional movement
    plus_dm = high.diff()
    minus_dm = -low.diff()
    
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    
    # Calculate ATR
    atr = calculate_atr(high, low, close, period)
    
    # Calculate directional indicators
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    # Calculate DX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    
    # ADX is EMA of DX
    adx = calculate_ema(dx, period)
    
    return adx

# Helper function for strategy builders
def add_indicators_to_dataframe(
    df: pd.DataFrame,
    indicators: list
) -> pd.DataFrame:
    """
    Add multiple indicators to a dataframe
    
    Args:
        df: DataFrame with OHLCV data
        indicators: List of indicator configs
            [
                {'type': 'sma', 'period': 20},
                {'type': 'rsi', 'period': 14},
                {'type': 'macd'},
                {'type': 'atr'},
            ]
    
    Returns:
        DataFrame with indicators added as columns
    """
    df = df.copy()
    
    for indicator in indicators:
        ind_type = indicator.get('type')
        
        if ind_type == 'sma':
            period = indicator.get('period', 20)
            df[f'sma_{period}'] = calculate_sma(df['close'], period)
        
        elif ind_type == 'ema':
            period = indicator.get('period', 20)
            df[f'ema_{period}'] = calculate_ema(df['close'], period)
        
        elif ind_type == 'rsi':
            period = indicator.get('period', 14)
            df['rsi'] = calculate_rsi(df['close'], period)
        
        elif ind_type == 'macd':
            macd, signal, hist = calculate_macd(df['close'])
            df['macd'] = macd
            df['macd_signal'] = signal
            df['macd_hist'] = hist
        
        elif ind_type == 'atr':
            period = indicator.get('period', 14)
            df['atr'] = calculate_atr(df['high'], df['low'], df['close'], period)
        
        elif ind_type == 'bollinger':
            period = indicator.get('period', 20)
            std_dev = indicator.get('std_dev', 2.0)
            upper, middle, lower = calculate_bollinger_bands(df['close'], period, std_dev)
            df['bb_upper'] = upper
            df['bb_middle'] = middle
            df['bb_lower'] = lower
        
        elif ind_type == 'stochastic':
            k_period = indicator.get('k_period', 14)
            d_period = indicator.get('d_period', 3)
            k, d = calculate_stochastic(df['high'], df['low'], df['close'], k_period, d_period)
            df['stoch_k'] = k
            df['stoch_d'] = d
        
        elif ind_type == 'adx':
            period = indicator.get('period', 14)
            df['adx'] = calculate_adx(df['high'], df['low'], df['close'], period)
        
        else:
            logger.warning(f"Unknown indicator type: {ind_type}")
    
    return df
