"""Debug test to see exactly what Groq is returning"""
import asyncio
import logging
import json

logging.basicConfig(level=logging.DEBUG)

async def test_groq_sentiment():
    from utils.clients import get_groq_client
    from retrievers.exa_client import exa_client
    
    print("\n" + "="*80)
    print("DEBUGGING GROQ SENTIMENT SCORING")
    print("="*80)
    
    # Get a real article from Exa
    articles = await exa_client.search_fast("NVDA latest news", num_results=15)
    
    print(f"\nFound {len(articles)} articles from Exa")
    
    # Find first article with actual content
    test_article = None
    for article in articles:
        text = article.get('text', '').strip()
        title = article.get('title', '')
        if len(text) > 100:
            test_article = article
            print(f"\nUsing article: {title[:60]}...")
            print(f"Text length: {len(text)} chars")
            print(f"Text preview: {text[:200]}...")
            break
    
    if not test_article:
        print("\n❌ No articles with sufficient content found!")
        print("\nAll article previews:")
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article.get('title', 'NO TITLE')[:60]}")
            print(f"   Text length: {len(article.get('text', ''))} chars")
            print(f"   Text: {article.get('text', 'NO TEXT')[:100]}")
        return
    
    # Test Groq scoring
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

Article title: {test_article['title']}
Article content: {test_article['text'][:500]}
Symbol: NVDA"""
    
    print("\n" + "-"*80)
    print("SENDING TO GROQ:")
    print("-"*80)
    print(prompt[:300] + "...")
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=100,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        print("\n" + "-"*80)
        print("GROQ RESPONSE:")
        print("-"*80)
        print(f"Raw content: {repr(content)}")
        print(f"Content preview: {content}")
        
        # Try to parse
        try:
            result = json.loads(content)
            print("\n✓ Successfully parsed JSON:")
            print(f"  Score: {result.get('score')}")
            print(f"  Reasoning: {result.get('reasoning')}")
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON parsing failed: {e}")
            print(f"   Error position: {e.pos}")
            print(f"   Error message: {e.msg}")
    
    except Exception as e:
        print(f"\n❌ Groq API call failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq_sentiment())



