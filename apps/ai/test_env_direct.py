"""Direct .env file parsing to debug"""
from pathlib import Path

env_path = Path(__file__).parent.parent.parent / ".env"

print("Reading .env file directly...")
print(f"Path: {env_path}\n")

with open(env_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines[:10], 1):
    if 'GROQ' in line:
        print(f"Line {i}: {line.strip()}")
        print(f"Length of line: {len(line.strip())}")
        
        # Extract key
        if '=' in line:
            key, value = line.strip().split('=', 1)
            print(f"Key: {key}")
            print(f"Value: {value}")
            print(f"Value length: {len(value)}")
            print(f"Value repr: {repr(value)}")

# Now try with python-dotenv
print("\n" + "="*60)
print("Testing with python-dotenv:")
print("="*60)

from dotenv import dotenv_values

config = dotenv_values(env_path)
groq_key = config.get('GROQ_API_KEY', 'NOT FOUND')
print(f"GROQ_API_KEY from dotenv_values: {groq_key}")
print(f"Length: {len(groq_key)}")

# Try load_dotenv
print("\n" + "="*60)
print("Testing with load_dotenv:")
print("="*60)

import os
from dotenv import load_dotenv

# Clear env
if 'GROQ_API_KEY' in os.environ:
    del os.environ['GROQ_API_KEY']

load_dotenv(env_path, override=True)
groq_from_env = os.getenv('GROQ_API_KEY', 'NOT FOUND')
print(f"GROQ_API_KEY from os.getenv: {groq_from_env}")
print(f"Length: {len(groq_from_env)}")

