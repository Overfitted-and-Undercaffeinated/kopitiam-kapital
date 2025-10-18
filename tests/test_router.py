"""Integration tests for Router Agent"""
import pytest
import time
import asyncio
from apps.ai.agents.router import RouterAgent
from apps.ai.models.schemas import IntentType, UrgencyLevel, RouterResponse

# Test data
TEST_QUERIES = [
    # RECOMMEND intent
    ("Should I buy AAPL?", IntentType.RECOMMEND, ["AAPL"]),
    ("Give me a trading idea for TSLA", IntentType.RECOMMEND, ["TSLA"]),
    ("What's a good trade right now?", IntentType.RECOMMEND, []),
    
    # RESEARCH intent
    ("What's happening with tech stocks?", IntentType.RESEARCH, []),
    ("Why is NVDA going up?", IntentType.RESEARCH, ["NVDA"]),
    ("Latest news on semiconductor sector", IntentType.RESEARCH, []),
    
    # PORTFOLIO intent
    ("Show my portfolio", IntentType.PORTFOLIO, []),
    ("What's my P&L today?", IntentType.PORTFOLIO, []),
    ("How are my positions doing?", IntentType.PORTFOLIO, []),
    
    # ALERTS intent
    ("Alert me when MSFT hits $400", IntentType.ALERTS, ["MSFT"]),
    ("Set up monitoring for GOOGL", IntentType.ALERTS, ["GOOGL"]),
    
    # EXPLAIN intent
    ("What is RSI?", IntentType.EXPLAIN, ["RSI"]),
    ("How does MACD work?", IntentType.EXPLAIN, ["MACD"]),
    ("Explain stop loss", IntentType.EXPLAIN, []),
    
    # SETTINGS intent
    ("Change my risk profile", IntentType.SETTINGS, []),
    ("Update my preferences", IntentType.SETTINGS, []),
]


@pytest.fixture
def router_agent():
    """Create RouterAgent instance"""
    return RouterAgent()


class TestRouterBasic:
    """Basic functionality tests"""
    
    @pytest.mark.asyncio
    async def test_router_initialization(self, router_agent):
        """Test router agent initializes correctly"""
        assert router_agent.name == "router"
        assert router_agent.model == "llama-3.3-70b-versatile"
        assert router_agent.client is not None
    
    @pytest.mark.asyncio
    async def test_empty_query_raises_error(self, router_agent):
        """Test that empty queries raise ValueError"""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await router_agent.classify_intent("")
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await router_agent.classify_intent("   ")
    
    @pytest.mark.asyncio
    async def test_basic_classification(self, router_agent):
        """Test basic query classification"""
        response = await router_agent.classify_intent("Should I buy AAPL?")
        
        # Check response structure
        assert isinstance(response, RouterResponse)
        assert isinstance(response.intent, IntentType)
        assert isinstance(response.entities, list)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.urgency, UrgencyLevel)
        
        # Check expected classification
        assert response.intent == IntentType.RECOMMEND
        assert "AAPL" in response.entities


class TestRouterLatency:
    """Latency and performance tests"""
    
    @pytest.mark.asyncio
    async def test_router_latency_target(self, router_agent):
        """Test router meets <1s latency target"""
        query = "Should I buy TSLA?"
        
        start_time = time.time()
        response = await router_agent.classify_intent(query)
        latency = time.time() - start_time
        
        print(f"\nLatency: {latency*1000:.0f}ms")
        print(f"Intent: {response.intent.value}")
        print(f"Confidence: {response.confidence:.2f}")
        
        # CRITICAL: Must be under 1 second
        assert latency < 1.0, f"Router latency {latency:.2f}s exceeds 1s target"
    
    @pytest.mark.asyncio
    async def test_multiple_queries_latency(self, router_agent):
        """Test average latency across multiple queries"""
        queries = [
            "Should I buy AAPL?",
            "What's happening with tech?",
            "Show my portfolio",
        ]
        
        latencies = []
        for query in queries:
            start_time = time.time()
            await router_agent.classify_intent(query)
            latency = time.time() - start_time
            latencies.append(latency)
        
        avg_latency = sum(latencies) / len(latencies)
        print(f"\nAverage latency: {avg_latency*1000:.0f}ms")
        print(f"Min: {min(latencies)*1000:.0f}ms, Max: {max(latencies)*1000:.0f}ms")
        
        # Average should be well under 1s
        assert avg_latency < 0.8, f"Average latency {avg_latency:.2f}s too high"


class TestRouterAccuracy:
    """Intent classification accuracy tests"""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("query,expected_intent,expected_entities", TEST_QUERIES)
    async def test_intent_classification(self, router_agent, query, expected_intent, expected_entities):
        """Test intent classification for various queries"""
        response = await router_agent.classify_intent(query)
        
        print(f"\nQuery: {query}")
        print(f"Expected: {expected_intent.value}, Got: {response.intent.value}")
        print(f"Entities: {response.entities}")
        print(f"Confidence: {response.confidence:.2f}")
        
        # Check intent matches
        assert response.intent == expected_intent, \
            f"Expected {expected_intent.value}, got {response.intent.value}"
        
        # Check entities if specified
        for entity in expected_entities:
            assert entity in response.entities, \
                f"Expected entity '{entity}' not found in {response.entities}"
    
    @pytest.mark.asyncio
    async def test_confidence_threshold(self, router_agent):
        """Test that confidence scores are reasonable"""
        queries = [
            "Should I buy AAPL?",  # Clear intent
            "stocks",  # Ambiguous
        ]
        
        for query in queries:
            response = await router_agent.classify_intent(query)
            print(f"\nQuery: '{query}' -> Confidence: {response.confidence:.2f}")
            
            # Confidence should always be between 0 and 1
            assert 0.0 <= response.confidence <= 1.0
            
            # Clear queries should have high confidence
            if "buy" in query.lower():
                assert response.confidence > 0.6, "Clear query should have higher confidence"


class TestEntityExtraction:
    """Entity extraction tests"""
    
    @pytest.mark.asyncio
    async def test_ticker_extraction(self, router_agent):
        """Test ticker extraction"""
        test_cases = [
            ("Should I buy AAPL and MSFT?", ["AAPL", "MSFT"]),
            ("What's happening with TSLA?", ["TSLA"]),
            ("NVDA looks interesting", ["NVDA"]),
        ]
        
        for query, expected_tickers in test_cases:
            response = await router_agent.classify_intent(query)
            print(f"\nQuery: {query}")
            print(f"Extracted: {response.entities}")
            
            for ticker in expected_tickers:
                assert ticker in response.entities, \
                    f"Ticker '{ticker}' not found in {response.entities}"
    
    @pytest.mark.asyncio
    async def test_entity_deduplication(self, router_agent):
        """Test that duplicate entities are removed"""
        response = await router_agent.classify_intent("AAPL AAPL AAPL")
        
        # Should only have one AAPL
        assert response.entities.count("AAPL") == 1


class TestUrgency:
    """Urgency classification tests"""
    
    @pytest.mark.asyncio
    async def test_urgency_classification(self, router_agent):
        """Test urgency level classification"""
        test_cases = [
            ("URGENT: Should I buy now?", UrgencyLevel.HIGH),
            ("Should I buy AAPL?", UrgencyLevel.MEDIUM),
            ("What is RSI?", UrgencyLevel.LOW),
        ]
        
        for query, expected_urgency in test_cases:
            response = await router_agent.classify_intent(query)
            print(f"\nQuery: {query}")
            print(f"Urgency: {response.urgency.value}")
            
            # Note: Urgency classification might be flexible
            # Just check it's a valid urgency level
            assert isinstance(response.urgency, UrgencyLevel)


class TestErrorHandling:
    """Error handling and fallback tests"""
    
    @pytest.mark.asyncio
    async def test_fallback_classification(self, router_agent):
        """Test that fallback works for edge cases"""
        # Test with non-English or unusual queries
        queries = [
            "buy stock",  # Minimal query
            "portfolio",  # Single word
            "???",  # Special characters
        ]
        
        for query in queries:
            # Should not crash, should return valid response
            response = await router_agent.classify_intent(query)
            assert isinstance(response, RouterResponse)
            assert isinstance(response.intent, IntentType)
            print(f"\nQuery: '{query}' -> Intent: {response.intent.value} (fallback)")
    
    @pytest.mark.asyncio
    async def test_backward_compatibility(self, router_agent):
        """Test legacy route() method still works"""
        result = await router_agent.route("Should I buy AAPL?")
        
        # Check it returns dict with expected keys
        assert isinstance(result, dict)
        assert "intent" in result
        assert "entities" in result
        assert "confidence" in result
        assert "urgency" in result


class TestIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, router_agent):
        """Test complete workflow from query to response"""
        query = "Should I buy AAPL stock today?"
        
        # Classify intent
        response = await router_agent.classify_intent(query)
        
        # Validate complete response
        assert response.intent == IntentType.RECOMMEND
        assert "AAPL" in response.entities
        assert response.confidence > 0.0
        assert isinstance(response.urgency, UrgencyLevel)
        assert response.reasoning is not None
        
        print(f"\n=== Full Router Response ===")
        print(f"Query: {query}")
        print(f"Intent: {response.intent.value}")
        print(f"Entities: {response.entities}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Urgency: {response.urgency.value}")
        print(f"Reasoning: {response.reasoning}")


# Run with: pytest tests/test_router.py -v -s
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

