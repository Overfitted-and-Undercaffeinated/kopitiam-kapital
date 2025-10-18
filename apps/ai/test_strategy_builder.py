#!/usr/bin/env python3
"""
Test script to debug strategy builder
"""
import asyncio
import json
import sys
import os
import pandas as pd

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_strategy_builder():
    """Test if the strategy builder can create an executable function"""
    try:
        from agents.strategy_translator import strategy_translator
        from backtesting.builder import strategy_builder
        
        print("Testing strategy builder...")
        
        # First get the strategy JSON
        strategy_def = await strategy_translator.translate_strategy(
            natural_language="mean reversion",
            symbol="AAPL"
        )
        
        print(f"Strategy: {strategy_def['name']}")
        
        # Build the strategy function
        strategy_func = await strategy_builder.build_strategy(strategy_def)
        print("✅ Strategy function built successfully")
        
        # Test with some mock data
        print("\nTesting with mock data...")
        
        # Create mock OHLCV data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        mock_data = pd.DataFrame({
            'open': [100 + i for i in range(100)],
            'high': [105 + i for i in range(100)],
            'low': [95 + i for i in range(100)],
            'close': [102 + i for i in range(100)],
            'volume': [1000000] * 100
        }, index=dates)
        
        print(f"Mock data shape: {mock_data.shape}")
        print(f"Mock data columns: {mock_data.columns.tolist()}")
        
        # Test the strategy function
        try:
            signal = await strategy_func(mock_data)
            print(f"Strategy signal: {signal}")
            
            if signal:
                print("✅ Strategy generated a signal!")
            else:
                print("❌ Strategy did not generate a signal")
                
        except Exception as e:
            print(f"❌ Error running strategy function: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_strategy_builder())
