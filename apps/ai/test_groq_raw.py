"""See exactly what Groq returns"""
import asyncio
from utils.clients import get_groq_client

async def test():
    client = get_groq_client()
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": """Analyze this article and return sentiment.

Return ONLY a JSON object:
{
  "score": 0.75,
  "reasoning": "Brief explanation"
}

Article: Nvidia stock is a top pick says Morgan Stanley"""
            }
        ],
        temperature=0.1,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    
    print("RAW CONTENT:")
    print(repr(content))
    print("\nPRETTY CONTENT:")
    print(content)
    
    import json
    try:
        result = json.loads(content)
        print("\nPARSED:")
        print(f"Keys: {list(result.keys())}")
        print(f"Keys repr: {[repr(k) for k in result.keys()]}")
        print(f"Score value: {result.get('score')}")
        print(f"Direct access result['score']: {result['score']}")
    except Exception as e:
        print(f"\nERROR: {e}")

asyncio.run(test())



