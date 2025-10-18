"""Exa.ai client for web search and retrieval"""

class ExaClient:
    """Client for Exa.ai search API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search_fast(self, query: str, num_results: int = 10):
        """Fast search for recent news and articles"""
        # TODO: Implement Exa fast search
        pass
    
    async def search_deep(self, query: str, num_results: int = 10):
        """Deep search with full content retrieval"""
        # TODO: Implement Exa deep search
        pass
    
    async def get_contents(self, urls: list[str]):
        """Get full content for URLs"""
        # TODO: Implement content retrieval
        pass

