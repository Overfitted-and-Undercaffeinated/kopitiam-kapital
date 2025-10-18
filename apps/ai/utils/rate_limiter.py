"""
Rate limiter using Redis token bucket algorithm
Prevents API abuse and controls costs
"""
import redis.asyncio as redis
from datetime import datetime, timedelta
import logging
from .config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter with Redis backend"""
    
    def __init__(self):
        self.redis = None
        self.enabled = settings.enable_rate_limiting
    
    async def _get_redis(self):
        """Lazy Redis connection"""
        if self.redis is None:
            try:
                self.redis = await redis.from_url(settings.redis_url, decode_responses=True)
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.redis = None
        return self.redis
    
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
                # Redis unavailable - fail open (allow request)
                logger.warning("Redis unavailable for rate limiting - allowing request")
                return True
            
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
            # Fail open - allow request if Redis is down
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

