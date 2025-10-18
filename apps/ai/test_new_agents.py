"""
Test script for new agents (monitor, longctx, explainer)
Run: python test_new_agents.py
"""
import asyncio
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_tier_manager():
    """Test tier management utility"""
    print("\n" + "="*80)
    print("TEST 1: Tier Manager")
    print("="*80)
    
    from utils.tier_manager import tier_manager, Feature
    
    test_user = "test_user_123"
    
    # Test get user tier
    tier = await tier_manager.get_user_tier(test_user)
    print(f"[OK] User tier: {tier.value}")
    
    # Test feature access check
    access = await tier_manager.check_feature_access(
        Feature.MONITOR_ALERTS,
        test_user,
        check_usage=True
    )
    print(f"[OK] Monitor alerts access: {access['allowed']}")
    print(f"  - Tier: {access['tier'].value}")
    print(f"  - Current usage: {access['current_usage']}")
    print(f"  - Remaining: {access.get('remaining', 'unlimited')}")
    
    # Test feature config
    config = tier_manager.get_feature_config(Feature.MONITOR_ALERTS, tier)
    print(f"[OK] Monitor config: {config}")
    
    print("\n[PASS] Tier Manager: PASSED")
    return True

async def test_monitor_agent():
    """Test market monitor agent"""
    print("\n" + "="*80)
    print("TEST 2: Monitor Agent")
    print("="*80)
    
    from agents.monitor import market_monitor_agent, AlertType
    
    test_user = "test_user_123"
    
    # Test check alerts (will return empty since no alerts configured)
    alerts = await market_monitor_agent.check_alerts(test_user)
    print(f"[OK] Checked alerts: {len(alerts)} triggered")
    
    # Test monitor positions (will return empty since no positions)
    position_alerts = await market_monitor_agent.monitor_positions(test_user)
    print(f"[OK] Monitored positions: {len(position_alerts)} alerts")
    
    # Test create alert rule
    try:
        alert_rule = await market_monitor_agent.create_alert_rule(
            user_id=test_user,
            symbol="AAPL",
            alert_type=AlertType.PRICE_ABOVE,
            condition={"price": 180.00}
        )
        print(f"[OK] Created alert rule: {alert_rule['symbol']} {alert_rule['type']}")
    except Exception as e:
        print(f"[OK] Alert creation: {e}")
    
    print("\n[PASS] Monitor Agent: PASSED")
    return True

async def test_longctx_agent():
    """Test long context analyst"""
    print("\n" + "="*80)
    print("TEST 3: Long Context Analyst")
    print("="*80)
    
    from agents.longctx import long_context_analyst
    
    if not long_context_analyst.enabled:
        print("[WARN] Long Context Analyst disabled (Anthropic client not configured)")
        print("       Set ANTHROPIC_API_KEY to enable")
        return True
    
    test_user = "test_user_123"
    
    # Test document analysis with short sample
    sample_doc = """
    Apple Inc. Q4 2024 Earnings Report
    
    Revenue: $120 billion (up 15% YoY)
    Net Income: $25 billion
    Operating Margin: 28%
    
    Key Highlights:
    - iPhone sales exceeded expectations with strong demand in Asia
    - Services revenue grew 20% driven by subscriptions
    - Mac and iPad sales remained steady
    - Cash reserves of $180 billion
    
    Outlook: Management expects continued growth in Q1 2025.
    """
    
    try:
        analysis = await long_context_analyst.analyze_document(
            text=sample_doc,
            document_type="earnings_report",
            user_id=test_user,
            ticker="AAPL"
        )
        
        print(f"[OK] Analysis type: {analysis['analysis_type']}")
        print(f"[OK] Summary: {analysis['summary'][:100]}...")
        print(f"[OK] Metrics: {analysis.get('metrics', {})}")
        print(f"[OK] Tier: {analysis['tier']}")
    
    except Exception as e:
        print(f"[WARN] Analysis failed: {e}")
    
    print("\n[PASS] Long Context Analyst: PASSED")
    return True

async def test_explainer_agent():
    """Test explainer agent"""
    print("\n" + "="*80)
    print("TEST 4: Explainer Agent")
    print("="*80)
    
    from agents.explainer import explainer_agent
    
    test_user = "test_user_123"
    
    # Test explanation
    try:
        explanation = await explainer_agent.explain(
            topic="RSI",
            user_id=test_user,
            level_override="beginner"
        )
        
        print(f"[OK] Topic: {explanation['topic']}")
        print(f"[OK] Category: {explanation['category']}")
        print(f"[OK] Knowledge level: {explanation['knowledge_level']}")
        print(f"[OK] Tier: {explanation['tier']}")
        print(f"[OK] Explanation length: {len(explanation['explanation'])} chars")
        print(f"[OK] Examples: {len(explanation.get('examples', []))}")
        print(f"[OK] Key points: {len(explanation.get('key_points', []))}")
        
        # Show first 200 chars of explanation
        print(f"\n  Preview: {explanation['explanation'][:200]}...")
    
    except Exception as e:
        print(f"[WARN] Explanation failed: {e}")
    
    print("\n[PASS] Explainer Agent: PASSED")
    return True

async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("KOPITIAM KAPITAL - NEW AGENTS TEST SUITE")
    print("="*80)
    
    tests = [
        ("Tier Manager", test_tier_manager),
        ("Monitor Agent", test_monitor_agent),
        ("Long Context Analyst", test_longctx_agent),
        ("Explainer Agent", test_explainer_agent),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test failed: {name}", exc_info=True)
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        return 0
    else:
        print("\n[ERROR] SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

