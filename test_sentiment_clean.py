#!/usr/bin/env python3
"""
Test sentiment analysis agent with cleaned Reddit/StockTwits removal
"""
import asyncio
import sys
import json
from pathlib import Path

# Add apps/ai to path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "ai"))

from sentiment.aggregator import sentiment_aggregator


async def test_sentiment():
    """Run sentiment analysis on several stocks"""
    
    symbols = ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT"]
    
    print("\n" + "="*80)
    print("SENTIMENT ANALYSIS - NEWS ONLY (Reddit & StockTwits Removed)")
    print("="*80 + "\n")
    
    for symbol in symbols:
        print(f"\n📊 Analyzing: {symbol}")
        print("-" * 80)
        
        try:
            result = await sentiment_aggregator.get_sentiment(symbol, user_id="test-user")
            
            # Display results
            print(f"Overall Score:        {result['overall_score']} ({result['direction'].upper()})")
            print(f"Confidence:           {result['confidence']}")
            print(f"Trending:             {result['trending']}")
            print(f"Contrarian Signal:    {result['contrarian_signal']}")
            
            print(f"\nSentiment Breakdown:")
            print(f"  News:               {result['sentiment_breakdown']['news']}")
            
            print(f"\nVolume:")
            print(f"  News Articles:      {result['volume']['news_articles']}")
            
            print(f"\nTop Sources ({len(result['top_sources'])} articles):")
            for i, source in enumerate(result['top_sources'][:3], 1):
                print(f"  {i}. {source['title'][:60]}...")
                print(f"     Score: {source['sentiment_score']} | URL: {source['url'][:50]}...")
            
            print(f"\nTimestamp:            {result['timestamp']}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_sentiment())
