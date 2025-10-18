"""
Quick Integration Test - Validates all components work together
Fast execution - no full backtests
"""
import asyncio
import sys

print("="*60)
print("QUICK INTEGRATION TEST")
print("="*60)

# Test 1: VaR/CVaR calculations
print("\n[1/5] Testing VaR & CVaR calculations...")
try:
    from data.risk import calculate_var, calculate_cvar
    
    test_returns = [0.05, -0.03, 0.02, -0.08, 0.04, -0.10, 0.06]
    var_95 = calculate_var(test_returns, 0.95)
    cvar_95 = calculate_cvar(test_returns, 0.95)
    
    assert var_95 < 0, "VaR should be negative"
    assert cvar_95 <= var_95, "CVaR should be worse than VaR"
    
    print(f"  ✓ VaR (95%): {var_95:.2%}")
    print(f"  ✓ CVaR (95%): {cvar_95:.2%}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 2: Strategy Translation
print("\n[2/5] Testing Strategy Translator...")
try:
    from agents.strategy_translator import strategy_translator
    
    async def test_translation():
        strategy = await strategy_translator.translate_strategy(
            natural_language="buy when RSI is below 30",
            symbol="AAPL"
        )
        assert 'name' in strategy
        assert 'entry_rules' in strategy
        assert 'exit_rules' in strategy
        return strategy
    
    strategy = asyncio.run(test_translation())
    print(f"  ✓ Translated to: {strategy['name']}")
    print(f"  ✓ Has {len(strategy['indicators'])} indicators")
    print(f"  ✓ Has {len(strategy['entry_rules'])} entry rules")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 3: Backtest Engine with Visuals
print("\n[3/5] Testing Backtest Engine...")
try:
    from backtesting.engine import BacktestEngine, Trade
    from datetime import datetime
    
    # Create mock trades
    engine = BacktestEngine()
    trades = [
        Trade("AAPL", 100, datetime(2024, 1, 1), 95, 110, "BUY", 10),
        Trade("AAPL", 110, datetime(2024, 2, 1), 105, 120, "BUY", 10),
    ]
    
    trades[0].exit_price = 110
    trades[0].exit_date = datetime(2024, 1, 15)
    trades[0].pnl = 100
    trades[0].pnl_pct = 0.10
    trades[0].outcome = 'win'
    
    trades[1].exit_price = 105
    trades[1].exit_date = datetime(2024, 2, 15)
    trades[1].pnl = -50
    trades[1].pnl_pct = -0.045
    trades[1].outcome = 'loss'
    
    # Test visual generation
    equity_curve = engine._generate_equity_curve(trades, 100000)
    drawdown = engine._generate_drawdown_series(equity_curve)
    monthly = engine._generate_monthly_returns(trades)
    
    assert len(equity_curve) > 0, "Equity curve should have data"
    assert len(drawdown) > 0, "Drawdown should have data"
    
    print(f"  ✓ Equity curve: {len(equity_curve)} points")
    print(f"  ✓ Drawdown series: {len(drawdown)} points")
    print(f"  ✓ Monthly returns: {len(monthly)} months")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 4: Backtest Explainer
print("\n[4/5] Testing Backtest Explainer...")
try:
    from agents.backtest_explainer import backtest_explainer
    
    async def test_explainer():
        metrics = {
            'win_rate': 0.67,
            'sharpe_ratio': 1.85,
            'total_return_pct': 0.23,
            'max_drawdown': -0.08,
            'num_trades': 45,
            'profit_factor': 1.8,
            'avg_win': 250,
            'avg_loss': 150,
            'winning_trades': 30,
            'losing_trades': 15
        }
        
        explanation = await backtest_explainer.generate_explanation(
            strategy_name="RSI Oversold",
            strategy_description="Buy when RSI < 30",
            metrics=metrics,
            symbol="AAPL",
            period="2023-01-01 to 2025-01-01"
        )
        
        assert len(explanation) > 100, "Explanation should be substantial"
        return explanation
    
    explanation = asyncio.run(test_explainer())
    word_count = len(explanation.split())
    print(f"  ✓ Generated explanation: {word_count} words")
    print(f"  ✓ Preview: {explanation[:100]}...")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 5: Strategy Builder Integration
print("\n[5/5] Testing Strategy Builder...")
try:
    from backtesting.builder import strategy_builder
    from backtesting.templates import get_template
    
    # Get a template
    template = get_template('rsi_oversold')
    assert template is not None, "Template should exist"
    
    # Validate it
    is_valid, error = strategy_builder.validate_strategy(template)
    assert is_valid, f"Template should be valid: {error}"
    
    # Build it
    strategy_func = strategy_builder.build_strategy(template)
    assert callable(strategy_func), "Should return a function"
    
    print(f"  ✓ Template: {template['name']}")
    print(f"  ✓ Validation: passed")
    print(f"  ✓ Build: successful")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL INTEGRATION TESTS PASSED")
print("="*60)
print("\nComponents Verified:")
print("  ✓ VaR/CVaR calculations")
print("  ✓ Strategy Translator (Groq)")
print("  ✓ Backtest Engine with visuals")
print("  ✓ Backtest Explainer (Groq)")
print("  ✓ Strategy Builder")
print("\n✨ Feature is ready to use!")
print("\nTo test the full API endpoint:")
print("  python example_enhanced_backtest.py")

