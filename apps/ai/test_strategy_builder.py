#!/usr/bin/env python3
"""
Comprehensive test suite for strategy builder
Tests both translation and execution capabilities
"""
import asyncio
import json
import sys
import os
import pandas as pd

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_strategy_translation():
    """Test the strategy translation with various descriptions"""
    from agents.strategy_translator import strategy_translator
    
    test_cases = [
        {
            "description": "mean reversion",
            "symbol": "AAPL",
            "name": "Mean Reversion (Simple)"
        },
        {
            "description": "Buy when RSI is below 30 and sell when it goes above 70",
            "symbol": "AAPL",
            "name": "RSI Oversold/Overbought"
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
            "symbol": "GOOGL",
            "name": "Bollinger Band Mean Reversion"
        }
    ]
    
    print("=" * 80)
    print("STRATEGY TRANSLATION TEST SUITE")
    print("=" * 80)
    
    successful_strategies = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}] {test['name']}")
        print(f"Description: {test['description']}")
        print(f"Symbol: {test['symbol']}")
        print("-" * 80)
        
        try:
            strategy = await strategy_translator.translate_strategy(
                natural_language=test['description'],
                symbol=test['symbol']
            )
            
            print(f"✅ SUCCESS")
            print(f"   Name: {strategy['name']}")
            print(f"   Category: {strategy['category']}")
            print(f"   Indicators: {[i['type'] for i in strategy['indicators']]}")
            print(f"   Entry Rules: {len(strategy['entry_rules'])} rule(s)")
            print(f"   Exit Rules: {len(strategy['exit_rules'])} rule(s)")
            print(f"   Stop Loss: {strategy['risk_management']['stop_loss_percent']*100:.1f}%")
            print(f"   Take Profit: {strategy['risk_management']['take_profit_percent']*100:.1f}%")
            
            successful_strategies.append(strategy)
                
        except ValueError as e:
            print(f"❌ ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"Translation Tests Complete: {len(successful_strategies)}/{len(test_cases)} passed")
    print("=" * 80)
    
    return successful_strategies


async def test_strategy_execution(strategies):
    """Test if translated strategies can be executed with mock data"""
    from backtesting.builder import strategy_builder
    
    print("\n" + "=" * 80)
    print("STRATEGY EXECUTION TEST SUITE")
    print("=" * 80)
    
    # Create mock OHLCV data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    mock_data = pd.DataFrame({
        'open': [100 + i*0.5 for i in range(100)],
        'high': [105 + i*0.5 for i in range(100)],
        'low': [95 + i*0.5 for i in range(100)],
        'close': [102 + i*0.5 for i in range(100)],
        'volume': [1000000] * 100
    }, index=dates)
    
    print(f"\nMock data:")
    print(f"  Shape: {mock_data.shape}")
    print(f"  Columns: {mock_data.columns.tolist()}")
    print(f"  Date range: {mock_data.index[0]} to {mock_data.index[-1]}")
    
    execution_results = []
    
    for i, strategy_def in enumerate(strategies, 1):
        print(f"\n[Execution Test {i}/{len(strategies)}] {strategy_def['name']}")
        print("-" * 80)
        
        try:
            # Validate strategy structure
            is_valid, error_msg = strategy_builder.validate_strategy(strategy_def)
            if not is_valid:
                print(f"❌ VALIDATION FAILED: {error_msg}")
                continue
            
            print("✅ Strategy structure is valid")
            
            # Build the strategy function
            strategy_func = await strategy_builder.build_strategy(strategy_def)
            print("✅ Strategy function built successfully")
            
            # Test the strategy function with mock data
            signal = await strategy_func(mock_data)
            print(f"   Signal generated: {signal}")
            
            if signal:
                print("✅ Strategy generated a signal!")
                execution_results.append({
                    "name": strategy_def['name'],
                    "signal": signal,
                    "status": "success"
                })
            else:
                print("⚠️  Strategy did not generate a signal (might need different market conditions)")
                execution_results.append({
                    "name": strategy_def['name'],
                    "signal": None,
                    "status": "no_signal"
                })
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            execution_results.append({
                "name": strategy_def['name'],
                "signal": None,
                "status": "error",
                "error": str(e)
            })
    
    print("\n" + "=" * 80)
    success_count = sum(1 for r in execution_results if r['status'] == 'success')
    print(f"Execution Tests Complete: {success_count}/{len(strategies)} generated signals")
    print("=" * 80)
    
    return execution_results


async def test_invalid_strategies():
    """Test error handling with invalid/vague descriptions"""
    from agents.strategy_translator import strategy_translator
    
    invalid_cases = [
        "",
        "buy",
        "something random that makes no sense",
    ]
    
    print("\n" + "=" * 80)
    print("INVALID STRATEGY TEST SUITE")
    print("=" * 80)
    
    for i, description in enumerate(invalid_cases, 1):
        print(f"\n[Invalid Test {i}/{len(invalid_cases)}] '{description}'")
        print("-" * 80)
        
        try:
            strategy = await strategy_translator.translate_strategy(
                natural_language=description,
                symbol="AAPL"
            )
            
            print(f"⚠️  Strategy was generated (loose interpretation)")
            print(f"   Name: {strategy['name']}")
                
        except ValueError as e:
            print(f"✅ ERROR CAUGHT (as expected): {e}")
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")
    
    print("\n" + "=" * 80)
    print("Invalid Strategy Tests Complete")
    print("=" * 80)


async def main():
    """Run all tests"""
    print("\n🧪 STRATEGY BUILDER COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Test 1: Translation
    strategies = await test_strategy_translation()
    
    # Test 2: Execution (only if we have successful translations)
    if strategies:
        await test_strategy_execution(strategies)
    else:
        print("\n⚠️  Skipping execution tests - no strategies translated successfully")
    
    # Test 3: Error handling
    await test_invalid_strategies()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
