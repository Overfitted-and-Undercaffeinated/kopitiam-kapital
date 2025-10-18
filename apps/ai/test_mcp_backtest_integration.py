"""
Test MCP Integration with Enhanced Backtesting
Verifies all 5 MCP enhancements work correctly
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_1_mcp_server_startup():
    """Test MCP server can start successfully"""
    from utils.mcp_client import mcp_risk_client
    
    print("\n[1/8] Testing MCP server startup...")
    
    if not mcp_risk_client.enabled:
        await mcp_risk_client.start_server()
    
    assert mcp_risk_client.enabled, "MCP server failed to start"
    assert mcp_risk_client.server_process is not None, "MCP server process is None"
    print("✅ MCP server started successfully")

async def test_2_mcp_var_calculation():
    """Test MCP VaR calculation"""
    from utils.mcp_client import mcp_risk_client
    
    print("\n[2/8] Testing MCP VaR calculation...")
    
    returns = [-0.05, -0.02, 0.03, -0.08, 0.05, 0.02, -0.03]
    
    var_result = await mcp_risk_client.call_tool(
        'calculate_var',
        {
            'returns': returns,
            'position_value': 100000,
            'confidence_level': 0.95
        }
    )
    
    assert var_result is not None, "VaR result is None"
    assert 'var_percent' in var_result, "var_percent missing"
    assert 'var_amount' in var_result, "var_amount missing"
    assert 'worst_case_loss' in var_result, "worst_case_loss missing"
    assert var_result['var_percent'] < 0, "VaR should be negative"
    print(f"✅ VaR: {var_result['var_percent']:.2%}, Amount: ${var_result['var_amount']:,.2f}, Worst case: ${var_result['worst_case_loss']:,.2f}")

async def test_3_mcp_position_sizing():
    """Test MCP Kelly Criterion position sizing"""
    from utils.mcp_client import mcp_risk_client
    
    print("\n[3/8] Testing MCP position sizing (Kelly Criterion)...")
    
    position = await mcp_risk_client.calculate_position_size(
        method='kelly',
        capital=100000,
        current_price=485.50,
        win_rate=0.67,
        avg_win=0.08,
        avg_loss=0.04
    )
    
    assert position is not None, "Position result is None"
    assert position['shares'] > 0, "Shares should be positive"
    assert position['method'] == 'kelly', "Method should be kelly"
    assert 'position_value' in position, "position_value missing"
    assert 'risk_amount' in position, "risk_amount missing"
    print(f"✅ Position: {position['shares']} shares, Value: ${position['position_value']:,.2f}, Risk: ${position['risk_amount']:,.2f}")

async def test_4_mcp_stop_optimization():
    """Test MCP ATR-based stop optimization"""
    from utils.mcp_client import mcp_risk_client
    
    print("\n[4/8] Testing MCP stop loss optimization (ATR-based)...")
    
    stop_result = await mcp_risk_client.optimize_stop_loss(
        entry_price=485.50,
        atr=12.30,
        risk_tolerance='moderate',
        direction='BUY'
    )
    
    assert stop_result is not None, "Stop result is None"
    assert stop_result['stop_loss'] < 485.50, "Stop loss should be below entry"
    assert stop_result['atr_multiplier'] == 2.0, "ATR multiplier should be 2.0 for moderate"
    assert 'distance_percent' in stop_result, "distance_percent missing"
    print(f"✅ Stop: ${stop_result['stop_loss']:.2f} ({stop_result['atr_multiplier']}x ATR, {stop_result['distance_percent']:.2%} distance)")

async def test_5_mcp_risk_reward():
    """Test MCP risk/reward calculation"""
    from utils.mcp_client import mcp_risk_client
    
    print("\n[5/8] Testing MCP risk/reward analysis...")
    
    rr_result = await mcp_risk_client.calculate_risk_reward(
        entry_price=485.50,
        stop_loss=461.23,
        take_profit=534.05,
        win_rate=0.67,
        position_size=50
    )
    
    assert rr_result is not None, "Risk/reward result is None"
    assert rr_result['risk_reward_ratio'] > 0, "R:R ratio should be positive"
    assert 'expected_value' in rr_result, "expected_value missing"
    assert 'recommendation' in rr_result, "recommendation missing"
    print(f"✅ R:R: {rr_result['risk_reward_ratio']}, EV: ${rr_result['expected_value']:.2f}")
    print(f"   Assessment: {rr_result['recommendation']}")

async def test_6_capabilities_endpoint():
    """Test system capabilities endpoint"""
    from fastapi.testclient import TestClient
    from main import app
    
    print("\n[6/8] Testing capabilities endpoint...")
    
    client = TestClient(app)
    response = client.get("/system/capabilities")
    
    assert response.status_code == 200, f"Status code is {response.status_code}"
    data = response.json()
    
    assert 'mcp_risk_tools' in data, "mcp_risk_tools missing"
    assert data['mcp_risk_tools']['enabled'] == True, "MCP should be enabled"
    assert data['mcp_risk_tools']['status'] == 'operational', "MCP status should be operational"
    assert len(data['mcp_risk_tools']['features']) >= 4, "Should have at least 4 features"
    
    print("✅ Capabilities endpoint working")
    print(f"   MCP Status: {data['mcp_risk_tools']['status']}")
    print(f"   Features: {len(data['mcp_risk_tools']['features'])}")

async def test_7_full_backtest_with_mcp():
    """Test complete backtest flow with all MCP features"""
    print("\n[7/8] Testing full backtest with MCP integration...")
    print("   (This may take 10-15 seconds...)")
    
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    response = client.post("/backtest/run", json={
        "symbol": "AAPL",
        "natural_language_strategy": "buy when RSI is below 30",
        "include_visuals": True,
        "include_voice": False  # Skip voice for faster test
    })
    
    assert response.status_code == 200, f"Status code is {response.status_code}, Error: {response.json() if response.status_code != 200 else ''}"
    data = response.json()
    
    # Verify structure
    assert 'metrics' in data, "metrics missing"
    assert 'explanation' in data, "explanation missing"
    assert 'strategy' in data, "strategy missing"
    
    # Verify MCP-powered metrics
    metrics = data['metrics']
    assert metrics.get('mcp_powered') == True, "Should be MCP powered"
    assert 'var_95' in metrics, "var_95 missing"
    assert 'var_amount' in metrics, "var_amount missing"
    assert 'worst_case_loss' in metrics, "worst_case_loss missing"
    
    # Verify position sizing recommendation
    if metrics.get('win_rate', 0) > 0:
        assert 'recommended_position' in metrics, "recommended_position missing"
        rec_pos = metrics['recommended_position']
        assert 'shares' in rec_pos, "shares missing in recommended_position"
        assert 'method' in rec_pos, "method missing"
        assert rec_pos['method'] == 'kelly_criterion', "method should be kelly_criterion"
        
        print("✅ Full backtest with MCP integration complete")
        print(f"   VaR: {metrics['var_95']:.2%}")
        print(f"   Worst case loss: ${metrics['worst_case_loss']:,.2f}")
        print(f"   Recommended position: {rec_pos['shares']} shares (${rec_pos['position_value']:,.2f})")
    else:
        print("✅ Full backtest complete (no position recommendation due to 0% win rate)")

async def test_8_mcp_failure_handling():
    """Test that errors are raised when MCP fails"""
    from utils.mcp_client import mcp_risk_client
    from fastapi.testclient import TestClient
    from main import app
    
    print("\n[8/8] Testing MCP failure handling...")
    
    # Save original state
    original_enabled = mcp_risk_client.enabled
    
    # Temporarily disable MCP (simulate failure)
    mcp_risk_client.enabled = False
    
    try:
        client = TestClient(app)
        response = client.post("/backtest/run", json={
            "symbol": "AAPL",
            "natural_language_strategy": "buy when RSI is below 30"
        })
        
        # Should return 503 error
        assert response.status_code == 503, f"Expected 503, got {response.status_code}"
        error_detail = response.json()['detail']
        assert "MCP" in error_detail, "Error message should mention MCP"
        
        print("✅ MCP failure handling works correctly")
        print(f"   Error message: {error_detail[:100]}...")
        
    finally:
        # Restore original state
        mcp_risk_client.enabled = original_enabled

async def run_all_tests():
    """Run all MCP integration tests"""
    print("=" * 70)
    print("MCP BACKTEST INTEGRATION TEST SUITE")
    print("=" * 70)
    print("\nTesting 5 MCP enhancements:")
    print("  1. MCP VaR in backtesting")
    print("  2. Position sizing recommendations")
    print("  3. ATR-based dynamic stops")
    print("  4. Risk/reward in explainer")
    print("  5. System capabilities endpoint")
    print()
    
    tests = [
        ("MCP Server Startup", test_1_mcp_server_startup),
        ("MCP VaR Calculation", test_2_mcp_var_calculation),
        ("MCP Position Sizing", test_3_mcp_position_sizing),
        ("MCP Stop Optimization", test_4_mcp_stop_optimization),
        ("MCP Risk/Reward", test_5_mcp_risk_reward),
        ("Capabilities Endpoint", test_6_capabilities_endpoint),
        ("Full Backtest with MCP", test_7_full_backtest_with_mcp),
        ("MCP Failure Handling", test_8_mcp_failure_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name} FAILED: {e}")
            failed += 1
            break  # Stop on first failure
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            break
    
    print()
    print("=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ALL MCP INTEGRATION TESTS PASSED!")
        print("\nMCP enhancements are fully operational:")
        print("  ✅ Professional VaR calculations with MCP")
        print("  ✅ Kelly Criterion position sizing")
        print("  ✅ ATR-based dynamic stop optimization")
        print("  ✅ Risk/reward analysis in explanations")
        print("  ✅ System capabilities API")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("\nPlease check:")
        print("  - Node.js is installed")
        print("  - MCP server is built: cd mcp/risk-tools && npm install && npm run build")
        print("  - USE_MCP_RISK_TOOLS=true in .env")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)

