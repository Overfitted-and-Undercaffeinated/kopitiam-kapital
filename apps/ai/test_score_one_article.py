"""Test scoring a single article with full debug output"""
import asyncio
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def test_one_article():
    from retrievers.exa_client import exa_client
    from utils.clients import get_groq_client
    
    print("\n" + "="*80)
    print("TESTING SINGLE ARTICLE SCORING")
    print("="*80)
    
    # Get articles
    articles = await exa_client.search_fast("NVDA latest news", num_results=15)
    
    # Find the Markets Insider article (should have good highlights)
    test_article = None
    for article in articles:
        if 'markets insider' in article.get('title', '').lower():
            test_article = article
            break
    
    if not test_article:
        # Use any article with highlights
        for article in articles:
            if article.get('highlights') and len(article['highlights']) > 0:
                test_article = article
                break
    
    if not test_article:
        print("❌ No suitable article found")
        return
    
    print(f"\nArticle: {test_article['title']}")
    print(f"URL: {test_article['url']}")
    print(f"\nText length: {len(test_article.get('text', ''))} chars")
    print(f"Highlights: {len(test_article.get('highlights', []))}")
    
    if test_article.get('highlights'):
        print("\nHighlights:")
        for i, h in enumerate(test_article['highlights'][:3], 1):
            print(f"  {i}. {h}")
    
    # Now try to score it using the actual agent logic
    article_text = test_article.get('text', '').strip()
    article_title = test_article.get('title', '')
    article_highlights = test_article.get('highlights', [])
    
    # Check for paywall
    paywall_indicators = ['oops, something went wrong', 'upgrade now', 'subscribe', 'login required']
    is_paywall = any(indicator in article_text.lower() for indicator in paywall_indicators)
    
    print(f"\nIs paywall: {is_paywall}")
    
    # Determine content to analyze
    if article_highlights and not is_paywall:
        content_to_analyze = ' '.join(article_highlights[:3])[:500]
        print(f"\nUsing highlights (first 500 chars)")
    elif len(article_text) > 50 and not is_paywall:
        content_to_analyze = article_text[:500]
        print(f"\nUsing article text (first 500 chars)")
    else:
        content_to_analyze = f"{article_title}. {article_text[:200]}"
        print(f"\nUsing fallback (title + snippet)")
    
    print(f"\nContent to analyze:")
    print("-"*80)
    print(content_to_analyze)
    print("-"*80)
    
    # Call Groq
    client = get_groq_client()
    
    prompt = f"""You are a financial sentiment analyzer. 

Analyze this article and return a sentiment score for the mentioned stock.

Score:
- 0.0 = Very Bearish (bad news, sell recommendation, negative outlook)
- 0.3 = Bearish (concerns, risks, downgrades)
- 0.5 = Neutral (mixed or factual reporting)
- 0.7 = Bullish (positive news, opportunities)
- 1.0 = Very Bullish (strong buy signals, major positive developments)

Return ONLY a JSON object:
{{
  "score": 0.75,
  "reasoning": "Brief explanation of why this score"
}}

Article title: {article_title}
Article content: {content_to_analyze}
Symbol: NVDA"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        print(f"\nGroq response:")
        print(content)
        
        result = json.loads(content)
        print(f"\n✓ Score: {result['score']}")
        print(f"✓ Reasoning: {result['reasoning']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_one_article())


