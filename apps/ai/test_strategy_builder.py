"""
Test script for strategy builder - converts natural language to backtestable strategies
"""
import asyncio
import json
from agents.strategy_translator import strategy_translator


async def test_strategy_builder():
    """Test the strategy builder with various descriptions"""
    
    test_cases = [
        {
            "description": "Buy when RSI is below 30 and sell when it goes above 70",
            "symbol": "AAPL",
            "name": "Simple RSI Oversold"
        },
        {
            "description": "Buy when price breaks above the 20-day moving average, exit when it breaks below",
            "symbol": "MSFT",
            "name": "20-Day SMA Breakout"
        },
        {
            "description": "MACD crossover - buy when MACD crosses above signal line, sell when it crosses below",
            "symbol": "TSLA",
            "name": "MACD Crossover"
        },
        {
            "description": "Buy on Bollinger band lower band touch with 5% stop loss and 15% take profit",
            "symbol": None,
            "name": "Bollinger Band Mean Reversion"
        },
        {
            "description": "trend following strategy: price above 50 SMA and 200 SMA, with MACD positive",
            "symbol": "QQQ",
            "name": "Multi-indicator Trend"
        }
    ]
    
    print("=" * 80)
    print("STRATEGY BUILDER TEST SUITE")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}] {test['name']}")
        print(f"Description: {test['description']}")
        print(f"Symbol: {test['symbol'] or 'N/A'}")
        print("-" * 80)
        
        try:
            strategy = await strategy_translator.translate_strategy(
                natural_language=test['description'],
                symbol=test['symbol']
            )
            
            if strategy.get('error'):
                print(f"❌ ERROR: {strategy['message']}")
                print(f"💡 Suggestion: {strategy['suggestion']}")
            else:
                print(f"✅ SUCCESS")
                print(f"   Name: {strategy['name']}")
                print(f"   Category: {strategy['category']}")
                print(f"   Difficulty: {strategy['difficulty']}")
                print(f"   Indicators: {[i['type'] for i in strategy['indicators']]}")
                print(f"   Entry Rules: {len(strategy['entry_rules'])} rule(s)")
                print(f"   Exit Rules: {len(strategy['exit_rules'])} rule(s)")
                print(f"   Stop Loss: {strategy['risk_management']['stop_loss_percent']*100:.1f}%")
                print(f"   Take Profit: {strategy['risk_management']['take_profit_percent']*100:.1f}%")
                print(f"\n   Full JSON:")
                print(json.dumps(strategy, indent=2))
                
        except ValueError as e:
            print(f"❌ ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)


async def test_invalid_strategies():
    """Test error handling with invalid/vague descriptions"""
    
    invalid_cases = [
        "something random",
        "buy",
        "very complicated multi-timeframe strategy with quantum mechanics"
    ]
    
    print("\n" + "=" * 80)
    print("INVALID STRATEGY TEST SUITE")
    print("=" * 80)
    
    for i, description in enumerate(invalid_cases, 1):
        print(f"\n[Invalid Test {i}] '{description}'")
        print("-" * 80)
        
        try:
            strategy = await strategy_translator.translate_strategy(
                natural_language=description,
                symbol=None
            )
            
            if strategy.get('error'):
                print(f"✅ ERROR CAUGHT (as expected)")
                print(f"   Message: {strategy['message']}")
                print(f"   Suggestion: {strategy['suggestion']}")
            else:
                print(f"⚠️  Strategy was generated (might be loose interpretation)")
                print(f"   Name: {strategy['name']}")
                
        except ValueError as e:
            print(f"✅ ERROR CAUGHT (as expected): {e}")
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("Starting Strategy Builder Tests...\n")
    asyncio.run(test_strategy_builder())
    asyncio.run(test_invalid_strategies())

