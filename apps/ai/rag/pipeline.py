"""
RAG pipeline orchestration
Combines Exa.ai, pgvector, and Mem0 for intelligent retrieval
"""
from typing import List, Dict, Optional
import logging
import asyncio
from datetime import datetime

# Flexible imports
try:
    from ..retrievers.exa_client import exa_client
    from ..retrievers.supabase_client import supabase_client
    from ..memory.mem0_service import mem0_service
    from ..rag.embeddings import embedding_service
    from ..rag.cache_strategy import cache_strategy
    from ..utils.config import settings
except ImportError:
    from retrievers.exa_client import exa_client
    from retrievers.supabase_client import supabase_client
    from memory.mem0_service import mem0_service
    from rag.embeddings import embedding_service
    from rag.cache_strategy import cache_strategy
    from utils.config import settings

logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    Orchestrates the full RAG (Retrieval-Augmented Generation) workflow
    
    Multi-source retrieval:
    1. Exa.ai - Latest financial news (REAL in MVP)
    2. Supabase pgvector - Cached research (MOCK in MVP)
    3. Mem0 - User context (STUB in MVP)
    
    Features:
    - Smart caching (4-hour TTL for news)
    - Source ranking and deduplication
    - Parallel retrieval for speed
    - Cost tracking for all API calls
    """
    
    def __init__(self):
        self.name = "rag_pipeline"
        logger.info("Initialized RAG Pipeline")
    
    async def retrieve_and_generate(
        self,
        query: str,
        user_id: str,
        task: str = "research",
        mode: str = "fast"
    ) -> Dict:
        """
        Execute full RAG pipeline
        
        Args:
            query: User query or research topic
            user_id: User ID for personalization
            task: Task type ("research", "recommendation", "brief")
            mode: Retrieval mode ("fast" or "deep")
        
        Returns:
            {
                "sources": List[Dict],  # Retrieved sources
                "context": str,  # Assembled context for LLM
                "user_policy": Dict,  # User's trading policy
                "metadata": Dict  # Retrieval metadata
            }
        """
        logger.info(f"RAG Pipeline: query='{query[:50]}...', task={task}, mode={mode}")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Check cache
            cached = await cache_strategy.get_cached_results(query, "news")
            if cached:
                logger.info("Using cached RAG results")
                return {
                    "sources": cached,
                    "context": self._assemble_context(cached),
                    "user_policy": await mem0_service.get_policy(user_id),
                    "metadata": {"cached": True, "latency_ms": 0}
                }
            
            # Step 2: Parallel retrieval from all sources
            logger.info("Retrieving from multiple sources in parallel...")
            
            exa_task = self._retrieve_from_exa(query, mode)
            vector_task = self._retrieve_from_vector(query, user_id)
            mem0_task = self._retrieve_from_mem0(user_id, query)
            
            # Wait for all retrievals
            exa_results, vector_results, mem0_context = await asyncio.gather(
                exa_task,
                vector_task,
                mem0_task,
                return_exceptions=True
            )
            
            # Handle exceptions in parallel tasks
            exa_results = exa_results if not isinstance(exa_results, Exception) else []
            vector_results = vector_results if not isinstance(vector_results, Exception) else []
            mem0_context = mem0_context if not isinstance(mem0_context, Exception) else {}
            
            logger.info(
                f"Retrieved: {len(exa_results)} from Exa, "
                f"{len(vector_results)} from vector DB, "
                f"Mem0 context: {bool(mem0_context.get('past_trades'))}"
            )
            
            # Step 3: Combine and rank sources
            all_sources = exa_results + vector_results
            ranked_sources = self._rank_sources(all_sources, query)
            
            # Step 4: Deduplicate by URL
            deduped_sources = self._deduplicate_sources(ranked_sources)
            
            # Limit to top 10
            top_sources = deduped_sources[:10]
            
            # Step 5: Assemble context
            context = self._assemble_context(top_sources, mem0_context)
            
            # Step 6: Cache results
            if top_sources:
                await cache_strategy.cache_results(query, "news", top_sources, user_id)
            
            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.info(f"RAG pipeline complete in {latency_ms:.0f}ms")
            
            return {
                "sources": top_sources,
                "context": context,
                "user_policy": await mem0_service.get_policy(user_id),
                "metadata": {
                    "cached": False,
                    "latency_ms": latency_ms,
                    "num_sources": len(top_sources),
                    "exa_count": len(exa_results),
                    "vector_count": len(vector_results),
                    "has_user_context": bool(mem0_context.get('past_trades'))
                }
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline error: {e}", exc_info=True)
            # Return minimal context
            return {
                "sources": [],
                "context": f"Query: {query}",
                "user_policy": await mem0_service.get_policy(user_id),
                "metadata": {"error": str(e)}
            }
    
    async def _retrieve_from_exa(self, query: str, mode: str) -> List[Dict]:
        """
        Retrieve from Exa.ai
        
        Args:
            query: Search query
            mode: "fast" or "deep"
        
        Returns:
            List of Exa search results
        """
        try:
            if mode == "deep":
                return await exa_client.search_deep(query, num_results=10)
            else:
                return await exa_client.search_fast(query, num_results=5)
        
        except Exception as e:
            logger.error(f"Exa retrieval failed: {e}")
            return []
    
    async def _retrieve_from_vector(self, query: str, user_id: str) -> List[Dict]:
        """
        Retrieve from Supabase pgvector
        
        🚨 MOCK: Returns empty list (pgvector not integrated)
        
        Args:
            query: Search query
            user_id: User ID
        
        Returns:
            List of similar cached documents
        """
        try:
            # Generate embedding for query
            embedding = await embedding_service.embed_text(query, user_id)
            
            # Vector similarity search
            results = await supabase_client.vector_search(
                embedding=embedding,
                table="notes",
                top_k=10,
                similarity_threshold=0.7
            )
            
            return results  # Will be empty list in MVP (mock)
        
        except Exception as e:
            logger.error(f"Vector retrieval failed: {e}")
            return []
    
    async def _retrieve_from_mem0(self, user_id: str, query: str) -> Dict:
        """
        Retrieve user context from Mem0
        
        🚨 STUB: Returns empty context
        
        Args:
            user_id: User ID
            query: Query context
        
        Returns:
            User context dict
        """
        try:
            context = await mem0_service.get_context(user_id, query)
            return context
        
        except Exception as e:
            logger.error(f"Mem0 retrieval failed: {e}")
            return {"past_trades": [], "win_rate": None, "preferences": {}}
    
    def _rank_sources(self, sources: List[Dict], query: str) -> List[Dict]:
        """
        Rank sources by relevance
        
        Ranking factors:
        1. Recency (newer = higher score)
        2. Relevance score (from Exa or similarity)
        3. Source quality (trusted domains)
        
        Args:
            sources: List of source dicts
            query: Original query
        
        Returns:
            Sorted list of sources
        """
        if not sources:
            return []
        
        try:
            # Add ranking score to each source
            for source in sources:
                score = 0.0
                
                # Factor 1: Relevance/similarity score (weight: 0.5)
                if 'score' in source:
                    score += source['score'] * 0.5
                
                # Factor 2: Recency (weight: 0.3)
                if 'published_date' in source and source['published_date']:
                    try:
                        pub_date = datetime.fromisoformat(source['published_date'].replace('Z', '+00:00'))
                        age_hours = (datetime.now() - pub_date.replace(tzinfo=None)).total_seconds() / 3600
                        
                        # Decay: 1.0 at 0 hours, 0.5 at 72 hours, 0.0 at 168 hours
                        recency_score = max(0, 1.0 - (age_hours / 168))
                        score += recency_score * 0.3
                    except:
                        pass
                
                # Factor 3: Source quality (weight: 0.2)
                trusted_domains = ['reuters.com', 'bloomberg.com', 'ft.com', 'wsj.com', 'sec.gov']
                url = source.get('url', '')
                if any(domain in url for domain in trusted_domains):
                    score += 0.2
                
                source['ranking_score'] = score
            
            # Sort by ranking score (descending)
            sorted_sources = sorted(sources, key=lambda x: x.get('ranking_score', 0), reverse=True)
            
            return sorted_sources
        
        except Exception as e:
            logger.error(f"Error ranking sources: {e}")
            return sources
    
    def _deduplicate_sources(self, sources: List[Dict]) -> List[Dict]:
        """
        Remove duplicate sources by URL
        
        Args:
            sources: List of sources
        
        Returns:
            Deduplicated list
        """
        seen_urls = set()
        deduped = []
        
        for source in sources:
            url = source.get('url', '')
            
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduped.append(source)
        
        logger.debug(f"Deduplicated {len(sources)} → {len(deduped)} sources")
        
        return deduped
    
    def _assemble_context(
        self,
        sources: List[Dict],
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Assemble context string for LLM from sources
        
        Args:
            sources: Retrieved sources
            user_context: Optional user context from Mem0
        
        Returns:
            Formatted context string
        """
        if not sources and not user_context:
            return "No additional context available."
        
        context_parts = []
        
        # Add user context if available
        if user_context and user_context.get('past_trades'):
            context_parts.append("## User Trading History")
            for trade in user_context['past_trades'][:3]:
                context_parts.append(
                    f"- {trade.get('symbol')}: {trade.get('outcome')} "
                    f"(P&L: ${trade.get('pnl', 0):.2f})"
                )
            context_parts.append("")
        
        # Add retrieved sources
        if sources:
            context_parts.append("## Retrieved Financial Intelligence")
            
            for i, source in enumerate(sources, 1):
                context_parts.append(f"\n### Source {i}: {source.get('title', 'Untitled')}")
                context_parts.append(f"URL: {source.get('url', 'N/A')}")
                
                if source.get('published_date'):
                    context_parts.append(f"Published: {source.get('published_date')}")
                
                # Add text content
                text = source.get('text', '')
                if text:
                    # Truncate to ~500 chars per source
                    truncated = text[:500] + "..." if len(text) > 500 else text
                    context_parts.append(f"\n{truncated}")
                
                # Add highlights if available
                if source.get('highlights'):
                    context_parts.append("\nKey Points:")
                    for highlight in source['highlights'][:3]:
                        context_parts.append(f"  - {highlight}")
        
        context = "\n".join(context_parts)
        
        logger.debug(f"Assembled context: {len(context)} characters from {len(sources)} sources")
        
        return context

# Global instance
rag_pipeline = RAGPipeline()


