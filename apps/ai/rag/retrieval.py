"""Document retrieval service"""

class RetrievalService:
    """Retrieves relevant documents from vector store"""
    
    def __init__(self):
        pass
    
    async def retrieve(self, query_embedding: list[float], top_k: int = 10):
        """Retrieve top-k most relevant documents"""
        # TODO: Implement pgvector retrieval
        pass
    
    async def hybrid_retrieve(self, query: str, top_k: int = 10):
        """Hybrid retrieval combining semantic and keyword search"""
        # TODO: Implement hybrid retrieval
        pass

