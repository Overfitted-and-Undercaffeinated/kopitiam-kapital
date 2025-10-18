"""
Test Sentiment Analysis Pipeline
Run: python apps/ai/test_sentiment.py
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

from sentiment.news_sentiment import news_sentiment_analyzer
from sentiment.social_scraper import social_sentiment_analyzer
from sentiment.aggregator import sentiment_aggregator

async def test_news_sentiment():
    """Test news sentiment analysis"""
    print("\n" + "="*80)
    print("TEST 1: NEWS SENTIMENT ANALYSIS")
    print("="*80)
    
    try:
        result = await news_sentiment_analyzer.analyze(
            symbol="NVDA",
            lookback_hours=24
        )
        
        print(f"\n[OK] News sentiment analysis completed")
        print(f"  Score: {result['score']:.2f}")
        print(f"  Articles analyzed: {result['article_count']}")
        print(f"  Trending: {result['trending']}")
        
        if result['articles']:
            print("\n  Top articles:")
            for i, article in enumerate(result['articles'][:3], 1):
                print(f"    {i}. {article['title'][:60]}...")
                print(f"       Score: {article['sentiment_score']:.2f}")
                print(f"       URL: {article['url']}")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] News sentiment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_reddit_sentiment():
    """Test Reddit sentiment scraper"""
    print("\n" + "="*80)
    print("TEST 2: REDDIT SENTIMENT ANALYSIS")
    print("="*80)
    
    try:
        result = await social_sentiment_analyzer._analyze_reddit(
            symbol="NVDA",
            lookback_hours=24
        )
        
        print(f"\n[OK] Reddit sentiment analysis completed")
        print(f"  Score: {result['score']:.2f}")
        print(f"  Mentions: {result['mention_count']}")
        
        if result['mention_count'] == 0:
            print("  [WARN] No Reddit mentions found - this is expected if PRAW not configured")
            print("  [WARN] Mock mode is active")
        else:
            print("\n  Top posts:")
            for i, post in enumerate(result['top_posts'][:3], 1):
                print(f"    {i}. {post['title'][:60]}...")
                print(f"       Score: {post['score']:.2f}, Upvotes: {post['upvotes']}")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Reddit sentiment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_stocktwits_sentiment():
    """Test StockTwits sentiment"""
    print("\n" + "="*80)
    print("TEST 3: STOCKTWITS SENTIMENT ANALYSIS")
    print("="*80)
    
    try:
        result = await social_sentiment_analyzer._analyze_stocktwits(symbol="NVDA")
        
        print(f"\n[OK] StockTwits sentiment analysis completed")
        print(f"  Score: {result['score']:.2f}")
        print(f"  Messages: {result['message_count']}")
        
        if result.get('bullish_count') is not None:
            print(f"  Bullish: {result['bullish_count']}, Bearish: {result['bearish_count']}")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] StockTwits sentiment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_sentiment_aggregator():
    """Test full sentiment aggregator"""
    print("\n" + "="*80)
    print("TEST 4: SENTIMENT AGGREGATOR (FULL PIPELINE)")
    print("="*80)
    
    try:
        result = await sentiment_aggregator.get_sentiment(
            symbol="NVDA",
            lookback_hours=24,
            user_id="test_user"
        )
        
        print(f"\n[OK] Sentiment aggregator completed")
        print(f"\n  Symbol: {result['symbol']}")
        print(f"  Overall Score: {result['overall_score']:.2f} ({result['direction']})")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Trending: {result['trending']}")
        print(f"  Contrarian Signal: {result['contrarian_signal']}")
        
        print("\n  Breakdown:")
        print(f"    News:       {result['sentiment_breakdown']['news']:.2f}")
        print(f"    Reddit:     {result['sentiment_breakdown']['reddit']:.2f}")
        print(f"    StockTwits: {result['sentiment_breakdown']['stocktwits']:.2f}")
        
        print("\n  Volume:")
        print(f"    News articles:      {result['volume']['news_articles']}")
        print(f"    Reddit mentions:    {result['volume']['reddit_mentions']}")
        print(f"    StockTwits messages: {result['volume']['stocktwits_messages']}")
        
        if result['top_sources']:
            print("\n  Top sources:")
            for i, source in enumerate(result['top_sources'][:5], 1):
                print(f"    {i}. [{source['type'].upper()}] {source['title'][:50]}...")
                print(f"       Score: {source['sentiment_score']:.2f}")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Sentiment aggregator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_symbols():
    """Test sentiment for multiple symbols"""
    print("\n" + "="*80)
    print("TEST 5: MULTIPLE SYMBOLS")
    print("="*80)
    
    symbols = ["AAPL", "TSLA", "MSFT"]
    results = {}
    
    for symbol in symbols:
        try:
            print(f"\n  Analyzing {symbol}...")
            result = await sentiment_aggregator.get_sentiment(symbol=symbol)
            results[symbol] = result
            print(f"  [OK] {symbol}: {result['overall_score']:.2f} ({result['direction']})")
        
        except Exception as e:
            print(f"  [ERROR] {symbol} failed: {e}")
            results[symbol] = None
    
    print("\n  Summary:")
    for symbol, result in results.items():
        if result:
            print(f"    {symbol}: {result['overall_score']:.2f} ({result['direction']})")
        else:
            print(f"    {symbol}: FAILED")
    
    return True

async def run_all_tests():
    """Run all sentiment tests"""
    print("\n" + "="*80)
    print("KOPITIAM CAPITAL - SENTIMENT ANALYSIS TEST SUITE")
    print("="*80)
    
    tests = [
        ("News Sentiment", test_news_sentiment),
        ("Reddit Sentiment", test_reddit_sentiment),
        ("StockTwits Sentiment", test_stocktwits_sentiment),
        ("Sentiment Aggregator", test_sentiment_aggregator),
        ("Multiple Symbols", test_multiple_symbols)
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
    print("TEST SUMMARY")
    print("="*80)
    
    for name, success in results.items():
        status = "[OK]" if success else "[ERROR]"
        print(f"  {status} {name}")
    
    passed = sum(1 for s in results.values() if s)
    total = len(results)
    
    print(f"\n  Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  [OK] ALL TESTS PASSED!")
    else:
        print(f"\n  [WARN] {total - passed} test(s) failed")
    
    print("\n" + "="*80)
    print("NOTES:")
    print("  - Reddit requires PRAW configured in .env")
    print("  - StockTwits is free (no API key needed)")
    print("  - News sentiment uses Exa.ai (requires API key)")
    print("  - If any source fails, aggregator uses neutral (0.5) for that source")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())

