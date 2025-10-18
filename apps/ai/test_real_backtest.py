#!/usr/bin/env python3
"""
Test script to debug real backtest with AAPL data
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_real_backtest():
    """Test backtest with real AAPL data"""
    try:
        from agents.strategy_translator import strategy_translator
        from backtesting.builder import strategy_builder
        from backtesting.engine import BacktestEngine
        
        print("Testing real backtest with AAPL data...")
        
        # Get strategy definition
        strategy_def = await strategy_translator.translate_strategy(
            natural_language="mean reversion",
            symbol="AAPL"
        )
        
        print(f"Strategy: {strategy_def['name']}")
        
        # Build strategy function
        strategy_func = await strategy_builder.build_strategy(strategy_def)
        print("✅ Strategy function built")
        
        # Test with real AAPL data
        engine = BacktestEngine()
        
        print("Running backtest...")
        result = await engine.run_backtest(
            symbol="AAPL",
            start_date="2023-10-20",
            end_date="2025-10-19",
            strategy_fn=strategy_func,
            initial_capital=100000.0,
            include_visuals=True
        )
        
        print(f"\n=== Backtest Results ===")
        print(f"Total trades: {result.get('num_trades', 0)}")
        print(f"Total return: {result.get('total_return_pct', 0)*100:.2f}%")
        print(f"Win rate: {result.get('win_rate', 0)*100:.2f}%")
        
        trades = result.get('trades', [])
        if trades:
            print(f"First few trades:")
            for i, trade in enumerate(trades[:3]):
                print(f"  Trade {i+1}: {trade}")
        else:
            print("❌ No trades generated!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_backtest())
