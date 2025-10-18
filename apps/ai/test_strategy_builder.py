#!/usr/bin/env python3
"""
Comprehensive test suite for strategy builder
Tests translation, execution, and returns chart-ready data
"""
import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

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


async def test_strategy_backtest(strategies):
    """Run actual backtests with real market data and generate visualizations"""
    from backtesting.builder import strategy_builder
    from backtesting.engine import BacktestEngine
    
    print("\n" + "=" * 80)
    print("STRATEGY BACKTEST & VISUALIZATION SUITE")
    print("=" * 80)
    
    # Backtest parameters
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')  # 2 years
    initial_capital = 100000.0
    
    print(f"\nBacktest Period: {start_date} to {end_date}")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    
    engine = BacktestEngine()
    backtest_results = []
    
    for i, strategy_def in enumerate(strategies, 1):
        strategy_name = strategy_def['name']
        symbol = strategy_def.get('symbol', 'AAPL')  # Default to AAPL if not specified
        
        print(f"\n[Backtest {i}/{len(strategies)}] {strategy_name} on {symbol}")
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
            print("✅ Strategy function built")
            
            # Run backtest
            print(f"⏳ Running backtest...")
            results = await engine.run_backtest(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                strategy_fn=strategy_func,
                initial_capital=initial_capital,
                include_visuals=True
            )
            
            print(f"✅ Backtest complete!")
            print(f"   Trades: {results['num_trades']}")
            print(f"   Win Rate: {results['win_rate']*100:.1f}%")
            print(f"   Total Return: ${results['total_return']:,.2f} ({results['total_return_pct']*100:.2f}%)")
            print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            print(f"   Max Drawdown: {results['max_drawdown']*100:.2f}%")
            
            # Show chart data availability
            if results['num_trades'] > 0 and 'visuals' in results:
                equity_points = len(results['visuals'].get('equity_curve', []))
                drawdown_points = len(results['visuals'].get('drawdown_series', []))
                print(f"   📊 Chart data ready:")
                print(f"      - Equity curve: {equity_points} data points")
                print(f"      - Drawdown series: {drawdown_points} data points")
                print(f"      - Use BacktestChart component in frontend to visualize")
            else:
                print(f"   ⚠️  No trades generated - no chart data")
            
            backtest_results.append({
                'name': strategy_name,
                'symbol': symbol,
                'results': results,
                'status': 'success'
            })
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            backtest_results.append({
                'name': strategy_name,
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            })
    
    print("\n" + "=" * 80)
    success_count = sum(1 for r in backtest_results if r['status'] == 'success')
    trades_count = sum(r['results']['num_trades'] for r in backtest_results 
                      if r['status'] == 'success')
    print(f"Backtest Complete: {success_count}/{len(strategies)} strategies tested")
    print(f"Total Trades: {trades_count}")
    print("=" * 80)
    
    return backtest_results


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
    
    # Test 2: Backtesting with visualizations (only if we have successful translations)
    if strategies:
        # Store symbol in strategy def for backtest
        for i, strategy in enumerate(strategies):
            if i == 0:
                strategy['symbol'] = 'AAPL'
            elif i == 1:
                strategy['symbol'] = 'MSFT'
            elif i == 2:
                strategy['symbol'] = 'TSLA'
            else:
                strategy['symbol'] = 'GOOGL'
        
        await test_strategy_backtest(strategies)
    else:
        print("\n⚠️  Skipping backtest tests - no strategies translated successfully")
    
    # Test 3: Error handling
    await test_invalid_strategies()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETE")
    print("📊 Chart data is ready - use BacktestChart component to visualize in frontend")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
