#!/usr/bin/env python3
"""
Test script to check AAPL raw data
"""
import asyncio
import sys
import os
import pandas as pd

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_aapl_data():
    """Check AAPL raw data to see if it's valid"""
    try:
        from data.market_data import market_data_service
        
        print("Checking AAPL raw data...")
        
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
        
        print(f"\nData columns: {data.columns.tolist()}")
        print(f"Data types:\n{data.dtypes}")
        
        print(f"\nFirst 5 rows:")
        print(data.head())
        
        print(f"\nLast 5 rows:")
        print(data.tail())
        
        # Check for any obvious issues
        print(f"\nData analysis:")
        print(f"Close price range: {data['Close'].min():.2f} - {data['Close'].max():.2f}")
        print(f"Any null values: {data.isnull().sum().sum()}")
        print(f"Any duplicate dates: {data.index.duplicated().sum()}")
        
        # Check if prices are realistic
        if data['Close'].min() < 0:
            print("❌ Negative prices found!")
        if data['Close'].max() > 1000:
            print("⚠️  Very high prices - might be data issue")
        if data['Close'].std() == 0:
            print("❌ No price variation - all prices are the same!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_aapl_data())
