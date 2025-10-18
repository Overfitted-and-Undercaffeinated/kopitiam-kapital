#!/usr/bin/env python3
"""
Test news sentiment analyzer directly - shows reasoning and scoring
"""
import asyncio
import sys
import json
from pathlib import Path

# Add apps/ai to path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "ai"))

from sentiment.news_sentiment import news_sentiment_analyzer


async def test_news_sentiment():
    """Run news sentiment analysis on a stock"""
    
    symbol = "NVDA"  # Test with NVDA (should be bullish - AI hype)
    
    print("\n" + "="*90)
    print(f"NEWS SENTIMENT ANALYZER - Testing: {symbol}")
    print("="*90 + "\n")
    
    try:
        result = await news_sentiment_analyzer.analyze(symbol, lookback_hours=24)
        
        print(f"📰 Overall News Sentiment Score: {result['score']:.2f}")
        print(f"📊 Articles Analyzed: {result['article_count']}")
        print(f"🔥 Trending: {result['trending']}")
        print(f"📝 Source: {result['source']}")
        
        print("\n" + "-"*90)
        print("DETAILED ARTICLE BREAKDOWN:")
        print("-"*90 + "\n")
        
        for i, article in enumerate(result['articles'], 1):
            print(f"\n[Article {i}]")
            print(f"Title:        {article['title']}")
            print(f"URL:          {article['url']}")
            print(f"Date:         {article['published_date']}")
            print(f"Score:        {article['sentiment_score']} ({['Very Bearish', 'Bearish', 'Neutral', 'Bullish', 'Very Bullish'][int(article['sentiment_score']*4)]}")
            print(f"Reasoning:    {article['sentiment_reasoning']}")
            if article['text']:
                print(f"Snippet:      {article['text'][:80]}...")
        
        print("\n" + "="*90)
        print("✅ ANALYSIS COMPLETE")
        print("="*90)
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_news_sentiment())
