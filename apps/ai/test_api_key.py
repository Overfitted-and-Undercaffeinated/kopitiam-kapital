"""Quick test to verify API key loading"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
print(f"Loading .env from: {env_path}")
print(f"File exists: {env_path.exists()}")

load_dotenv(env_path)

# Check what API key is loaded
groq_key = os.getenv("GROQ_API_KEY")
print(f"\nGROQ_API_KEY loaded: {groq_key[:20]}...{groq_key[-10:] if groq_key else 'None'}")
print(f"Full length: {len(groq_key) if groq_key else 0} characters")

# Test with OpenAI SDK
try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=groq_key,
        base_url="https://api.groq.com/openai/v1"
    )
    
    print("\n[OK] Client created successfully")
    print(f"Base URL: {client.base_url}")
    
    # Try a simple API call
    print("\nTesting API call...")
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": "Say 'hello' in one word"}],
        max_tokens=5
    )
    
    print(f"[OK] API call successful!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\n[ERROR] {e}")

