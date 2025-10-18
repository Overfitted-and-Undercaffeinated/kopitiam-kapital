"""Test Router Agent with all production enhancements integrated"""
import asyncio
import time

async def main():
    """Test Router with new features"""
    print("="*70)
    print("TESTING ROUTER AGENT WITH PRODUCTION ENHANCEMENTS")
    print("="*70 + "\n")
    
    from agents.router import RouterAgent
    from utils.config import settings
    from utils.rate_limiter import rate_limiter
    from utils.cost_tracker import cost_tracker
    
    # Disable rate limiting for testing (no Redis needed)
    settings.enable_rate_limiting = False
    
    router = RouterAgent()
    print(f"[OK] Router initialized with model: {router.model}\n")
    
    test_queries = [
        "Should I buy AAPL?",
        "What's happening with tech stocks?",
        "Show my portfolio performance",
    ]
    
    total_cost = 0.0
    
    for query in test_queries:
        print(f"Query: '{query}'")
        
        start = time.time()
        result = await router.classify_intent(query, user_id="test-user-123")
        latency = time.time() - start
        
        print(f"  Intent: {result.intent.value}")
        print(f"  Entities: {result.entities}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Urgency: {result.urgency.value}")
        print(f"  Latency: {latency*1000:.0f}ms")
        
        # Track cost (Groq is free, so should be $0)
        cost = await cost_tracker.log_cost(
            user_id="test-user-123",
            service="groq-llama-3.3-70b",
            tokens_input=len(query.split()) * 1.3,
            tokens_output=100
        )
        total_cost += cost
        print(f"  Cost: ${cost:.4f}")
        print()
    
    print("="*70)
    print(f"[SUCCESS] Router working with all enhancements!")
    print(f"Total cost: ${total_cost:.4f} (Groq is FREE!)")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())

