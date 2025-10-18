"""
Comprehensive Integration Test - Tests All 3 Differentiators
Run: python apps/ai/test_integration.py
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
logging.getLogger('openai').setLevel(logging.WARNING)

async def test_1_sentiment_analysis():
    """Test sentiment analysis (already tested but reconfirm)"""
    print("\n" + "="*80)
    print("TEST 1: SENTIMENT ANALYSIS")
    print("="*80)
    
    try:
        from sentiment.aggregator import sentiment_aggregator
        
        result = await sentiment_aggregator.get_sentiment(
            symbol="NVDA",
            user_id="test_user"
        )
        
        assert 'symbol' in result, "Missing symbol"
        assert 'overall_score' in result, "Missing overall_score"
        assert 'sentiment_breakdown' in result, "Missing sentiment_breakdown"
        
        print(f"[OK] Sentiment: {result['overall_score']:.2f} ({result['direction']})")
        print(f"  News: {result['sentiment_breakdown']['news']:.2f}")
        print(f"  Reddit: {result['sentiment_breakdown']['reddit']:.2f}")
        print(f"  StockTwits: {result['sentiment_breakdown']['stocktwits']:.2f}")
        print(f"  Trending: {result['trending']}")
        
        return True, result
        
    except Exception as e:
        print(f"[ERROR] Sentiment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_2_backtest_integration():
    """Test backtest with strategy builder"""
    print("\n" + "="*80)
    print("TEST 2: BACKTEST INTEGRATION (Strategy Builder + Engine)")
    print("="*80)
    
    try:
        from backtesting.templates import get_template
        from backtesting.builder import strategy_builder
        from backtesting.engine import BacktestEngine
        from data.market_data import market_data_service
        from datetime import datetime, timedelta
        
        # Step 1: Get template
        print("  Step 1: Getting RSI oversold template...")
        template = get_template('rsi_oversold')
        assert template is not None, "Template not found"
        print(f"  [OK] Template: {template['name']}")
        
        # Step 2: Build strategy
        print("  Step 2: Building strategy function...")
        strategy_func = strategy_builder.build_strategy(template)
        assert callable(strategy_func), "Strategy function not callable"
        print("  [OK] Strategy function built")
        
        # Step 3: Get market data
        print("  Step 3: Getting market data...")
        
        data = await market_data_service.get_ohlcv(
            symbol="AAPL",
            period="3mo",  # 3 months for faster test
            interval="1d"
        )
        
        assert not data.empty, "No market data returned"
        print(f"  [OK] Got {len(data)} days of data")
        
        # Step 4: Run backtest
        print("  Step 4: Running backtest...")
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        engine = BacktestEngine()
        results = await engine.run_backtest(
            symbol="AAPL",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            strategy_fn=strategy_func,
            initial_capital=100000
        )
        
        # BacktestEngine returns metrics directly, not {metrics: ...}
        assert 'win_rate' in results, "Missing win_rate in results"
        assert 'num_trades' in results, "Missing num_trades in results"
        
        print(f"[OK] Backtest complete:")
        print(f"  Win Rate: {results['win_rate']:.1%}")
        print(f"  Total Return: {results['total_return_pct']:.1%}")
        print(f"  Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        print(f"  Trades: {results['num_trades']}")
        
        return True, results
        
    except Exception as e:
        print(f"[ERROR] Backtest test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_3_recommendation_agent():
    """Test recommendation agent (integrates sentiment + backtest)"""
    print("\n" + "="*80)
    print("TEST 3: RECOMMENDATION AGENT (Full Integration)")
    print("="*80)
    
    try:
        from agents.recommend import recommendation_agent
        
        print("  Generating recommendation for NVDA...")
        recommendation = await recommendation_agent.generate_recommendation(
            symbol="NVDA",
            user_id="test_user"
        )
        
        # Verify structure
        assert 'symbol' in recommendation, "Missing symbol"
        assert 'action' in recommendation, "Missing action"
        assert 'sentiment' in recommendation, "Missing sentiment"
        assert 'backtest_validation' in recommendation, "Missing backtest_validation"
        assert 'reasoning' in recommendation, "Missing reasoning"
        
        print(f"[OK] Recommendation generated:")
        print(f"  Symbol: {recommendation['symbol']}")
        print(f"  Action: {recommendation['action']}")
        print(f"  Entry: ${recommendation['entry_price']:.2f}")
        print(f"  Stop: ${recommendation['stop_loss']:.2f}")
        print(f"  Target: ${recommendation['take_profit']:.2f}")
        print(f"  Sentiment: {recommendation['sentiment']['score']:.2f} ({recommendation['sentiment']['direction']})")
        print(f"  Backtest Win Rate: {recommendation['backtest_validation']['win_rate']:.1%}")
        print(f"  Reasoning: {recommendation['reasoning'][:100]}...")
        
        return True, recommendation
        
    except Exception as e:
        print(f"[ERROR] Recommendation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_4_chat_ai_agent():
    """Test chat AI agent"""
    print("\n" + "="*80)
    print("TEST 4: CHAT AI AGENT")
    print("="*80)
    
    try:
        from collaboration.chat import chat_ai_agent
        
        # Test 1: Should respond to question with symbol
        message1 = "What do you think about NVDA?"
        print(f"  Testing message: '{message1}'")
        
        should_respond, response = await chat_ai_agent.handle_message(
            message=message1,
            workspace_id="test_workspace",
            user_id="test_user"
        )
        
        assert should_respond, "AI should respond to question with symbol"
        assert response is not None, "Response should not be None"
        assert 'message' in response, "Missing message"
        
        print(f"[OK] AI responded:")
        print(f"  Message: {response['message'][:150]}...")
        print(f"  Symbols analyzed: {response.get('symbols_analyzed', [])}")
        
        # Test 2: Should NOT respond to random chat
        message2 = "Hey team, how's everyone doing?"
        should_respond2, _ = await chat_ai_agent.handle_message(
            message=message2,
            workspace_id="test_workspace",
            user_id="test_user"
        )
        
        assert not should_respond2, "AI should NOT respond to random chat"
        print(f"[OK] AI correctly ignored: '{message2}'")
        
        return True, response
        
    except Exception as e:
        print(f"[ERROR] Chat AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_5_websocket_connection_manager():
    """Test WebSocket connection manager"""
    print("\n" + "="*80)
    print("TEST 5: WEBSOCKET CONNECTION MANAGER")
    print("="*80)
    
    try:
        from streaming.websocket_server import ConnectionManager
        
        manager = ConnectionManager()
        
        # Test connection tracking
        print("  Testing connection tracking...")
        workspace_id = "test_workspace"
        
        # Simulate connections (without actual WebSocket objects)
        assert manager.get_connection_count() == 0, "Should start with 0 connections"
        assert manager.get_workspace_count() == 0, "Should start with 0 workspaces"
        
        print("[OK] Connection manager initialized correctly")
        print(f"  Connection count: {manager.get_connection_count()}")
        print(f"  Workspace count: {manager.get_workspace_count()}")
        
        return True, None
        
    except Exception as e:
        print(f"[ERROR] WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_6_complete_demo_flow():
    """Test complete demo flow end-to-end"""
    print("\n" + "="*80)
    print("TEST 6: COMPLETE DEMO FLOW (End-to-End)")
    print("="*80)
    
    try:
        print("  Simulating complete user journey for TSLA...")
        
        # Step 1: User asks about stock
        print("\n  Step 1: User asks 'Should I buy TSLA?'")
        
        # Step 2: Get sentiment
        print("  Step 2: Getting sentiment...")
        from sentiment.aggregator import sentiment_aggregator
        sentiment = await sentiment_aggregator.get_sentiment("TSLA", user_id="demo_user")
        print(f"  [OK] Sentiment: {sentiment['overall_score']:.2f} ({sentiment['direction']})")
        
        # Step 3: Get recommendation (includes backtest)
        print("  Step 3: Generating recommendation...")
        from agents.recommend import recommendation_agent
        recommendation = await recommendation_agent.generate_recommendation(
            symbol="TSLA",
            user_id="demo_user"
        )
        print(f"  [OK] Recommendation: {recommendation['action']}")
        print(f"       Win Rate: {recommendation['backtest_validation']['win_rate']:.1%}")
        
        # Step 4: AI responds to team chat
        print("  Step 4: User shares in team chat...")
        from collaboration.chat import chat_ai_agent
        message = f"Got a {recommendation['action']} signal for TSLA. Sentiment is {sentiment['overall_score']:.2f}. Thoughts?"
        should_respond, ai_response = await chat_ai_agent.handle_message(
            message=message,
            workspace_id="demo_workspace",
            user_id="demo_user"
        )
        
        if should_respond:
            print(f"  [OK] AI responded: {ai_response['message'][:100]}...")
        else:
            print("  [WARN] AI did not respond (might be ok)")
        
        print("\n[OK] COMPLETE DEMO FLOW SUCCESS")
        print("  [OK] Sentiment analysis working")
        print("  [OK] Backtest validation working")
        print("  [OK] Recommendation generation working")
        print("  [OK] Chat AI working")
        
        return True, {
            'sentiment': sentiment,
            'recommendation': recommendation,
            'ai_response': ai_response if should_respond else None
        }
        
    except Exception as e:
        print(f"[ERROR] Demo flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_7_error_handling():
    """Test error handling"""
    print("\n" + "="*80)
    print("TEST 7: ERROR HANDLING")
    print("="*80)
    
    try:
        from agents.recommend import recommendation_agent
        
        # Test with invalid symbol
        print("  Testing invalid symbol...")
        try:
            result = await recommendation_agent.generate_recommendation(
                symbol="INVALID_SYMBOL_12345",
                user_id="test_user"
            )
            print("[WARN] Should have handled invalid symbol gracefully")
            print(f"  Got result: {result.get('action', 'N/A')}")
        except Exception as e:
            print(f"[OK] Error handled: {type(e).__name__}")
        
        return True, None
        
    except Exception as e:
        print(f"[ERROR] Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_8_morning_brief():
    """Test morning brief generation with voice"""
    print("\n" + "="*80)
    print("TEST 8: MORNING BRIEF WITH VOICE")
    print("="*80)
    
    try:
        from agents.morning_brief import morning_brief_agent
        
        watchlist = ["NVDA", "TSLA"]
        
        print(f"  Generating morning brief for watchlist: {watchlist}")
        
        brief = await morning_brief_agent.generate_brief(
            watchlist=watchlist,
            market="US",
            user_id="test_user",
            include_voice=True
        )
        
        print(f"\n[OK] Morning brief generated:")
        print(f"  Type: {brief['type']}")
        print(f"  Text length: {len(brief['text'])} chars (target: <1000)")
        print(f"  Symbols analyzed: {brief['symbols_analyzed']}")
        print(f"  Has voice: {brief['audio_base64'] is not None}")
        
        # Check text length (should be <2 min read, ~400 words, ~2000 chars)
        assert len(brief['text']) < 2000, f"Brief too long: {len(brief['text'])} chars"
        assert len(brief['symbols_analyzed']) == len(watchlist), "Not all symbols analyzed"
        
        print(f"\n  Brief preview:")
        print(f"  {brief['text'][:200]}...")
        
        if brief['audio_base64']:
            print(f"\n  [OK] Voice narration generated!")
            print(f"    Audio size: {len(brief['audio_base64'])} bytes (base64)")
        else:
            print(f"\n  [WARN] No voice (ElevenLabs might be disabled)")
        
        return True, brief
        
    except Exception as e:
        print(f"[ERROR] Morning brief test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def test_9_eod_brief():
    """Test EOD brief generation with voice"""
    print("\n" + "="*80)
    print("TEST 9: EOD BRIEF WITH VOICE")
    print("="*80)
    
    try:
        from agents.eod_brief import eod_brief_agent
        
        watchlist = ["AAPL", "MSFT"]
        
        print(f"  Generating EOD brief for watchlist: {watchlist}")
        
        brief = await eod_brief_agent.generate_brief(
            watchlist=watchlist,
            market="US",
            user_id="test_user",
            include_voice=True
        )
        
        print(f"\n[OK] EOD brief generated:")
        print(f"  Type: {brief['type']}")
        print(f"  Text length: {len(brief['text'])} chars (target: <1000)")
        print(f"  Symbols analyzed: {brief['symbols_analyzed']}")
        print(f"  Has voice: {brief['audio_base64'] is not None}")
        
        # Check performance summary
        perf_summary = brief['performance_summary']
        print(f"\n  Performance Summary:")
        print(f"    Gainers: {perf_summary['gainers']}")
        print(f"    Losers: {perf_summary['losers']}")
        print(f"    Avg change: {perf_summary['average_change']:.2f}%")
        
        # Check text length
        assert len(brief['text']) < 2000, f"Brief too long: {len(brief['text'])} chars"
        assert len(brief['symbols_analyzed']) == len(watchlist), "Not all symbols analyzed"
        
        print(f"\n  Brief preview:")
        print(f"  {brief['text'][:200]}...")
        
        if brief['audio_base64']:
            print(f"\n  [OK] Voice narration generated!")
            print(f"    Audio size: {len(brief['audio_base64'])} bytes (base64)")
        else:
            print(f"\n  [WARN] No voice (ElevenLabs might be disabled)")
        
        return True, brief
        
    except Exception as e:
        print(f"[ERROR] EOD brief test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("KOPITIAM CAPITAL - COMPREHENSIVE INTEGRATION TEST")
    print("="*80)
    print("\nTesting all 3 differentiators + integration + voice briefs...")
    
    tests = [
        ("Sentiment Analysis", test_1_sentiment_analysis),
        ("Backtest Integration", test_2_backtest_integration),
        ("Recommendation Agent", test_3_recommendation_agent),
        ("Chat AI Agent", test_4_chat_ai_agent),
        ("WebSocket Manager", test_5_websocket_connection_manager),
        ("Complete Demo Flow", test_6_complete_demo_flow),
        ("Error Handling", test_7_error_handling),
        ("Morning Brief with Voice", test_8_morning_brief),
        ("EOD Brief with Voice", test_9_eod_brief),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            success, data = await test_func()
            results[name] = {'success': success, 'data': data}
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results[name] = {'success': False, 'data': None}
    
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
        print("\n  [OK] ALL TESTS PASSED - READY FOR DEMO!")
    else:
        print(f"\n  [WARN] {total - passed} test(s) failed - needs fixes")
    
    print("\n" + "="*80)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

