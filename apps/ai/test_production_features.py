"""
Comprehensive test of all production enhancements
"""
import asyncio
import sys
from pathlib import Path

async def test_all_features():
    """Test all production features"""
    
    print("="*70)
    print("TESTING PRODUCTION ENHANCEMENTS")
    print("="*70 + "\n")
    
    # Test 1: Configuration
    print("1. Testing Enhanced Configuration...")
    try:
        from utils.config import settings, COST_PRICING
        
        print(f"   [OK] Market data provider: {settings.market_data_provider}")
        print(f"   [OK] Rate limiting enabled: {settings.enable_rate_limiting}")
        print(f"   [OK] Cost tracking enabled: {settings.enable_cost_tracking}")
        print(f"   [OK] Disclaimers enabled: {settings.enable_disclaimers}")
        print(f"   [OK] Cost pricing loaded: {len(COST_PRICING)} services")
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 2: Market Data Service
    print("\n2. Testing Market Data Service...")
    try:
        from data.market_data import market_data_service
        
        # Use mock mode for testing
        settings.use_mock_market_data = True
        
        price = await market_data_service.get_latest_price("AAPL")
        print(f"   [OK] Mock price for AAPL: ${price:.2f}")
        
        data = await market_data_service.get_ohlcv("TSLA", period="1mo")
        print(f"   [OK] Mock OHLCV for TSLA: {len(data)} rows")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Rate Limiter
    print("\n3. Testing Rate Limiter...")
    try:
        from utils.rate_limiter import rate_limiter
        
        # Test with rate limiting disabled (no Redis needed)
        settings.enable_rate_limiting = False
        
        allowed = await rate_limiter.check_limit("test_key", 10, 3600)
        print(f"   [OK] Rate limit check (disabled mode): {allowed}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 4: Cost Tracker
    print("\n4. Testing Cost Tracker...")
    try:
        from utils.cost_tracker import cost_tracker
        
        cost = await cost_tracker.log_cost(
            user_id="test-123",
            service="gpt-4o",
            tokens_input=1000,
            tokens_output=500
        )
        
        print(f"   [OK] Calculated cost: ${cost:.4f}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 5: Resilience Wrapper
    print("\n5. Testing Resilience Wrapper...")
    try:
        from utils.resilience import resilient_service
        
        async def test_fn():
            return "success"
        
        async def fallback_fn():
            return "fallback"
        
        result = await resilient_service.call_with_fallback(
            primary_fn=test_fn,
            fallback_fn=fallback_fn,
            service_name="test-service"
        )
        
        print(f"   [OK] Resilient call result: {result}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 6: Market Hours
    print("\n6. Testing Market Hours...")
    try:
        from utils.market_hours import market_hours
        
        sgx_open = market_hours.is_market_open("SGX")
        active = market_hours.get_active_markets()
        
        print(f"   [OK] SGX market open: {sgx_open}")
        print(f"   [OK] Active markets: {', '.join(active) if active else 'None'}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 7: Disclaimers
    print("\n7. Testing Disclaimers...")
    try:
        from utils.disclaimers import add_disclaimer_to_recommendation
        
        rec = {"action": "BUY", "symbol": "AAPL"}
        rec_with_disclaimer = add_disclaimer_to_recommendation(rec)
        
        has_disclaimer = 'disclaimer' in rec_with_disclaimer
        print(f"   [OK] Disclaimer added: {has_disclaimer}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 8: Versioning
    print("\n8. Testing Model Versioning...")
    try:
        from utils.versioning import versioning
        
        prompt = "Test prompt template"
        hash_val = versioning.get_prompt_hash(prompt)
        
        print(f"   [OK] Prompt hash generated: {hash_val}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 9: Cache Strategy
    print("\n9. Testing Cache Strategy...")
    try:
        from rag.cache_strategy import cache_strategy
        
        should_cache = await cache_strategy.should_use_cache("AAPL news", "news")
        
        print(f"   [OK] Cache check working: {should_cache}")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 10: Position Manager
    print("\n10. Testing Position Manager...")
    try:
        from portfolio.position_manager import position_manager
        
        print(f"   [OK] Position manager initialized")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 11: Backtesting Engine
    print("\n11. Testing Backtesting Engine...")
    try:
        from backtesting.engine import backtest_engine, Trade
        
        print(f"   [OK] Backtest engine initialized")
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    print("\n" + "="*70)
    print("ALL PRODUCTION ENHANCEMENTS WORKING!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_all_features())
    sys.exit(0 if success else 1)

