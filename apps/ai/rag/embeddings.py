"""
Embedding generation service using OpenAI
Model: text-embedding-3-large (3072 dimensions)
"""
from typing import List, Optional
import logging
import numpy as np

# Flexible imports
try:
    from ..utils.config import settings
    from ..utils.clients import get_openai_client
    from ..utils.cost_tracker import cost_tracker
except ImportError:
    from utils.config import settings
    from utils.clients import get_openai_client
    from utils.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Generates embeddings for text using OpenAI
    
    Features:
    - Model: text-embedding-3-large (3072 dimensions, best quality)
    - Batch support for efficiency
    - Cost tracking (~$0.00013/1K tokens)
    - Mock mode for testing
    """
    
    def __init__(self):
        self.model = "text-embedding-3-large"
        self.dimensions = 3072
        self.client = None
        
        if not settings.use_mock_llm:
            self.client = get_openai_client()
            logger.info(f"Initialized OpenAI embeddings with model: {self.model}")
    
    async def embed_text(self, text: str, user_id: Optional[str] = None) -> List[float]:
        """
        Generate embedding for single text
        
        Args:
            text: Text to embed
            user_id: Optional user ID for cost tracking
        
        Returns:
            3072-dimensional embedding vector
        """
        if settings.use_mock_llm:
            logger.warning("🚨 MOCK MODE - OpenAI embeddings not enabled, returning random vector")
            return self._mock_embedding()
        
        try:
            logger.debug(f"Embedding text: '{text[:50]}...'")
            
            # Call OpenAI embeddings API
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )
            
            embedding = response.data[0].embedding
            
            # Track cost
            if user_id:
                # Estimate tokens (roughly 1 token per 4 characters)
                tokens = len(text) // 4
                await cost_tracker.log_cost(
                    user_id=user_id,
                    service="openai-embedding",
                    tokens_input=tokens,
                    metadata={"model": self.model}
                )
            
            # Normalize to unit length
            normalized = self._normalize_embedding(embedding)
            
            logger.debug(f"Generated embedding with {len(normalized)} dimensions")
            return normalized
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Fallback to mock
            logger.warning("Falling back to mock embedding")
            return self._mock_embedding()
    
    async def embed_batch(
        self,
        texts: List[str],
        user_id: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for batch of texts (more efficient)
        
        Args:
            texts: List of texts to embed
            user_id: Optional user ID for cost tracking
        
        Returns:
            List of embedding vectors
        """
        if settings.use_mock_llm:
            logger.warning(f"🚨 MOCK MODE - Generating {len(texts)} mock embeddings")
            return [self._mock_embedding() for _ in texts]
        
        try:
            logger.info(f"Batch embedding {len(texts)} texts")
            
            # Call OpenAI embeddings API (batch)
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.dimensions
            )
            
            embeddings = [data.embedding for data in response.data]
            
            # Track cost
            if user_id:
                total_tokens = sum(len(text) // 4 for text in texts)
                await cost_tracker.log_cost(
                    user_id=user_id,
                    service="openai-embedding",
                    tokens_input=total_tokens,
                    metadata={"model": self.model, "batch_size": len(texts)}
                )
            
            # Normalize all embeddings
            normalized = [self._normalize_embedding(emb) for emb in embeddings]
            
            logger.info(f"Generated {len(normalized)} batch embeddings")
            return normalized
            
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            # Fallback to mock
            logger.warning(f"Falling back to {len(texts)} mock embeddings")
            return [self._mock_embedding() for _ in texts]
    
    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        Normalize embedding to unit length (for cosine similarity)
        
        Args:
            embedding: Raw embedding vector
        
        Returns:
            Normalized embedding
        """
        vec = np.array(embedding)
        norm = np.linalg.norm(vec)
        
        if norm == 0:
            return embedding
        
        normalized = vec / norm
        return normalized.tolist()
    
    def _mock_embedding(self) -> List[float]:
        """
        Generate mock embedding for testing
        
        Returns:
            Random 3072-dimensional vector
        """
        # Use deterministic seed for consistent testing
        np.random.seed(42)
        vec = np.random.randn(self.dimensions)
        
        # Normalize to unit length
        vec = vec / np.linalg.norm(vec)
        
        return vec.tolist()

# Global instance
embedding_service = EmbeddingService()


