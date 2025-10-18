#!/usr/bin/env python3
"""
Test script to debug indicators calculation
"""
import sys
import os
import pandas as pd
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_indicators():
    """Test if RSI indicator calculation works"""
    try:
        from data.indicators import add_indicators_to_dataframe
        
        print("Testing indicators calculation...")
        
        # Create more realistic mock data with some volatility
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        
        # Create data with some ups and downs to generate RSI values
        np.random.seed(42)
        base_price = 100
        price_changes = np.random.normal(0, 2, 50)  # Random price changes
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] + change
            prices.append(max(new_price, 50))  # Keep prices positive
        
        mock_data = pd.DataFrame({
            'open': prices,
            'high': [p + np.random.uniform(0, 2) for p in prices],
            'low': [p - np.random.uniform(0, 2) for p in prices],
            'close': prices,
            'volume': [1000000] * 50
        }, index=dates)
        
        print(f"Mock data shape: {mock_data.shape}")
        print(f"Price range: {mock_data['close'].min():.2f} - {mock_data['close'].max():.2f}")
        
        # Test adding RSI indicator
        indicators = [{"type": "rsi", "period": 14}]
        
        print(f"\nAdding indicators: {indicators}")
        
        # Normalize column names (yfinance uses Capital, we need lowercase)
        data = mock_data.copy()
        data.columns = data.columns.str.lower()
        
        # Add indicators
        result_data = add_indicators_to_dataframe(data, indicators)
        
        print(f"Result columns: {result_data.columns.tolist()}")
        
        # Check if RSI was added
        if 'rsi' in result_data.columns:
            print("✅ RSI indicator added successfully!")
            
            # Check RSI values
            rsi_values = result_data['rsi'].dropna()
            print(f"RSI values (last 10): {rsi_values.tail(10).tolist()}")
            print(f"RSI range: {rsi_values.min():.2f} - {rsi_values.max():.2f}")
            
            # Check if any RSI values are below 30 (oversold)
            oversold_count = (rsi_values < 30).sum()
            print(f"Oversold RSI values (< 30): {oversold_count}")
            
            # Check if any RSI values are above 70 (overbought)
            overbought_count = (rsi_values > 70).sum()
            print(f"Overbought RSI values (> 70): {overbought_count}")
            
        else:
            print("❌ RSI indicator not found in result!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_indicators()
