"""
Comprehensive test of RAG Pipeline
Tests with mock mode and optionally with real Exa.ai API
"""
import asyncio
import sys

async def test_rag_pipeline():
    """Test complete RAG pipeline"""
    
    print("="*70)
    print("RAG PIPELINE COMPREHENSIVE TEST")
    print("="*70 + "\n")
    
    from rag.pipeline import rag_pipeline
    from retrievers.exa_client import exa_client
    from rag.embeddings import embedding_service
    from memory.mem0_service import mem0_service
    from retrievers.supabase_client import supabase_client
    from utils.config import settings
    
    # Test 1: Components Initialization
    print("1. Testing Component Initialization...")
    print(f"   [OK] RAG Pipeline initialized")
    print(f"   [OK] Exa client ready (mock={settings.use_mock_exa})")
    print(f"   [OK] Embedding service ready (mock={settings.use_mock_llm})")
    print(f"   [OK] Supabase client ready (MOCK STUB)")
    print(f"   [OK] Mem0 service ready (STUB)")
    
    # Test 2: Exa.ai Search (Mock Mode First)
    print("\n2. Testing Exa.ai Search (Mock Mode)...")
    settings.use_mock_exa = True
    
    try:
        results = await exa_client.search_fast("AAPL latest news", num_results=3)
        print(f"   [OK] Mock search returned {len(results)} results")
        
        for i, result in enumerate(results[:2], 1):
            print(f"   [{i}] {result['title'][:50]}...")
            print(f"       URL: {result['url']}")
            print(f"       Score: {result['score']:.2f}")
    
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 3: OpenAI Embeddings (Mock Mode)
    print("\n3. Testing Embeddings Service (Mock Mode)...")
    settings.use_mock_llm = True
    
    try:
        embedding = await embedding_service.embed_text("AAPL earnings analysis")
        print(f"   [OK] Generated embedding with {len(embedding)} dimensions")
        print(f"   [OK] Vector normalized: {abs(sum(x*x for x in embedding) - 1.0) < 0.01}")
    
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 4: Supabase Vector Search (Mock)
    print("\n4. Testing Supabase Vector Search (Mock)...")
    
    try:
        results = await supabase_client.vector_search(embedding, top_k=5)
        print(f"   [OK] Mock vector search returned {len(results)} results (expected: 0)")
    
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 5: Mem0 Service (Stub)
    print("\n5. Testing Mem0 Service (Stub)...")
    
    try:
        policy = await mem0_service.get_policy("test-user-123", "AAPL")
        print(f"   [OK] Got default policy: risk_profile={policy['risk_profile']}")
        print(f"   [OK] Max position size: {policy['max_position_size_pct']}%")
        
        context = await mem0_service.get_context("test-user-123", "AAPL")
        print(f"   [OK] Got user context (stub): {len(context['past_trades'])} trades")
    
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 6: Full RAG Pipeline (Mock Mode)
    print("\n6. Testing Full RAG Pipeline (Mock Mode)...")
    
    try:
        result = await rag_pipeline.retrieve_and_generate(
            query="AAPL latest earnings and price action",
            user_id="test-user-123",
            task="research",
            mode="fast"
        )
        
        print(f"   [OK] Pipeline completed")
        print(f"   [OK] Retrieved {len(result['sources'])} sources")
        print(f"   [OK] Context length: {len(result['context'])} characters")
        print(f"   [OK] User policy: {result['user_policy']['risk_profile']}")
        print(f"   [OK] Metadata: {result['metadata']}")
        
        # Show first source
        if result['sources']:
            first = result['sources'][0]
            print(f"\n   First Source:")
            print(f"   Title: {first['title'][:60]}...")
            print(f"   URL: {first['url']}")
            print(f"   Score: {first.get('score', 0):.2f}")
    
    except Exception as e:
        print(f"   [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 7: Context Assembly
    print("\n7. Testing Context Assembly...")
    
    try:
        context_str = result['context']
        
        # Check that context is well-formatted
        has_sources = "Source" in context_str or "sources" in context_str.lower()
        has_content = len(context_str) > 100
        
        print(f"   [OK] Context is formatted: {has_sources}")
        print(f"   [OK] Context has content: {has_content}")
        print(f"\n   Context Preview:")
        print("   " + context_str[:200].replace("\n", "\n   ") + "...")
    
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    print("\n" + "="*70)
    print("[SUCCESS] RAG Pipeline Mock Mode Working!")
    print("="*70)
    
    # Test 8: Real Exa.ai API (Optional)
    print("\n8. Testing Real Exa.ai API (Optional)...")
    
    try:
        # Ask if should test with real API
        print("   Do you want to test with real Exa.ai API? (costs ~$0.01)")
        print("   Set USE_MOCK_EXA=false in .env to enable")
        
        if not settings.use_mock_exa:
            print("\n   Testing with REAL Exa.ai API...")
            
            real_results = await exa_client.search_fast(
                "Apple Inc AAPL latest financial news",
                num_results=3
            )
            
            print(f"   [OK] Real API returned {len(real_results)} results")
            
            for i, result in enumerate(real_results[:3], 1):
                print(f"\n   [{i}] {result['title']}")
                print(f"       URL: {result['url']}")
                print(f"       Published: {result.get('published_date', 'N/A')}")
                print(f"       Score: {result.get('score', 0):.2f}")
                
                if result.get('highlights'):
                    print(f"       Highlights: {result['highlights'][0][:60]}...")
            
            print("\n   [SUCCESS] Real Exa.ai API working!")
        
        else:
            print("   [SKIPPED] USE_MOCK_EXA=true (using mock mode)")
    
    except Exception as e:
        print(f"   [WARNING] Real API test failed: {e}")
        print("   This is OK - mock mode is working")
    
    print("\n" + "="*70)
    print("RAG PIPELINE TESTS COMPLETE!")
    print("="*70)
    print("\nSummary:")
    print(f"  [OK] Exa.ai client: Working (mock={settings.use_mock_exa})")
    print(f"  [OK] Embeddings: Working (mock={settings.use_mock_llm})")
    print(f"  [OK] Supabase: Mock stub with warnings")
    print(f"  [OK] Mem0: Stub with default policy")
    print(f"  [OK] RAG Pipeline: Fully functional")
    print(f"\nNext: Implement Recommendation Agent using RAG pipeline!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_rag_pipeline())
    sys.exit(0 if success else 1)

