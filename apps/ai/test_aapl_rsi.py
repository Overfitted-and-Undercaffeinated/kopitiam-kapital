#!/usr/bin/env python3
"""
Test script to check AAPL RSI values
"""
import asyncio
import sys
import os
import pandas as pd

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_aapl_rsi():
    """Check AAPL RSI values to see if any are oversold"""
    try:
        from data.market_data import market_data_service
        from data.indicators import add_indicators_to_dataframe
        
        print("Checking AAPL RSI values...")
        
        # Get AAPL data
        data = await market_data_service.get_ohlcv(
            symbol="AAPL",
            period="max"
        )
        
        if data is None or data.empty:
            print("❌ No data available for AAPL")
            return
            
        print(f"Got {len(data)} days of AAPL data")
        print(f"Date range: {data.index[0]} to {data.index[-1]}")
        
        # Add RSI indicator
        data.columns = data.columns.str.lower()
        indicators = [{"type": "rsi", "period": 14}]
        data_with_rsi = add_indicators_to_dataframe(data, indicators)
        
        # Check RSI values
        rsi_values = data_with_rsi['rsi'].dropna()
        print(f"\nRSI Analysis:")
        print(f"Total RSI values: {len(rsi_values)}")
        print(f"RSI range: {rsi_values.min():.2f} - {rsi_values.max():.2f}")
        print(f"RSI mean: {rsi_values.mean():.2f}")
        
        # Check oversold values
        oversold_count = (rsi_values < 30).sum()
        print(f"Oversold RSI values (< 30): {oversold_count}")
        
        if oversold_count > 0:
            oversold_dates = rsi_values[rsi_values < 30]
            print(f"Oversold dates: {oversold_dates.head(10).to_dict()}")
        
        # Check recent RSI values
        recent_rsi = rsi_values.tail(10)
        print(f"\nRecent RSI values (last 10):")
        for date, rsi in recent_rsi.items():
            print(f"  {date}: {rsi:.2f}")
        
        # Check if we need more historical data
        if oversold_count == 0:
            print(f"\n❌ No oversold RSI values found in the dataset!")
            print(f"This explains why no trades are generated.")
            print(f"The mean reversion strategy needs RSI < 30 to trigger buy signals.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_aapl_rsi())
