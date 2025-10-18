"""RAG pipeline orchestration"""

class RAGPipeline:
    """Orchestrates the full RAG workflow"""
    
    def __init__(self):
        pass
    
    async def retrieve_and_generate(self, query: str, user_id: str):
        """Execute full RAG pipeline"""
        # TODO: Implement RAG pipeline
        # 1. Embed query
        # 2. Retrieve relevant documents (Exa + pgvector)
        # 3. Rerank results
        # 4. Generate response with LLM
        pass

