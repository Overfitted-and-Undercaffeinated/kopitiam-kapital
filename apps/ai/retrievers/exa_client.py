"""
Exa.ai client for semantic web search
Focus: Financial news retrieval for MVP
"""
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

# Flexible imports
try:
    from ..utils.config import settings
    from ..utils.rate_limiter import rate_limiter
    from ..utils.cost_tracker import cost_tracker
    from ..utils.resilience import resilient_service
except ImportError:
    from utils.config import settings
    from utils.rate_limiter import rate_limiter
    from utils.cost_tracker import cost_tracker
    from utils.resilience import resilient_service

logger = logging.getLogger(__name__)

class ExaClient:
    """
    Client for Exa.ai semantic search API
    
    Features:
    - Fast mode: Recent financial news (<2s, top 5)
    - Deep mode: Full content retrieval (>2s, top 10)
    - Rate limiting: 500 calls/hour
    - Cost tracking: ~$0.01/search
    - Caching: 4-hour TTL for news
    - Mock mode: For testing without API calls
    """
    
    def __init__(self):
        self.api_key = settings.exa_api_key
        self.client = None
        self._cache = None  # Lazy load to avoid circular imports
        self.enabled = False  # Track if Exa is actually working
        
        # Initialize client if not in mock mode
        if not settings.use_mock_exa:
            try:
                from exa_py import Exa
                self.client = Exa(api_key=self.api_key)
                self.enabled = True
                logger.info("Initialized Exa.ai client")
            except ImportError:
                logger.warning("exa-py not installed. Install with: pip install exa-py")
                settings.use_mock_exa = True
            except Exception as e:
                logger.error(f"Failed to initialize Exa client: {e}")
                settings.use_mock_exa = True
    
    @property
    def cache(self):
        """Lazy load cache_strategy to avoid circular imports"""
        if self._cache is None:
            try:
                from ..rag.cache_strategy import cache_strategy
                self._cache = cache_strategy
            except ImportError:
                from rag.cache_strategy import cache_strategy
                self._cache = cache_strategy
        return self._cache
    
    async def search_fast(
        self,
        query: str,
        num_results: int = 5,
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Fast search for recent financial news
        
        Use case: Recommendation generation, quick research
        Latency: <2s target
        Results: Top 5 most relevant
        
        Args:
            query: Search query (e.g., "AAPL latest earnings news")
            num_results: Number of results to return (default: 5)
            user_id: Optional user ID for cost tracking
        
        Returns:
            List of search results with title, URL, snippet, published date
        """
        if settings.use_mock_exa:
            logger.warning("🚨 MOCK MODE - Exa.ai not enabled, returning mock results")
            return self._mock_search_results(query, num_results, mode="fast")
        
        # Check rate limit
        rate_key = f"exa_search_{user_id}" if user_id else "exa_search_global"
        
        if not await rate_limiter.check_limit(rate_key, settings.exa_calls_per_hour, 3600):
            logger.warning(f"Exa rate limit exceeded for {rate_key}. Using cached results.")
            cached = await self.cache.get_cached_results(query, "news")
            if cached:
                return cached
            return []
        
        # Define primary and fallback functions
        async def primary():
            return await self._exa_search(query, num_results, mode="fast")
        
        async def fallback():
            logger.info("Exa search failed, checking cache...")
            cached = await self.cache.get_cached_results(query, "news")
            return cached if cached else []
        
        # Make resilient call
        results = await resilient_service.call_with_fallback(
            primary_fn=primary,
            fallback_fn=fallback,
            max_retries=2,
            service_name="exa-search-fast"
        )
        
        # Track cost
        if user_id and results:
            await cost_tracker.log_cost(
                user_id=user_id,
                service="exa-search",
                units=num_results,
                metadata={"query": query, "mode": "fast"}
            )
        
        # Cache results
        if results:
            await self.cache.cache_results(query, "news", results, user_id)
        
        return results or []
    
    async def search_deep(
        self,
        query: str,
        num_results: int = 10,
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Deep search with full content retrieval
        
        Use case: Research reports, detailed analysis, morning briefs
        Latency: >2s (more thorough)
        Results: Top 10 with full content
        
        Args:
            query: Search query
            num_results: Number of results (default: 10)
            user_id: Optional user ID for cost tracking
        
        Returns:
            List of results with full content
        """
        if settings.use_mock_exa:
            logger.warning("🚨 MOCK MODE - Exa.ai not enabled, returning mock results")
            return self._mock_search_results(query, num_results, mode="deep")
        
        # Check rate limit
        rate_key = f"exa_search_{user_id}" if user_id else "exa_search_global"
        
        if not await rate_limiter.check_limit(rate_key, settings.exa_calls_per_hour, 3600):
            logger.warning(f"Exa rate limit exceeded for {rate_key}. Using cached results.")
            cached = await cache_strategy.get_cached_results(query, "research")
            return cached if cached else []
        
        # Define functions
        async def primary():
            return await self._exa_search(query, num_results, mode="deep")
        
        async def fallback():
            cached = await cache_strategy.get_cached_results(query, "research")
            return cached if cached else []
        
        # Make resilient call
        results = await resilient_service.call_with_fallback(
            primary_fn=primary,
            fallback_fn=fallback,
            max_retries=2,
            service_name="exa-search-deep"
        )
        
        # Track cost
        if user_id and results:
            await cost_tracker.log_cost(
                user_id=user_id,
                service="exa-search",
                units=num_results,
                metadata={"query": query, "mode": "deep"}
            )
        
        # Cache results
        if results:
            await cache_strategy.cache_results(query, "research", results, user_id)
        
        return results or []
    
    async def _exa_search(
        self,
        query: str,
        num_results: int,
        mode: str = "fast"
    ) -> List[Dict]:
        """
        Execute Exa.ai search
        
        Args:
            query: Search query
            num_results: Number of results
            mode: "fast" or "deep"
        
        Returns:
            Parsed search results
        """
        try:
            logger.info(f"Exa search ({mode}): '{query}' (top {num_results})")
            
            # Search parameters
            search_params = {
                "query": query,
                "num_results": num_results,
                "type": "neural",  # Semantic search
                "category": "financial news",
                "use_autoprompt": True,  # Let Exa optimize query
                "text": {"max_characters": 1000} if mode == "deep" else {"max_characters": 500},  # Get article text
                "highlights": {
                    "highlights_per_url": 3,
                    "num_sentences": 2,
                    "query": f"{query} sentiment analysis"
                }
            }
            
            # Add recency filter for fast mode
            if mode == "fast":
                # Recent news only (last 7 days for better results)
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                search_params["start_published_date"] = start_date
            
            # Execute search
            response = self.client.search_and_contents(**search_params)
            
            # Parse results
            results = self._parse_results(response, mode)
            
            logger.info(f"Exa returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Exa search failed: {e}")
            return []
    
    async def search_financial_documents(
        self,
        ticker: str,
        document_type: str = "10-K"
    ) -> Optional[Dict]:
        """
        Search for specific financial documents (10-K, earnings calls, annual reports)
        
        Args:
            ticker: Stock ticker (e.g., "AAPL")
            document_type: Type of document ("10-K", "earnings_call", "annual_report")
        
        Returns:
            Document with full text or None if not found
        """
        try:
            # Build search query for Exa.ai
            if document_type == "10-K":
                query = f"{ticker} 10-K SEC filing latest 2024 2025"
            elif document_type == "earnings_call":
                query = f"{ticker} earnings call transcript latest"
            elif document_type == "annual_report":
                query = f"{ticker} annual report latest"
            else:
                query = f"{ticker} {document_type} latest"
            
            logger.info(f"Searching for {document_type} for {ticker}: {query}")
            
            if settings.use_mock_exa:
                # Return mock document for testing
                return {
                    "title": f"{ticker} {document_type}",
                    "url": f"https://example.com/{ticker}-{document_type}",
                    "text": self._get_mock_document(ticker, document_type),
                    "published": datetime.now().isoformat(),
                    "source": "mock"
                }
            
            if not self.client:
                logger.error("Exa client not initialized")
                return None
            
            # Search with deep mode to get full text
            search_params = {
                "query": query,
                "num_results": 3,  # Get top 3 matches
                "type": "neural",
                "category": "financial documents",
                "use_autoprompt": True,
                "text": {"max_characters": 50000},  # Get significant text
            }
            
            response = self.client.search_and_contents(**search_params)
            
            if response.results:
                # Parse and return the first (best match) result
                best_result = response.results[0]
                return {
                    "title": best_result.title,
                    "url": best_result.url,
                    "text": best_result.text or "",
                    "published": best_result.published_date if hasattr(best_result, 'published_date') else datetime.now().isoformat(),
                    "source": "exa"
                }
            
            logger.warning(f"No {document_type} found for {ticker}")
            return None
        
        except Exception as e:
            logger.error(f"Error searching for {document_type} ({ticker}): {e}")
            return None
    
    def _get_mock_document(self, ticker: str, document_type: str) -> str:
        """Return mock financial document for testing"""
        mock_docs = {
            "10-K": f"""
SEC FORM 10-K: {ticker} ANNUAL REPORT

This is a mock 10-K filing for testing purposes.

BUSINESS OVERVIEW:
{ticker} is a leading technology company focused on innovation and customer satisfaction.
The company operates in multiple segments including software, hardware, and services.

FINANCIAL HIGHLIGHTS:
- Revenue: $150 billion
- Net Income: $25 billion  
- Operating Margin: 16.7%
- R&D Investment: $10 billion

RISKS:
- Market competition
- Regulatory changes
- Supply chain disruption
- Currency fluctuations

MANAGEMENT'S DISCUSSION & ANALYSIS:
The company performed well in fiscal year 2024, with strong revenue growth of 12% year-over-year.
Growth was driven by enterprise demand and new product launches.

OUTLOOK:
Management expects continued growth in the coming year, with focus on AI integration and sustainability.
""",
            "earnings_call": f"""
{ticker} Q4 2024 EARNINGS CALL TRANSCRIPT

CEO: Good afternoon everyone. Q4 was an exceptional quarter for {ticker}.

FINANCIAL RESULTS:
- Revenue: $38.5B (+12% YoY)
- Gross Margin: 46%
- Net Income: $7.2B
- EPS: $2.50

BUSINESS SEGMENTS:
1. Cloud Services: $15.2B revenue, +18% growth
2. AI Products: $8.1B revenue, +45% growth  
3. Traditional: $15.2B revenue, +2% growth

KEY ACHIEVEMENTS:
- Launched new AI assistant product
- Expanded cloud partnerships
- Improved operational efficiency

GUIDANCE:
Q1 2025: Revenue $37-39B
FY 2025: Revenue $155-160B

Q&A SESSION:
Analyst: Can you talk about AI adoption?
CEO: AI adoption is accelerating across all segments...
""",
            "annual_report": f"""
{ticker} 2024 ANNUAL REPORT

LETTER TO SHAREHOLDERS:
Dear Shareholders,
2024 was a transformative year for {ticker}...

KEY METRICS:
- Total Revenue: $152.8B (+12%)
- Operating Income: $25.5B
- Free Cash Flow: $28.3B
- Capital Returned: $35B

SUSTAINABILITY:
- Carbon neutral operations achieved
- 50% renewable energy
- Diversity: 40% women in leadership

INNOVATION:
- 3 major product launches
- 15% budget increase for R&D
- 2,500+ patents filed

STRATEGIC INITIATIVES:
1. AI-first approach
2. Cloud expansion
3. Emerging markets focus
"""
        }
        return mock_docs.get(document_type, f"Mock {document_type} for {ticker}")


    def _parse_results(self, response, mode: str) -> List[Dict]:
        """
        Parse Exa response to standard format
        
        Returns:
            List of dicts with: title, url, text, published_date, score, highlights
        """
        results = []
        
        for result in response.results:
            parsed = {
                "title": result.title,
                "url": result.url,
                "text": result.text if hasattr(result, 'text') else "",
                "published_date": result.published_date if hasattr(result, 'published_date') else None,
                "score": result.score if hasattr(result, 'score') else 0.0,
                "highlights": result.highlights if hasattr(result, 'highlights') else [],
                "author": result.author if hasattr(result, 'author') else None,
                "source": "exa",
                "mode": mode
            }
            results.append(parsed)
        
        return results
    
    def _mock_search_results(
        self,
        query: str,
        num_results: int,
        mode: str
    ) -> List[Dict]:
        """
        Generate mock search results for testing
        
        Returns deterministic results based on query
        """
        # Extract tickers from query
        import re
        tickers = re.findall(r'\b[A-Z]{2,5}\b', query.upper())
        ticker = tickers[0] if tickers else "MARKET"
        
        mock_results = []
        
        for i in range(num_results):
            result = {
                "title": f"{ticker} Shows Strong Performance - Analysis #{i+1}",
                "url": f"https://example.com/article-{ticker.lower()}-{i+1}",
                "text": f"Mock content for {ticker}. This is a detailed analysis of recent market movements and company performance. {mode.upper()} mode retrieval.",
                "published_date": (datetime.now() - timedelta(hours=i*6)).isoformat(),
                "score": 0.9 - (i * 0.1),
                "highlights": [
                    f"{ticker} earnings beat expectations",
                    f"Strong momentum in {ticker} stock",
                    f"Analysts upgrade {ticker} price target"
                ],
                "author": f"Mock Analyst {i+1}",
                "source": "exa-mock",
                "mode": mode
            }
            mock_results.append(result)
        
        return mock_results
    
    async def get_contents(self, urls: List[str]) -> List[Dict]:
        """
        Fetch full content for specific URLs
        
        Args:
            urls: List of URLs to fetch
        
        Returns:
            List of content dicts
        """
        if settings.use_mock_exa:
            logger.warning("🚨 MOCK MODE - Exa.ai content fetch not enabled")
            return [{"url": url, "text": f"Mock content for {url}"} for url in urls]
        
        try:
            response = self.client.get_contents(urls)
            return self._parse_results(response, "content")
        
        except Exception as e:
            logger.error(f"Error fetching contents: {e}")
            return []

# Global instance
exa_client = ExaClient()
