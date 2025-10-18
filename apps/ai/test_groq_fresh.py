"""Fresh test of Groq API with direct key"""
import sys
import os

# Clear any cached modules
if 'utils.config' in sys.modules:
    del sys.modules['utils.config']
if 'utils.clients' in sys.modules:
    del sys.modules['utils.clients']

# Force reload .env
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path, override=True)  # Override any existing env vars

# Direct test
from openai import OpenAI

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key length: {len(api_key)} characters")
print(f"API Key starts with: {api_key[:10]}...")
print(f"API Key ends with: ...{api_key[-10:]}")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

print("\nTesting Groq API...")

try:
    # Try current Groq models (as of Jan 2025)
    # Common models: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-instruct-v0.1
    model = "llama-3.3-70b-versatile"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Respond very briefly."},
            {"role": "user", "content": "Say hello in one word"}
        ],
        max_tokens=10,
        temperature=0.1
    )
    
    print(f"\n[SUCCESS!]")
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

