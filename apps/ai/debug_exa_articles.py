"""Debug: See what Exa is actually returning"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def debug_exa():
    from retrievers.exa_client import exa_client
    
    print("\n" + "="*80)
    print("DEBUGGING EXA ARTICLE CONTENT")
    print("="*80)
    
    # Search for NVDA news
    articles = await exa_client.search_fast("NVDA latest news", num_results=15)
    
    print(f"\nTotal articles returned: {len(articles)}")
    
    for i, article in enumerate(articles, 1):
        print("\n" + "-"*80)
        print(f"ARTICLE {i}:")
        print("-"*80)
        print(f"Title: {article.get('title', 'NO TITLE')}")
        print(f"URL: {article.get('url', 'NO URL')}")
        
        text = article.get('text', '')
        highlights = article.get('highlights', [])
        
        print(f"\nText length: {len(text)} chars")
        if text:
            print(f"Text preview: {text[:200]}...")
        else:
            print("Text preview: [EMPTY]")
        
        print(f"\nHighlights count: {len(highlights) if highlights else 0}")
        if highlights and len(highlights) > 0:
            for j, highlight in enumerate(highlights[:3], 1):
                print(f"  {j}. {highlight[:100]}...")
        
        # Check if would pass our filters
        skip_keywords = ['stock quote', 'stock price', 'latest stock news', 'annual income statement']
        would_skip = any(keyword in article.get('title', '').lower() for keyword in skip_keywords)
        has_content = len(text) >= 50 or len(highlights) > 0
        
        print(f"\nWould skip: {would_skip}")
        print(f"Has content: {has_content}")
        print(f"VERDICT: {'✓ KEEP' if not would_skip and has_content else '✗ SKIP'}")
    
    # Summary
    keepers = [
        a for a in articles
        if not any(kw in a.get('title', '').lower() for kw in ['stock quote', 'stock price', 'latest stock news', 'annual income statement'])
        and (len(a.get('text', '')) >= 50 or len(a.get('highlights', [])) > 0)
    ]
    
    print("\n" + "="*80)
    print(f"SUMMARY: {len(keepers)}/{len(articles)} articles would be kept for scoring")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(debug_exa())

