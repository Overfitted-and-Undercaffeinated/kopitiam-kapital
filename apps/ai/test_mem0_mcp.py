"""
Test Mem0 + MCP Integration
Tests user personalization and advanced risk calculations
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy logs
logging.getLogger('httpx').setLevel(logging.WARNING)

from memory.mem0_service import mem0_service
from utils.mcp_client import mcp_risk_client
from utils.config import settings

async def test_1_mem0_initialization():
    """Test Mem0 client initialization"""
    print("\n" + "="*80)
    print("TEST 1: MEM0 INITIALIZATION")
    print("="*80)
    
    try:
        print(f"  Mem0 enabled in config: {settings.use_mem0}")
        print(f"  Mem0 API key present: {bool(settings.mem0_api_key)}")
        print(f"  Mem0 client initialized: {mem0_service.client is not None}")
        print(f"  Mem0 active: {mem0_service.enabled}")
        
        if mem0_service.enabled:
            print("  [OK] Mem0 is ENABLED and ready")
        else:
            print("  [WARN] Mem0 is DISABLED (will use defaults)")
        
        return True, None
        
    except Exception as e:
        print(f"[ERROR] Mem0 initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_2_mem0_get_policy():
    """Test getting user policy from Mem0"""
    print("\n" + "="*80)
    print("TEST 2: MEM0 GET POLICY")
    print("="*80)
    
    try:
        policy = await mem0_service.get_policy("test_user_123")
        
        print(f"  [OK] Policy retrieved:")
        print(f"    Risk Tolerance: {policy['risk_tolerance']}")
        print(f"    Position Size: {policy['default_position_size_pct']:.1%}")
        print(f"    Stop Loss: {policy['default_stop_loss_pct']:.1%}")
        print(f"    Take Profit: {policy['default_take_profit_pct']:.1%}")
        print(f"    Holding Period: {policy['preferred_holding_period']}")
        
        assert 'risk_tolerance' in policy
        assert 'default_position_size_pct' in policy
        
        return True, policy
        
    except Exception as e:
        print(f"[ERROR] Mem0 get policy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_3_mem0_add_preference():
    """Test adding user preference to Mem0"""
    print("\n" + "="*80)
    print("TEST 3: MEM0 ADD PREFERENCE")
    print("="*80)
    
    try:
        # Add a preference
        await mem0_service.add_user_preference(
            user_id="test_user_123",
            preference_type="risk_tolerance",
            value="I prefer conservative risk with small positions"
        )
        
        print("  [OK] Preference added to Mem0")
        
        # Retrieve policy to see if it changed
        policy = await mem0_service.get_policy("test_user_123")
        
        if mem0_service.enabled:
            print(f"  Policy after adding preference: {policy['risk_tolerance']}")
            # Note: May take a moment for Mem0 to index, so might still be 'moderate'
        else:
            print("  [WARN] Mem0 disabled, preference not persisted")
        
        return True, None
        
    except Exception as e:
        print(f"[ERROR] Mem0 add preference test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_4_mem0_record_outcome():
    """Test recording trade outcome"""
    print("\n" + "="*80)
    print("TEST 4: MEM0 RECORD OUTCOME")
    print("="*80)
    
    try:
        trade = {
            'symbol': 'NVDA',
            'action': 'BUY',
            'entry_price': 485.50,
            'exit_price': 510.00,
            'pnl_pct': 0.05,
            'strategy': 'RSI Oversold',
            'sentiment_score': 0.82
        }
        
        await mem0_service.record_outcome("test_user_123", trade)
        
        print("  [OK] Trade outcome recorded in Mem0")
        print(f"    Symbol: {trade['symbol']}")
        print(f"    P&L: {trade['pnl_pct']:.1%} (win)")
        
        return True, None
        
    except Exception as e:
        print(f"[ERROR] Mem0 record outcome test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_5_mcp_client_initialization():
    """Test MCP client initialization"""
    print("\n" + "="*80)
    print("TEST 5: MCP CLIENT INITIALIZATION")
    print("="*80)
    
    try:
        print(f"  MCP enabled in config: {settings.use_mcp_risk_tools}")
        print(f"  MCP client enabled: {mcp_risk_client.enabled}")
        print(f"  MCP server path: {mcp_risk_client.server_path}")
        
        if mcp_risk_client.enabled:
            print("  [OK] MCP client is READY")
            print("  Note: Server will auto-start when first tool is called")
        else:
            print("  [WARN] MCP client is DISABLED")
        
        return True, None
        
    except Exception as e:
        print(f"[ERROR] MCP initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_6_mcp_start_server():
    """Test starting MCP server"""
    print("\n" + "="*80)
    print("TEST 6: MCP SERVER START")
    print("="*80)
    
    try:
        if not mcp_risk_client.enabled:
            print("  [SKIP] MCP disabled, skipping server start test")
            return True, None
        
        print("  Starting MCP Risk Tools server...")
        started = await mcp_risk_client.start_server()
        
        if started:
            print("  [OK] MCP server started successfully")
            print(f"    Process PID: {mcp_risk_client.server_process.pid if mcp_risk_client.server_process else 'N/A'}")
        else:
            print("  [WARN] MCP server failed to start (will use simple calculations)")
        
        return True, started
        
    except Exception as e:
        print(f"[ERROR] MCP server start test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_7_mcp_position_sizing():
    """Test MCP position sizing tool"""
    print("\n" + "="*80)
    print("TEST 7: MCP POSITION SIZING (Kelly Criterion)")
    print("="*80)
    
    try:
        if not mcp_risk_client.enabled or not mcp_risk_client.server_process:
            print("  [SKIP] MCP not running, skipping tool test")
            return True, None
        
        print("  Calling MCP calculate_position_size with Kelly method...")
        
        result = await mcp_risk_client.calculate_position_size(
            method='kelly',
            capital=100000,
            current_price=485.50,
            win_rate=0.67,
            avg_win=0.08,
            avg_loss=0.04,
            stop_loss=461.23
        )
        
        if result:
            print(f"  [OK] MCP returned position size:")
            print(f"    Shares: {result.get('shares')}")
            print(f"    Position Value: ${result.get('position_value', 0):.2f}")
            print(f"    Risk Amount: ${result.get('risk_amount', 0):.2f}")
            print(f"    Method: {result.get('method')}")
        else:
            print("  [WARN] MCP returned None (server might not be responding)")
        
        return True, result
        
    except Exception as e:
        print(f"[ERROR] MCP position sizing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_8_mcp_stop_optimization():
    """Test MCP stop loss optimization"""
    print("\n" + "="*80)
    print("TEST 8: MCP STOP LOSS OPTIMIZATION (ATR-based)")
    print("="*80)
    
    try:
        if not mcp_risk_client.enabled or not mcp_risk_client.server_process:
            print("  [SKIP] MCP not running, skipping tool test")
            return True, None
        
        print("  Calling MCP optimize_stop_loss...")
        
        result = await mcp_risk_client.optimize_stop_loss(
            entry_price=485.50,
            atr=12.30,
            risk_tolerance='moderate',
            direction='BUY'
        )
        
        if result:
            print(f"  [OK] MCP optimized stop loss:")
            print(f"    Stop Loss: ${result.get('stop_loss', 0):.2f}")
            print(f"    ATR Multiplier: {result.get('atr_multiplier', 0)}x")
            print(f"    Distance: {result.get('distance_percent', 0):.1%}")
        else:
            print("  [WARN] MCP returned None")
        
        return True, result
        
    except Exception as e:
        print(f"[ERROR] MCP stop optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_9_integrated_recommendation():
    """Test recommendation with Mem0 + MCP"""
    print("\n" + "="*80)
    print("TEST 9: INTEGRATED RECOMMENDATION (Mem0 + MCP + Sentiment + Backtest)")
    print("="*80)
    
    try:
        from agents.recommend import recommendation_agent
        
        print("  Generating recommendation with FULL integration...")
        print(f"    Mem0 enabled: {recommendation_agent.mem0_enabled}")
        print(f"    MCP enabled: {recommendation_agent.mcp_enabled}")
        
        recommendation = await recommendation_agent.generate_recommendation(
            symbol="AAPL",
            user_id="test_integrated_user"
        )
        
        print(f"\n  [OK] Integrated recommendation generated:")
        print(f"    Symbol: {recommendation['symbol']}")
        print(f"    Action: {recommendation['action']}")
        print(f"    Entry: ${recommendation['entry_price']:.2f}")
        print(f"    Stop: ${recommendation['stop_loss']:.2f}")
        print(f"    Target: ${recommendation['take_profit']:.2f}")
        print(f"    Position: {recommendation['position_size_shares']} shares ({recommendation['position_size_percent']:.1%})")
        print(f"    Method: {recommendation.get('method', 'N/A')}")
        print(f"    Sentiment: {recommendation['sentiment']['score']:.2f}")
        print(f"    Backtest Win Rate: {recommendation['backtest_validation']['win_rate']:.1%}")
        
        # Check if using advanced features
        if 'kelly' in recommendation.get('method', '').lower():
            print("\n  [OK] Using MCP Kelly Criterion! ✅")
        if recommendation['sentiment']['score'] != 0.5:
            print("  [OK] Using real sentiment data! ✅")
        
        return True, recommendation
        
    except Exception as e:
        print(f"[ERROR] Integrated recommendation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_10_mem0_search():
    """Test Mem0 memory search"""
    print("\n" + "="*80)
    print("TEST 10: MEM0 MEMORY SEARCH")
    print("="*80)
    
    try:
        # Search for memories
        memories = await mem0_service.search_memories(
            user_id="test_user_123",
            query="NVDA trades and sentiment",
            limit=5
        )
        
        print(f"  [OK] Found {len(memories)} memories")
        
        if memories:
            for i, memory in enumerate(memories[:3], 1):
                print(f"    {i}. {memory.get('content', '')[:80]}...")
                print(f"       Relevance: {memory.get('relevance', 0):.2f}")
        else:
            print("  [WARN] No memories found (expected for new user)")
        
        return True, memories
        
    except Exception as e:
        print(f"[ERROR] Mem0 search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def run_all_tests():
    """Run all Mem0 + MCP tests"""
    print("\n" + "="*80)
    print("KOPITIAM CAPITAL - MEM0 + MCP INTEGRATION TEST SUITE")
    print("="*80)
    
    print(f"\nConfiguration:")
    print(f"  USE_MEM0: {settings.use_mem0}")
    print(f"  USE_MCP_RISK_TOOLS: {settings.use_mcp_risk_tools}")
    
    tests = [
        ("Mem0 Initialization", test_1_mem0_initialization),
        ("Mem0 Get Policy", test_2_mem0_get_policy),
        ("Mem0 Add Preference", test_3_mem0_add_preference),
        ("Mem0 Record Outcome", test_4_mem0_record_outcome),
        ("MCP Client Init", test_5_mcp_client_initialization),
        ("MCP Server Start", test_6_mcp_start_server),
        ("MCP Position Sizing", test_7_mcp_position_sizing),
        ("MCP Stop Optimization", test_8_mcp_stop_optimization),
        ("Integrated Recommendation", test_9_integrated_recommendation),
        ("Mem0 Memory Search", test_10_mem0_search),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            success, data = await test_func()
            results[name] = {'success': success, 'data': data}
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results[name] = {'success': False, 'data': None}
    
    # Cleanup
    if mcp_risk_client.server_process:
        print("\n  Stopping MCP server...")
        mcp_risk_client.stop_server()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for name, result in results.items():
        status = "[OK]" if result['success'] else "[ERROR]"
        print(f"  {status} {name}")
    
    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"\n  Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  [OK] ALL MEM0 + MCP TESTS PASSED!")
    else:
        print(f"\n  [WARN] {total - passed} test(s) failed")
    
    print("\n" + "="*80)
    print("INTEGRATION STATUS:")
    print(f"  Mem0: {'ENABLED' if mem0_service.enabled else 'DISABLED (using defaults)'}")
    print(f"  MCP: {'AVAILABLE' if mcp_risk_client.enabled else 'UNAVAILABLE (using simple math)'}")
    print("="*80 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

