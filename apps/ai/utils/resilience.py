"""
Resilient service calls with retries, fallbacks, and circuit breakers
"""
import asyncio
import logging
from typing import Callable, Optional, Any
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """Base exception for service errors"""
    pass

class ServiceUnavailable(ServiceError):
    """Service is temporarily unavailable"""
    pass

class RateLimitExceeded(ServiceError):
    """Rate limit exceeded"""
    pass

class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures"""
    
    def __init__(self, service_name: str, failure_threshold: int = 5, timeout: int = 60):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds before trying again
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def record_failure(self):
        """Record a service failure"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"[CIRCUIT BREAKER OPEN] {self.service_name} appears to be down. "
                f"Blocking requests for {self.timeout}s"
            )
    
    def record_success(self):
        """Record a service success"""
        self.failure_count = 0
        self.last_failure_time = None
        
        if self.state == "OPEN":
            logger.info(f"[CIRCUIT BREAKER CLOSED] {self.service_name} service recovered.")
        
        self.state = "CLOSED"
    
    def should_allow_request(self) -> bool:
        """Check if request should be allowed"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                
                if elapsed > self.timeout:
                    # Move to half-open state (try one request)
                    self.state = "HALF_OPEN"
                    logger.info(f"[CIRCUIT BREAKER HALF-OPEN] {self.service_name} - Trying one request.")
                    return True
            
            return False
        
        # HALF_OPEN state - allow the request
        return True

class ResilientService:
    """Wrapper for resilient external service calls"""
    
    def __init__(self):
        self.circuit_breakers = {}  # service_name -> CircuitBreaker
    
    async def call_with_fallback(
        self,
        primary_fn: Callable,
        fallback_fn: Optional[Callable] = None,
        max_retries: int = 3,
        service_name: str = "unknown",
        raise_on_failure: bool = False
    ) -> Any:
        """
        Call primary function with retries and fallback
        
        Args:
            primary_fn: Primary function to call
            fallback_fn: Fallback if primary fails (optional)
            max_retries: Maximum retry attempts
            service_name: Name for logging/monitoring
            raise_on_failure: If True, raise exception when both fail
        
        Returns:
            Result from primary or fallback
        
        Raises:
            ServiceUnavailable: If both primary and fallback fail (when raise_on_failure=True)
        """
        # Check circuit breaker
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(service_name)
        
        breaker = self.circuit_breakers[service_name]
        
        if not breaker.should_allow_request():
            logger.warning(f"Circuit breaker OPEN for {service_name}. Skipping to fallback.")
            if fallback_fn:
                return await fallback_fn()
            elif raise_on_failure:
                raise ServiceUnavailable(f"{service_name} circuit breaker is OPEN")
            else:
                return None
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Calling {service_name} (attempt {attempt + 1}/{max_retries})")
                result = await primary_fn()
                
                # Reset circuit breaker on success
                breaker.record_success()
                
                return result
            
            except Exception as e:
                last_error = e
                logger.warning(
                    f"{service_name} failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                
                # Record failure in circuit breaker
                breaker.record_failure()
                
                # Exponential backoff
                if attempt < max_retries - 1:
                    backoff = 2 ** attempt  # 1s, 2s, 4s
                    logger.debug(f"Backing off for {backoff}s")
                    await asyncio.sleep(backoff)
        
        # Primary failed after all retries
        logger.error(f"{service_name} exhausted all retries. Last error: {last_error}")
        
        # Try fallback if available
        if fallback_fn:
            try:
                logger.info(f"Using fallback for {service_name}")
                result = await fallback_fn()
                logger.info(f"Fallback succeeded for {service_name}")
                return result
            
            except Exception as fallback_error:
                logger.error(f"Fallback also failed for {service_name}: {fallback_error}")
                
                if raise_on_failure:
                    raise ServiceUnavailable(
                        f"{service_name} and fallback both failed. "
                        f"Primary: {last_error}, Fallback: {fallback_error}"
                    )
                
                return None
        
        # No fallback available
        if raise_on_failure:
            raise ServiceUnavailable(f"{service_name} failed: {last_error}")
        
        logger.warning(f"[WARNING] {service_name.upper()} IS DOWN - Returning None")
        return None

# Global instance
resilient_service = ResilientService()

def with_resilience(service_name: str, fallback_fn: Optional[Callable] = None):
    """
    Decorator for resilient service calls
    
    Usage:
        @with_resilience("openai", fallback_fn=use_groq_instead)
        async def call_openai():
            return await openai.chat.completions.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await resilient_service.call_with_fallback(
                primary_fn=lambda: func(*args, **kwargs),
                fallback_fn=fallback_fn,
                service_name=service_name
            )
        return wrapper
    return decorator

