"""Embedding generation service"""

class EmbeddingService:
    """Generates embeddings for text using OpenAI or similar"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def embed_text(self, text: str):
        """Generate embedding for text"""
        # TODO: Implement using OpenAI embeddings
        pass
    
    async def embed_batch(self, texts: list[str]):
        """Generate embeddings for batch of texts"""
        # TODO: Implement batch embedding
        pass

