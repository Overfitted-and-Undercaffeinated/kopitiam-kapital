"""
Market data service with configurable providers
Supports: yfinance (free, testing) and Alpha Vantage (paid, demo)
"""
import yfinance as yf
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging

# Flexible imports
try:
    from ..utils.config import settings
    from ..data.data_cache import market_data_cache
except ImportError:
    from utils.config import settings
    from data.data_cache import market_data_cache

logger = logging.getLogger(__name__)

class MarketDataService:
    """Unified interface for market data with provider switching"""
    
    def __init__(self):
        self.provider = settings.market_data_provider
        
        if self.provider == "alphavantage":
            if not settings.alpha_vantage_api_key:
                logger.warning("Alpha Vantage selected but no API key. Falling back to yfinance.")
                self.provider = "yfinance"
            else:
                try:
                    from alpha_vantage.timeseries import TimeSeries
                    self.av = TimeSeries(key=settings.alpha_vantage_api_key, output_format='pandas')
                except ImportError:
                    logger.warning("alpha-vantage not installed. Falling back to yfinance.")
                    self.provider = "yfinance"
        
        logger.info(f"Market data provider: {self.provider}")
    
    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Ticker symbol (e.g., "AAPL")
        
        Returns:
            Current price or None if unavailable
        """
        if settings.use_mock_market_data:
            return self._mock_price(symbol)
        
        try:
            if self.provider == "yfinance":
                ticker = yf.Ticker(symbol)
                # Use 5d period to get data even when markets are closed
                data = ticker.history(period="5d")
                if data.empty:
                    logger.warning(f"No data for {symbol}")
                    return None
                # Get the most recent closing price
                return float(data['Close'].iloc[-1])
            
            elif self.provider == "alphavantage":
                data, _ = self.av.get_quote_endpoint(symbol=symbol)
                return float(data['05. price'][0])
        
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def get_ohlcv(
        self, 
        symbol: str, 
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get OHLCV data with caching
        
        Args:
            symbol: Ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data or None
        """
        if settings.use_mock_market_data:
            return self._mock_ohlcv(symbol, period)
        
        # Define fetch function for cache
        async def fetch_data():
            try:
                if self.provider == "yfinance":
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period, interval=interval)
                    return data
                
                elif self.provider == "alphavantage":
                    # Alpha Vantage has different period/interval logic
                    data, _ = self.av.get_daily(symbol=symbol, outputsize='full')
                    # Convert to match yfinance format
                    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    return data.head(self._period_to_days(period))
            
            except Exception as e:
                logger.error(f"Error fetching OHLCV for {symbol}: {e}")
                return None
        
        # Use cache (saves 1-3 seconds on cache hits!)
        return await market_data_cache.get_or_fetch(symbol, period, fetch_data)
    
    async def get_intraday(
        self,
        symbol: str,
        interval: str = "5min",
        days_back: int = 5
    ) -> Optional[pd.DataFrame]:
        """
        Get intraday data for technical indicators
        
        Args:
            symbol: Ticker symbol
            interval: Time interval (1min, 5min, 15min, 30min, 60min)
            days_back: Number of days to fetch
        
        Returns:
            DataFrame with intraday OHLCV
        """
        if settings.use_mock_market_data:
            return self._mock_intraday(symbol, interval, days_back)
        
        try:
            if self.provider == "yfinance":
                ticker = yf.Ticker(symbol)
                # yfinance periods for intraday: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
                period_map = {1: "1d", 5: "5d", 30: "1mo"}
                period = period_map.get(days_back, "5d")
                data = ticker.history(period=period, interval=interval)
                return data
            
            elif self.provider == "alphavantage":
                data, _ = self.av.get_intraday(
                    symbol=symbol,
                    interval=interval,
                    outputsize='full'
                )
                data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                return data
        
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return None
    
    def _period_to_days(self, period: str) -> int:
        """Convert period string to number of days"""
        mapping = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
            "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
        }
        return mapping.get(period, 30)
    
    def _mock_price(self, symbol: str) -> float:
        """Generate mock price for testing"""
        # Deterministic mock based on symbol
        base_price = sum(ord(c) for c in symbol)
        return float(base_price % 1000 + 100)
    
    def _mock_ohlcv(self, symbol: str, period: str) -> pd.DataFrame:
        """Generate realistic mock OHLCV data for testing"""
        days = self._period_to_days(period)
        base_price = self._mock_price(symbol)
        
        # Generate realistic price movements with volatility
        import numpy as np
        np.random.seed(42)  # For reproducible results
        
        dates = pd.date_range(end=datetime.now(), periods=days)
        
        # Create price movements with some volatility
        price_changes = np.random.normal(0, 2, days)  # Random price changes
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] + change
            prices.append(max(new_price, base_price * 0.5))  # Keep prices reasonable
        
        # Generate OHLC from close prices
        data = pd.DataFrame({
            'Open': [p + np.random.uniform(-1, 1) for p in prices],
            'High': [p + np.random.uniform(0, 3) for p in prices],
            'Low': [p - np.random.uniform(0, 3) for p in prices],
            'Close': prices,
            'Volume': [int(1000000 + np.random.uniform(-200000, 500000)) for _ in range(days)]
        }, index=dates)
        
        # Ensure High >= Low and High >= Open, Close
        data['High'] = data[['Open', 'High', 'Close']].max(axis=1)
        data['Low'] = data[['Open', 'Low', 'Close']].min(axis=1)
        
        return data
    
    def _mock_intraday(self, symbol: str, interval: str, days_back: int) -> pd.DataFrame:
        """Generate mock intraday data"""
        # For testing, just return daily data
        return self._mock_ohlcv(symbol, f"{days_back}d")

# Global instance
market_data_service = MarketDataService()

