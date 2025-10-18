#!/usr/bin/env python3
"""
Test script to debug rule evaluation in strategy builder
"""
import sys
import os
import pandas as pd
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rule_evaluation():
    """Test if rule evaluation is working"""
    try:
        from data.indicators import add_indicators_to_dataframe
        from backtesting.builder import StrategyBuilder
        
        print("Testing rule evaluation...")
        
        # Create realistic mock data with some volatility
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        
        np.random.seed(42)
        base_price = 100
        price_changes = np.random.normal(0, 2, 50)
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] + change
            prices.append(max(new_price, 50))
        
        mock_data = pd.DataFrame({
            'open': prices,
            'high': [p + np.random.uniform(0, 2) for p in prices],
            'low': [p - np.random.uniform(0, 2) for p in prices],
            'close': prices,
            'volume': [1000000] * 50
        }, index=dates)
        
        # Normalize column names
        data = mock_data.copy()
        data.columns = data.columns.str.lower()
        
        # Add RSI indicator
        indicators = [{"type": "rsi", "period": 14}]
        data = add_indicators_to_dataframe(data, indicators)
        
        print(f"Data columns: {data.columns.tolist()}")
        print(f"Data shape: {data.shape}")
        
        # Test rule evaluation
        builder = StrategyBuilder()
        
        # Test the entry rule: RSI < 30
        entry_rules = [{"indicator": "rsi", "condition": "<", "value": 30}]
        
        print(f"\nTesting entry rules: {entry_rules}")
        
        # Test on the last row (most recent data)
        current = data.iloc[-1]
        print(f"Current RSI value: {current.get('rsi', 'N/A')}")
        
        # Evaluate the rule
        should_enter = builder._evaluate_rules(entry_rules, current, data)
        print(f"Should enter trade: {should_enter}")
        
        # Test on all rows to see when rules trigger
        print(f"\nTesting rule evaluation on all rows:")
        trigger_count = 0
        for i in range(len(data)):
            row = data.iloc[i]
            rsi_val = row.get('rsi')
            if pd.notna(rsi_val):
                should_enter_row = builder._evaluate_rules(entry_rules, row, data)
                if should_enter_row:
                    trigger_count += 1
                    print(f"  Row {i}: RSI={rsi_val:.2f}, Should enter: {should_enter_row}")
        
        print(f"\nTotal trigger count: {trigger_count}")
        
        if trigger_count == 0:
            print("❌ No rules triggered - this explains why no trades are generated!")
        else:
            print(f"✅ {trigger_count} rules triggered - should generate trades")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rule_evaluation()
