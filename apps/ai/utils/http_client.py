"""
Shared HTTP client for efficient connection pooling
Reduces resource overhead and prevents connection leaks
"""
import httpx
import logging

logger = logging.getLogger(__name__)

class HTTPClientManager:
    """
    Singleton async HTTP client manager
    
    Benefits:
    - Connection pooling (reuse connections)
    - Reduced resource overhead
    - Prevents connection leaks
    - Centralized timeout/limit configuration
    """
    
    def __init__(self):
        self._client = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """
        Get or create shared HTTP client
        
        Returns:
            Configured httpx.AsyncClient with connection pooling
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20
                )
            )
            logger.info("Initialized shared HTTP client with connection pooling")
        return self._client
    
    async def close(self):
        """Close shared HTTP client gracefully"""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Closed shared HTTP client")

# Global singleton instance
http_client_manager = HTTPClientManager()

