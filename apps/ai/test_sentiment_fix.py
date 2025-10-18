"""Quick test to verify sentiment scoring fixes"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test_sentiment():
    from sentiment.news_sentiment import news_sentiment_analyzer
    from rag.cache_strategy import cache_strategy
    
    print("\nTesting news sentiment with fixes...")
    print("="*60)
    
    # Clear cache to force fresh results
    cache_strategy._cache.clear()
    print("Cache cleared - fetching fresh results...")
    
    result = await news_sentiment_analyzer.analyze('NVDA', 24, 'test')
    
    print(f"\nResults for NVDA:")
    print(f"  Sentiment Score: {result['score']}")
    print(f"  Articles Scored: {result['article_count']}")
    print(f"  Trending: {result['trending']}")
    
    if result['articles']:
        print(f"\n  Sample Articles:")
        for i, article in enumerate(result['articles'][:3], 1):
            print(f"    {i}. {article['title'][:60]}...")
            print(f"       Score: {article['sentiment_score']}")
            print(f"       Reason: {article['sentiment_reasoning'][:60]}...")
    
    print("\n" + "="*60)
    print(f"✓ Test complete")
    
    return result['article_count'] > 0

if __name__ == "__main__":
    success = asyncio.run(test_sentiment())
    exit(0 if success else 1)

