"""Quick local test of Router Agent"""
import asyncio
import time

async def main():
    """Test Router Agent locally"""
    print("="*60)
    print("Testing Router Agent")
    print("="*60 + "\n")
    
    # Import Router Agent
    from agents.router import RouterAgent
    from models.schemas import IntentType
    
    print("[OK] Imports successful!")
    
    # Initialize router
    router = RouterAgent()
    print(f"[OK] Router initialized with model: {router.model}\n")
    
    # Test queries
    test_queries = [
        "Should I buy AAPL?",
        "What's happening with tech stocks?",
        "Show my portfolio",
        "Alert me when TSLA hits $300",
        "What is RSI?",
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        try:
            start = time.time()
            result = await router.classify_intent(query)
            latency = time.time() - start
            
            print(f"  Intent: {result.intent.value}")
            print(f"  Entities: {result.entities}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Urgency: {result.urgency.value}")
            print(f"  Latency: {latency*1000:.0f}ms {'[OK]' if latency < 1.0 else '[WARN]'}")
            
            if result.reasoning:
                print(f"  Reasoning: {result.reasoning[:60]}...")
            
        except Exception as e:
            print(f"  [ERROR] {e}")
        
        print()
    
    print("="*60)
    print("[OK] All tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

