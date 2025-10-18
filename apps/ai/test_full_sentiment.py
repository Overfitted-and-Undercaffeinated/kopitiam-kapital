"""Test full sentiment flow end-to-end"""
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Force fresh import
    import importlib
    import sys
    
    # Remove cached modules
    for module in list(sys.modules.keys()):
        if 'sentiment' in module or 'exa' in module or 'rag' in module:
            del sys.modules[module]
    
    from sentiment.aggregator import sentiment_aggregator
    
    print("\n" + "="*80)
    print("FULL SENTIMENT AGGREGATION TEST (Fresh Import)")
    print("="*80)
    
    result = await sentiment_aggregator.get_sentiment('NVDA', 24, 'test_user')
    
    print("\n" + "="*80)
    print("RESULTS:")
    print("="*80)
    print(f"Overall Score: {result['overall_score']} ({result['direction']})")
    print(f"Confidence: {result['confidence']}")
    print(f"Trending: {result['trending']}")
    print(f"\nBreakdown:")
    print(f"  News:       {result['sentiment_breakdown']['news']}")
    print(f"  Reddit:     {result['sentiment_breakdown']['reddit']}")
    print(f"  StockTwits: {result['sentiment_breakdown']['stocktwits']}")
    print(f"\nVolume:")
    print(f"  News articles:  {result['volume']['news_articles']}")
    print(f"  Reddit posts:   {result['volume']['reddit_mentions']}")
    print(f"  StockTwits:     {result['volume']['stocktwits_messages']}")
    
    if result['top_sources']:
        print(f"\nTop Sources:")
        for i, source in enumerate(result['top_sources'][:3], 1):
            print(f"  {i}. [{source['type']}] {source['title'][:60]}...")
            if 'sentiment_score' in source:
                print(f"     Score: {source['sentiment_score']}")
    
    print("\n" + "="*80)
    
    # Check if it's working
    if result['overall_score'] != 0.5 or result['volume']['news_articles'] > 0:
        print("✓ SENTIMENT IS WORKING!")
        return True
    else:
        print("❌ SENTIMENT STILL DEFAULTING TO NEUTRAL")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)



