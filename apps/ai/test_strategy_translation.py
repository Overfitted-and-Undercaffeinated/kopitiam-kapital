#!/usr/bin/env python3
"""
Test script to debug strategy translation
"""
import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_strategy_translation():
    """Test what strategy JSON is generated for mean reversion"""
    try:
        from agents.strategy_translator import strategy_translator
        
        print("Testing strategy translation for 'mean reversion'...")
        
        # Test the translation
        strategy_def = await strategy_translator.translate_strategy(
            natural_language="mean reversion",
            symbol="AAPL"
        )
        
        print("\n=== Generated Strategy JSON ===")
        print(json.dumps(strategy_def, indent=2))
        
        print(f"\n=== Strategy Analysis ===")
        print(f"Name: {strategy_def.get('name')}")
        print(f"Description: {strategy_def.get('description')}")
        print(f"Indicators: {strategy_def.get('indicators')}")
        print(f"Entry Rules: {strategy_def.get('entry_rules')}")
        print(f"Exit Rules: {strategy_def.get('exit_rules')}")
        
        # Check if this looks like it would generate trades
        entry_rules = strategy_def.get('entry_rules', [])
        if not entry_rules:
            print("\n❌ PROBLEM: No entry rules!")
        else:
            print(f"\n✅ Has {len(entry_rules)} entry rule(s)")
            for i, rule in enumerate(entry_rules):
                print(f"  Rule {i+1}: {rule}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_strategy_translation())
