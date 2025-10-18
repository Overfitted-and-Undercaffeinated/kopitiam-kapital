"""Quick test script to verify Router Agent setup"""
import asyncio
import sys
import os

# Add apps/ai to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'ai'))

async def test_router():
    """Quick test of Router Agent"""
    try:
        from agents.router import RouterAgent
        from models.schemas import IntentType
        
        print("[OK] Imports successful!")
        
        # Initialize router
        router = RouterAgent()
        print(f"[OK] Router initialized with model: {router.model}")
        
        # Test classification
        test_queries = [
            "Should I buy AAPL?",
            "What's happening with tech stocks?",
            "Show my portfolio",
        ]
        
        print("\n" + "="*60)
        print("Testing Router Agent")
        print("="*60)
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            try:
                import time
                start = time.time()
                result = await router.classify_intent(query)
                latency = time.time() - start
                
                print(f"  Intent: {result.intent.value}")
                print(f"  Entities: {result.entities}")
                print(f"  Confidence: {result.confidence:.2f}")
                print(f"  Urgency: {result.urgency.value}")
                print(f"  Latency: {latency*1000:.0f}ms {'[OK]' if latency < 1.0 else '[WARN]'}")
                
            except Exception as e:
                print(f"  [ERROR] {e}")
        
        print("\n" + "="*60)
        print("[OK] All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_router())
    sys.exit(0 if success else 1)

