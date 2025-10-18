"""
Rate limiter using Redis token bucket algorithm (with in-memory fallback)
Prevents API abuse and controls costs
"""
import redis.asyncio as redis
from datetime import datetime, timedelta
import logging
from typing import Dict, Tuple
from .config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Token bucket rate limiter with Redis backend
    
    Features:
    - Redis for production (distributed rate limiting)
    - In-memory fallback for development (no Redis required)
    - Graceful degradation if Redis unavailable
    """
    
    def __init__(self):
        self.redis = None
        self.memory_store: Dict[str, Tuple[int, datetime]] = {}  # key: (count, expires_at)
        self.enabled = settings.enable_rate_limiting
        logger.info("Rate limiter initialized (Redis optional, in-memory fallback enabled)")
    
    async def _get_redis(self):
        """
        Lazy Redis connection with graceful failure
        
        Returns None if Redis unavailable (triggers in-memory fallback)
        """
        if self.redis is None:
            try:
                self.redis = await redis.from_url(settings.redis_url, decode_responses=True)
                logger.info("Connected to Redis for rate limiting")
            except Exception as e:
                # Don't log as error - expected in dev without Redis
                logger.debug(f"Redis unavailable (using in-memory fallback): {e}")
                self.redis = None
        return self.redis
    
    def _check_memory_limit(self, key: str, max_calls: int, window_seconds: int) -> bool:
        """
        In-memory rate limit check (fallback when Redis unavailable)
        
        Args:
            key: Unique key for this limit
            max_calls: Maximum calls allowed
            window_seconds: Time window in seconds
        
        Returns:
            True if under limit, False if exceeded
        """
        now = datetime.now()
        
        # Clean expired entries periodically
        expired_keys = [k for k, (_, expires_at) in self.memory_store.items() if expires_at < now]
        for k in expired_keys:
            del self.memory_store[k]
        
        # Check current key
        if key not in self.memory_store:
            # First call in window
            expires_at = now + timedelta(seconds=window_seconds)
            self.memory_store[key] = (1, expires_at)
            return True
        
        count, expires_at = self.memory_store[key]
        
        if now > expires_at:
            # Window expired, reset
            expires_at = now + timedelta(seconds=window_seconds)
            self.memory_store[key] = (1, expires_at)
            return True
        
        if count < max_calls:
            # Increment counter
            self.memory_store[key] = (count + 1, expires_at)
            return True
        
        # Rate limit exceeded
        remaining_seconds = (expires_at - now).total_seconds()
        logger.warning(f"Rate limit exceeded for {key} (memory). Resets in {remaining_seconds:.0f}s")
        return False
    
    async def check_limit(
        self,
        key: str,
        max_calls: int,
        window_seconds: int = 3600
    ) -> bool:
        """
        Check if request is within rate limit
        
        Args:
            key: Unique key for this limit (e.g., "exa_api_user123")
            max_calls: Maximum calls allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            True if under limit, False if exceeded
        """
        if not self.enabled:
            return True
        
        try:
            r = await self._get_redis()
            
            if r is None:
                # Redis unavailable - use in-memory fallback
                return self._check_memory_limit(key, max_calls, window_seconds)
            
            # Get current count
            current = await r.get(key)
            
            if current is None:
                # First call in window
                await r.setex(key, window_seconds, 1)
                return True
            
            current = int(current)
            
            if current < max_calls:
                # Increment counter
                await r.incr(key)
                return True
            
            # Rate limit exceeded
            ttl = await r.ttl(key)
            logger.warning(f"Rate limit exceeded for {key}. Resets in {ttl}s")
            return False
        
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fail open - allow request on unexpected errors
            return True
    
    async def get_remaining(self, key: str, max_calls: int) -> int:
        """Get remaining calls in current window"""
        if not self.enabled:
            return max_calls
        
        try:
            r = await self._get_redis()
            
            if r is None:
                return max_calls
            
            current = await r.get(key)
            
            if current is None:
                return max_calls
            
            return max(0, max_calls - int(current))
        
        except Exception as e:
            logger.error(f"Error getting remaining calls: {e}")
            return max_calls

# Global instance
rate_limiter = RateLimiter()

