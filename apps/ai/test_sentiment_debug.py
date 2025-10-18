"""Test with DEBUG level logging to see exact errors"""
import asyncio
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

async def main():
    from sentiment.news_sentiment import news_sentiment_analyzer
    
    print("\n" + "="*80)
    print("SENTIMENT TEST WITH DEBUG LOGGING")
    print("="*80 + "\n")
    
    result = await news_sentiment_analyzer.analyze('NVDA', 24, 'debug_test')
    
    print("\n" + "="*80)
    print(f"Final score: {result['score']}")
    print(f"Articles scored: {result['article_count']}")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())


