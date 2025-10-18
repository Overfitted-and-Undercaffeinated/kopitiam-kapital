#!/usr/bin/env python3
"""
Test script to debug backtest simulation loop
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_backtest_debug():
    """Debug the backtest simulation loop"""
    try:
        from agents.strategy_translator import strategy_translator
        from backtesting.builder import strategy_builder
        from backtesting.engine import BacktestEngine
        
        print("Debugging backtest simulation loop...")
        
        # Get strategy definition
        strategy_def = await strategy_translator.translate_strategy(
            natural_language="mean reversion",
            symbol="AAPL"
        )
        
        print(f"Strategy: {strategy_def['name']}")
        
        # Build strategy function
        strategy_func = await strategy_builder.build_strategy(strategy_def)
        print("✅ Strategy function built")
        
        # Test the strategy function directly with a small dataset
        print("\nTesting strategy function directly...")
        
        # Import market data service to get real AAPL data
        try:
            from data.market_data import market_data_service
            
            # Get a small amount of AAPL data
            data = await market_data_service.get_ohlcv(
                symbol="AAPL",
                period="max"
            )
            
            if data is None or data.empty:
                print("❌ No data available for AAPL")
                return
                
            # Filter to last 30 days for testing
            data = data.tail(30)
            print(f"Using {len(data)} days of AAPL data")
            print(f"Date range: {data.index[0]} to {data.index[-1]}")
            
            # Test the strategy function on this data
            signal = await strategy_func(data)
            print(f"Strategy signal: {signal}")
            
            if signal:
                print("✅ Strategy generated a signal!")
            else:
                print("❌ Strategy did not generate a signal")
                
        except Exception as e:
            print(f"Error getting market data: {e}")
            return
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_backtest_debug())