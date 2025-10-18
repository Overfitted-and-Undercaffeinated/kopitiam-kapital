"""
Market Data Cache - Avoid repeated downloads
Saves 1-3 seconds on cache hits
"""
import pandas as pd
from datetime import datetime
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

class MarketDataCache:
    """
    Simple in-memory cache for market data
    
    Features:
    - TTL-based expiration (default 1 hour)
    - Automatic cleanup of old entries
    - Thread-safe (using simple dict, good enough for single-process)
    
    Usage:
        cache = MarketDataCache(ttl_seconds=3600)
        data = await cache.get_or_fetch(
            "AAPL", 
            "max",
            fetch_function
        )
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize cache
        
        Args:
            ttl_seconds: Time-to-live in seconds (default: 1 hour)
        """
        self._cache = {}
        self._ttl = ttl_seconds
        logger.info(f"Initialized MarketDataCache with {ttl_seconds}s TTL")
    
    async def get_or_fetch(
        self,
        symbol: str,
        period: str,
        fetch_fn: Callable
    ) -> Optional[pd.DataFrame]:
        """
        Get data from cache or fetch if not available
        
        Args:
            symbol: Stock symbol
            period: Period (e.g., "1y", "2y", "max")
            fetch_fn: Async function to fetch data if not in cache
        
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = self._make_key(symbol, period)
        
        # Check cache
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            age = datetime.now().timestamp() - timestamp
            
            # Check if still valid
            if age < self._ttl:
                logger.info(
                    f"Cache HIT for {symbol} (age: {age:.0f}s, "
                    f"rows: {len(data) if data is not None else 0})"
                )
                return data
            else:
                # Expired - remove from cache
                logger.info(f"Cache EXPIRED for {symbol} (age: {age:.0f}s)")
                del self._cache[cache_key]
        
        # Cache miss - fetch data
        logger.info(f"Cache MISS for {symbol}, fetching...")
        try:
            data = await fetch_fn()
            
            # Store in cache
            self._cache[cache_key] = (data, datetime.now().timestamp())
            
            logger.info(
                f"Cached {symbol} data "
                f"({len(data) if data is not None else 0} rows)"
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            raise
    
    def _make_key(self, symbol: str, period: str) -> str:
        """Generate cache key"""
        return f"{symbol.upper()}_{period}"
    
    def invalidate(self, symbol: str = None, period: str = None):
        """
        Invalidate cache entries
        
        Args:
            symbol: If provided, only invalidate this symbol
            period: If provided, only invalidate this period
        """
        if symbol and period:
            # Invalidate specific entry
            key = self._make_key(symbol, period)
            if key in self._cache:
                del self._cache[key]
                logger.info(f"Invalidated cache for {symbol}_{period}")
        elif symbol:
            # Invalidate all entries for symbol
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(f"{symbol.upper()}_")]
            for key in keys_to_delete:
                del self._cache[key]
            logger.info(f"Invalidated {len(keys_to_delete)} cache entries for {symbol}")
        else:
            # Invalidate all
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Invalidated all cache entries ({count} total)")
    
    def cleanup_expired(self):
        """Remove all expired entries from cache"""
        now = datetime.now().timestamp()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if (now - timestamp) > self._ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        now = datetime.now().timestamp()
        
        total_entries = len(self._cache)
        total_size = sum(
            len(data) if isinstance(data, pd.DataFrame) else 0
            for data, _ in self._cache.values()
        )
        
        ages = [now - timestamp for _, timestamp in self._cache.values()]
        avg_age = sum(ages) / len(ages) if ages else 0
        
        return {
            'total_entries': total_entries,
            'total_rows': total_size,
            'average_age_seconds': avg_age,
            'ttl_seconds': self._ttl
        }

# Global instance
market_data_cache = MarketDataCache(ttl_seconds=3600)  # 1 hour TTL

