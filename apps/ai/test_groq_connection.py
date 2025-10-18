"""Quick test to check Groq API connection"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check if API key exists
groq_key = os.getenv("GROQ_API_KEY")
print(f"GROQ_API_KEY exists: {bool(groq_key)}")
if groq_key:
    print(f"GROQ_API_KEY starts with: {groq_key[:10]}...")
else:
    print("❌ GROQ_API_KEY is missing from .env file!")
    print("\nTo fix:")
    print("1. Get a free API key from: https://console.groq.com/keys")
    print("2. Add to .env file: GROQ_API_KEY=gsk_...")
    exit(1)

# Test connection
print("\nTesting Groq connection...")
try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=groq_key,
        base_url="https://api.groq.com/openai/v1"
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say 'Hello' if you can hear me."}
        ],
        max_tokens=10
    )
    
    result = response.choices[0].message.content
    print(f"✓ Groq responded: {result}")
    print("✓ Connection working!")
    
except Exception as e:
    print(f"❌ Groq connection failed: {e}")
    print("\nPossible issues:")
    print("1. Invalid API key")
    print("2. Network/firewall blocking Groq")
    print("3. Groq service is down")
    print("4. Check: https://status.groq.com/")
    exit(1)

