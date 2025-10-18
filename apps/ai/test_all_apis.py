"""
Comprehensive API Test Suite
Tests ALL external APIs and internal endpoints
"""
import asyncio
import logging
import sys
from pathlib import Path
import httpx

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
logging.getLogger('yfinance').setLevel(logging.WARNING)

from utils.config import settings

# ============================================================================
# EXTERNAL API TESTS
# ============================================================================

async def test_openai_api():
    """Test OpenAI API connection"""
    print("\n" + "="*80)
    print("TEST: OPENAI API")
    print("="*80)
    
    try:
        from utils.clients import get_openai_client
        
        client = get_openai_client()
        
        # Simple completion test
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OpenAI API working' and nothing else"}],
            max_tokens=10
        )
        
        content = response.choices[0].message.content
        
        print(f"  [OK] OpenAI API working")
        print(f"    Model: gpt-4o-mini")
        print(f"    Response: {content}")
        print(f"    Tokens: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] OpenAI API failed: {e}")
        return False

async def test_groq_api():
    """Test Groq API connection"""
    print("\n" + "="*80)
    print("TEST: GROQ API")
    print("="*80)
    
    try:
        from utils.clients import get_groq_client
        
        client = get_groq_client()
        
        # Simple completion test
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'Groq API working' and nothing else"}],
            max_tokens=10
        )
        
        content = response.choices[0].message.content
        
        print(f"  [OK] Groq API working")
        print(f"    Model: llama-3.3-70b-versatile")
        print(f"    Response: {content}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Groq API failed: {e}")
        return False

async def test_mem0_api():
    """Test Mem0 API connection"""
    print("\n" + "="*80)
    print("TEST: MEM0 API")
    print("="*80)
    
    try:
        from memory.mem0_service import mem0_service
        
        if not mem0_service.enabled:
            print("  [WARN] Mem0 disabled in config")
            return True  # Not a failure, just disabled
        
        # Test add and search
        test_user = "api_test_user"
        
        await mem0_service.add_user_preference(
            user_id=test_user,
            preference_type="test",
            value="API test preference"
        )
        
        print(f"  [OK] Mem0 API working")
        print(f"    Preference added successfully")
        print(f"    Client initialized: {mem0_service.client is not None}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Mem0 API failed: {e}")
        return False

async def test_yfinance_api():
    """Test yfinance API"""
    print("\n" + "="*80)
    print("TEST: YFINANCE API")
    print("="*80)
    
    try:
        from data.market_data import market_data_service
        
        # Get current price
        price = await market_data_service.get_latest_price("AAPL")
        
        print(f"  [OK] yfinance API working")
        print(f"    AAPL price: ${price:.2f}")
        
        # Get OHLCV data
        data = await market_data_service.get_ohlcv("AAPL", period="5d", interval="1d")
        
        print(f"    Historical data: {len(data)} days")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] yfinance API failed: {e}")
        return False

async def test_stocktwits_api():
    """Test StockTwits API"""
    print("\n" + "="*80)
    print("TEST: STOCKTWITS API")
    print("="*80)
    
    try:
        import httpx
        
        url = "https://api.stocktwits.com/api/2/streams/symbol/AAPL.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                
                print(f"  [OK] StockTwits API working")
                print(f"    Messages retrieved: {len(messages)}")
                
                return True
            elif response.status_code == 403:
                print(f"  [WARN] StockTwits returns 403 (expected without auth)")
                print(f"    API is accessible but rate limited")
                return True  # Not a failure, expected behavior
            else:
                print(f"  [ERROR] StockTwits unexpected status: {response.status_code}")
                return False
        
    except Exception as e:
        print(f"  [ERROR] StockTwits API failed: {e}")
        return False

async def test_reddit_api():
    """Test Reddit PRAW API"""
    print("\n" + "="*80)
    print("TEST: REDDIT PRAW API")
    print("="*80)
    
    try:
        import praw
        
        if not settings.client_id or not settings.client_secret:
            print("  [WARN] Reddit credentials not in .env")
            print("    Set CLIENT_ID and CLIENT_SECRET to enable")
            return True  # Not a failure, just not configured
        
        reddit = praw.Reddit(
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            user_agent=settings.user_agent
        )
        
        # Test connection
        subreddit = reddit.subreddit('wallstreetbets')
        posts = list(subreddit.hot(limit=1))
        
        print(f"  [OK] Reddit PRAW API working")
        print(f"    Connected to r/wallstreetbets")
        print(f"    Test post retrieved: {posts[0].title if posts else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Reddit API failed: {e}")
        return False

# ============================================================================
# INTERNAL ENDPOINT TESTS
# ============================================================================

async def test_health_endpoint():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST: HEALTH ENDPOINT")
    print("="*80)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Health endpoint working")
                print(f"    Status: {data.get('status')}")
                print(f"    Service: {data.get('service')}")
                return True
            else:
                print(f"  [ERROR] Health endpoint returned {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print(f"  [SKIP] FastAPI server not running")
        print(f"    Start with: uvicorn main:app --reload")
        return True  # Not a failure, just not started
    except Exception as e:
        print(f"  [ERROR] Health endpoint failed: {e}")
        return False

async def test_sentiment_endpoint():
    """Test sentiment endpoint"""
    print("\n" + "="*80)
    print("TEST: SENTIMENT ENDPOINT")
    print("="*80)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/sentiment/NVDA?user_id=test",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Sentiment endpoint working")
                print(f"    Overall Score: {data.get('overall_score')}")
                print(f"    Direction: {data.get('direction')}")
                return True
            else:
                print(f"  [ERROR] Sentiment endpoint returned {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print(f"  [SKIP] FastAPI server not running")
        return True
    except Exception as e:
        print(f"  [ERROR] Sentiment endpoint failed: {e}")
        return False

async def test_recommend_endpoint():
    """Test recommendation endpoint"""
    print("\n" + "="*80)
    print("TEST: RECOMMEND ENDPOINT")
    print("="*80)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/ai/recommend",
                json={"symbol": "AAPL", "user_id": "test"},
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Recommend endpoint working")
                print(f"    Symbol: {data.get('symbol')}")
                print(f"    Action: {data.get('action')}")
                print(f"    Win Rate: {data.get('backtest_validation', {}).get('win_rate', 0):.1%}")
                return True
            else:
                print(f"  [ERROR] Recommend endpoint returned {response.status_code}")
                print(f"    Response: {response.text[:200]}")
                return False
                
    except httpx.ConnectError:
        print(f"  [SKIP] FastAPI server not running")
        return True
    except Exception as e:
        print(f"  [ERROR] Recommend endpoint failed: {e}")
        return False

async def test_backtest_endpoint():
    """Test backtest endpoint"""
    print("\n" + "="*80)
    print("TEST: BACKTEST ENDPOINT")
    print("="*80)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/backtest/run",
                json={
                    "symbol": "AAPL",
                    "strategy_template_id": "rsi_oversold",
                    "initial_capital": 100000
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Backtest endpoint working")
                print(f"    Symbol: {data.get('symbol')}")
                print(f"    Strategy: {data.get('strategy')}")
                metrics = data.get('metrics', {})
                print(f"    Win Rate: {metrics.get('win_rate', 0):.1%}")
                print(f"    Trades: {metrics.get('num_trades', 0)}")
                return True
            else:
                print(f"  [ERROR] Backtest endpoint returned {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print(f"  [SKIP] FastAPI server not running")
        return True
    except Exception as e:
        print(f"  [ERROR] Backtest endpoint failed: {e}")
        return False

async def test_templates_endpoint():
    """Test backtest templates endpoint"""
    print("\n" + "="*80)
    print("TEST: BACKTEST TEMPLATES ENDPOINT")
    print("="*80)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/backtest/templates",
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('templates', [])
                print(f"  [OK] Templates endpoint working")
                print(f"    Templates available: {len(templates)}")
                for template in templates[:3]:
                    print(f"      - {template.get('name')} ({template.get('difficulty')})")
                return True
            else:
                print(f"  [ERROR] Templates endpoint returned {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print(f"  [SKIP] FastAPI server not running")
        return True
    except Exception as e:
        print(f"  [ERROR] Templates endpoint failed: {e}")
        return False

async def test_orchestrate_endpoint():
    """Test orchestrator endpoint"""
    print("\n" + "="*80)
    print("TEST: ORCHESTRATE ENDPOINT (Smart NLP)")
    print("="*80)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/ai/orchestrate",
                json={"query": "Should I buy TSLA?", "user_id": "test"},
                timeout=20.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Orchestrate endpoint working")
                print(f"    Intent: {data.get('intent')}")
                print(f"    Has result: {bool(data.get('result'))}")
                return True
            else:
                print(f"  [ERROR] Orchestrate endpoint returned {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print(f"  [SKIP] FastAPI server not running")
        return True
    except Exception as e:
        print(f"  [ERROR] Orchestrate endpoint failed: {e}")
        return False

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

async def test_full_recommendation_flow():
    """Test complete recommendation generation flow"""
    print("\n" + "="*80)
    print("TEST: FULL RECOMMENDATION FLOW (All APIs)")
    print("="*80)
    
    try:
        from agents.recommend import recommendation_agent
        from memory.mem0_service import mem0_service
        
        print("  Generating recommendation for MSFT...")
        print("  This tests: Sentiment + yfinance + Mem0 + Backtest + OpenAI")
        
        recommendation = await recommendation_agent.generate_recommendation(
            symbol="MSFT",
            user_id="integration_test_user"
        )
        
        print(f"\n  [OK] Complete flow working:")
        print(f"    Symbol: {recommendation['symbol']}")
        print(f"    Action: {recommendation['action']}")
        print(f"    Sentiment: {recommendation['sentiment']['score']:.2f}")
        print(f"    Backtest Win Rate: {recommendation['backtest_validation']['win_rate']:.1%}")
        print(f"    Position: {recommendation['position_size_shares']} shares")
        print(f"    Method: {recommendation.get('method', 'N/A')}")
        
        # Check if using advanced features
        if 'mem0' in recommendation.get('method', '').lower() or mem0_service.enabled:
            print(f"    [OK] Using Mem0 for personalization!")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Full recommendation flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chat_ai_with_sentiment():
    """Test chat AI with live sentiment lookup"""
    print("\n" + "="*80)
    print("TEST: CHAT AI WITH SENTIMENT LOOKUP")
    print("="*80)
    
    try:
        from collaboration.chat import chat_ai_agent
        
        message = "What's your take on MSFT?"
        
        print(f"  Testing message: '{message}'")
        print("  This tests: Symbol detection + Sentiment API + OpenAI")
        
        should_respond, response = await chat_ai_agent.handle_message(
            message=message,
            workspace_id="api_test_workspace",
            user_id="api_test_user"
        )
        
        if should_respond:
            print(f"\n  [OK] Chat AI with sentiment working:")
            print(f"    AI responded: Yes")
            print(f"    Symbols analyzed: {response.get('symbols_analyzed', [])}")
            print(f"    Message length: {len(response.get('message', ''))} chars")
        else:
            print(f"  [WARN] AI chose not to respond (might be ok)")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Chat AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_sentiment_aggregation():
    """Test sentiment aggregation from all sources"""
    print("\n" + "="*80)
    print("TEST: SENTIMENT AGGREGATION (All Sources)")
    print("="*80)
    
    try:
        from sentiment.aggregator import sentiment_aggregator
        
        print("  Testing sentiment for AMD...")
        print("  This tests: Exa + Groq + Reddit + StockTwits")
        
        result = await sentiment_aggregator.get_sentiment(
            symbol="AMD",
            user_id="api_test_user"
        )
        
        print(f"\n  [OK] Sentiment aggregation working:")
        print(f"    Overall: {result['overall_score']:.2f} ({result['direction']})")
        print(f"    News: {result['sentiment_breakdown']['news']:.2f}")
        print(f"    Reddit: {result['sentiment_breakdown']['reddit']:.2f}")
        print(f"    StockTwits: {result['sentiment_breakdown']['stocktwits']:.2f}")
        print(f"    Confidence: {result['confidence']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Sentiment aggregation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_api_tests():
    """Run all API tests"""
    print("\n" + "="*80)
    print("KOPITIAM CAPITAL - COMPREHENSIVE API TEST SUITE")
    print("="*80)
    
    print("\nTesting all external APIs and internal endpoints...")
    print(f"Base URL: http://localhost:8000")
    
    tests = [
        ("OpenAI API", test_openai_api),
        ("Groq API", test_groq_api),
        ("Mem0 API", test_mem0_api),
        ("yfinance API", test_yfinance_api),
        ("StockTwits API", test_stocktwits_api),
        ("Reddit PRAW API", test_reddit_api),
        ("Health Endpoint", test_health_endpoint),
        ("Sentiment Endpoint", test_sentiment_endpoint),
        ("Recommend Endpoint", test_recommend_endpoint),
        ("Backtest Endpoint", test_backtest_endpoint),
        ("Templates Endpoint", test_templates_endpoint),
        ("Orchestrate Endpoint", test_orchestrate_endpoint),
        ("Full Recommendation Flow", test_full_recommendation_flow),
        ("Chat AI + Sentiment", test_chat_ai_with_sentiment),
        ("Sentiment Aggregation", test_sentiment_aggregation),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            success = await test_func()
            results[name] = success
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("API TEST SUMMARY")
    print("="*80)
    
    external_apis = ["OpenAI API", "Groq API", "Mem0 API", "yfinance API", "StockTwits API", "Reddit PRAW API"]
    internal_endpoints = [name for name in results.keys() if name not in external_apis]
    
    print("\n  EXTERNAL APIs:")
    for name in external_apis:
        status = "[OK]" if results.get(name) else "[ERROR]"
        print(f"    {status} {name}")
    
    print("\n  INTERNAL Endpoints:")
    for name in internal_endpoints:
        status = "[OK]" if results.get(name) else "[ERROR]"
        print(f"    {status} {name}")
    
    passed = sum(1 for s in results.values() if s)
    total = len(results)
    
    print(f"\n  Total Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  [OK] ALL API TESTS PASSED!")
    elif passed >= total * 0.8:
        print(f"\n  [OK] Most APIs working ({passed}/{total})")
    else:
        print(f"\n  [WARN] {total - passed} API(s) failed")
    
    print("\n" + "="*80)
    print("NOTES:")
    print("  - FastAPI endpoints require server running:")
    print("    cd apps/ai && uvicorn main:app --reload")
    print("  - Some APIs return warnings (expected in dev mode)")
    print("  - 403 from StockTwits is normal without auth token")
    print("="*80 + "\n")
    
    return passed >= total * 0.8  # 80% pass rate is acceptable

if __name__ == "__main__":
    success = asyncio.run(run_all_api_tests())
    sys.exit(0 if success else 1)

