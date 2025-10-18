"""
Comprehensive tests for enhanced backtesting features
Tests strategy translation, VaR calculation, visual generation, and end-to-end flow
"""
import pytest
import asyncio
from datetime import datetime, timedelta

# Test data
SAMPLE_RETURNS = [0.05, -0.03, 0.02, -0.08, 0.04, -0.10, 0.06, 0.01, -0.02, 0.03]

# ============================================================================
# TEST 1: VaR Calculation
# ============================================================================

def test_var_calculation():
    """Test Value at Risk calculation"""
    from data.risk import calculate_var
    
    returns = SAMPLE_RETURNS
    
    # Test historical VaR
    var_95 = calculate_var(returns, 0.95, method="historical")
    assert var_95 < 0, "VaR should be negative (loss)"
    assert -0.15 < var_95 < 0, "VaR should be in reasonable range"
    
    # Test at different confidence levels
    var_99 = calculate_var(returns, 0.99, method="historical")
    assert var_99 <= var_95, "99% VaR should be worse than 95% VaR"
    
    print(f"✓ VaR calculation: 95%={var_95:.2%}, 99%={var_99:.2%}")

def test_cvar_calculation():
    """Test Conditional Value at Risk calculation"""
    from data.risk import calculate_cvar
    
    returns = SAMPLE_RETURNS
    
    # Test CVaR
    cvar_95 = calculate_cvar(returns, 0.95)
    assert cvar_95 < 0, "CVaR should be negative (loss)"
    
    # CVaR should be worse than or equal to VaR
    from data.risk import calculate_var
    var_95 = calculate_var(returns, 0.95)
    assert cvar_95 <= var_95, "CVaR should be worse than or equal to VaR"
    
    print(f"✓ CVaR calculation: {cvar_95:.2%}")

def test_risk_metrics_bundle():
    """Test comprehensive risk metrics calculation"""
    from data.risk import calculate_risk_metrics
    
    returns = SAMPLE_RETURNS
    
    metrics = calculate_risk_metrics(returns)
    
    # Check all expected keys exist
    expected_keys = ['var_95', 'var_99', 'cvar_95', 'cvar_99', 
                     'volatility', 'downside_deviation', 'max_loss', 'avg_loss']
    for key in expected_keys:
        assert key in metrics, f"Missing metric: {key}"
    
    # Sanity checks
    assert metrics['volatility'] > 0, "Volatility should be positive"
    assert metrics['max_loss'] < 0, "Max loss should be negative"
    assert metrics['var_99'] <= metrics['var_95'], "99% VaR should be worse"
    
    print(f"✓ Risk metrics bundle: volatility={metrics['volatility']:.2%}, max_loss={metrics['max_loss']:.2%}")

def test_empty_returns():
    """Test VaR with empty returns list"""
    from data.risk import calculate_var, calculate_cvar
    
    var = calculate_var([], 0.95)
    assert var == 0.0, "VaR of empty list should be 0"
    
    cvar = calculate_cvar([], 0.95)
    assert cvar == 0.0, "CVaR of empty list should be 0"
    
    print("✓ Empty returns handling")

# ============================================================================
# TEST 2: Strategy Translation
# ============================================================================

@pytest.mark.asyncio
async def test_strategy_translation_simple():
    """Test translating simple natural language strategies"""
    from agents.strategy_translator import strategy_translator
    
    test_cases = [
        "buy when RSI is below 30",
        "buy when price crosses above 50 day moving average",
        "buy on MACD bullish crossover"
    ]
    
    for description in test_cases:
        try:
            strategy_json = await strategy_translator.translate_strategy(
                natural_language=description,
                symbol="AAPL"
            )
            
            # Validate structure
            assert 'name' in strategy_json, "Strategy must have a name"
            assert 'entry_rules' in strategy_json, "Strategy must have entry rules"
            assert 'exit_rules' in strategy_json, "Strategy must have exit rules"
            assert 'indicators' in strategy_json, "Strategy must have indicators"
            
            # Validate rules
            assert len(strategy_json['entry_rules']) > 0, "Must have at least one entry rule"
            assert len(strategy_json['exit_rules']) > 0, "Must have at least one exit rule"
            
            print(f"✓ Translated: '{description}' -> {strategy_json['name']}")
        except Exception as e:
            print(f"✗ Failed to translate '{description}': {e}")
            raise

@pytest.mark.asyncio
async def test_strategy_translation_2week_low():
    """Test specific case: buy when price is below 2 week low"""
    from agents.strategy_translator import strategy_translator
    
    strategy_json = await strategy_translator.translate_strategy(
        natural_language="buy when price is below the 2 week low",
        symbol="NVDA"
    )
    
    # Validate it created indicators (should use SMA or similar)
    assert len(strategy_json['indicators']) > 0, "Should have indicators"
    
    # Validate entry rules reference price
    entry_rules = strategy_json['entry_rules']
    assert any('price' in str(rule.get('indicator', '')) for rule in entry_rules), \
        "Entry rules should reference price"
    
    print(f"✓ 2-week low strategy: {strategy_json['name']}")
    print(f"  Indicators: {[ind['type'] for ind in strategy_json['indicators']]}")
    print(f"  Entry rules: {entry_rules}")

@pytest.mark.asyncio
async def test_strategy_validation():
    """Test that translated strategies pass validation"""
    from agents.strategy_translator import strategy_translator
    from backtesting.builder import strategy_builder
    
    strategy_json = await strategy_translator.translate_strategy(
        natural_language="buy when RSI is below 30",
        symbol="AAPL"
    )
    
    # Validate with StrategyBuilder
    is_valid, error_msg = strategy_builder.validate_strategy(strategy_json)
    assert is_valid, f"Strategy should be valid: {error_msg}"
    
    print(f"✓ Strategy validation passed")

# ============================================================================
# TEST 3: Visual Data Generation
# ============================================================================

@pytest.mark.asyncio
async def test_equity_curve_generation():
    """Test equity curve data generation"""
    from backtesting.engine import BacktestEngine, Trade
    from datetime import datetime
    
    # Create sample trades
    trades = [
        Trade("AAPL", 100, datetime(2024, 1, 1), 95, 110, "BUY", 10),
        Trade("AAPL", 110, datetime(2024, 2, 1), 105, 120, "BUY", 10),
        Trade("AAPL", 105, datetime(2024, 3, 1), 100, 115, "BUY", 10)
    ]
    
    # Close trades
    trades[0].exit_price = 110
    trades[0].exit_date = datetime(2024, 1, 15)
    trades[0].pnl = (110 - 100) * 10
    trades[0].outcome = 'win'
    
    trades[1].exit_price = 105
    trades[1].exit_date = datetime(2024, 2, 15)
    trades[1].pnl = (105 - 110) * 10
    trades[1].outcome = 'loss'
    
    trades[2].exit_price = 115
    trades[2].exit_date = datetime(2024, 3, 15)
    trades[2].pnl = (115 - 105) * 10
    trades[2].outcome = 'win'
    
    # Generate equity curve
    engine = BacktestEngine()
    equity_curve = engine._generate_equity_curve(trades, 100000)
    
    # Validate
    assert len(equity_curve) == len(trades) + 1, "Should have start + trade exits"
    assert equity_curve[0]['equity'] == 100000, "Should start at initial capital"
    assert all('date' in point for point in equity_curve), "All points should have dates"
    assert all('equity' in point for point in equity_curve), "All points should have equity"
    
    print(f"✓ Equity curve generation: {len(equity_curve)} points")

@pytest.mark.asyncio
async def test_drawdown_calculation():
    """Test drawdown series generation"""
    from backtesting.engine import BacktestEngine
    
    # Sample equity curve
    equity_curve = [
        {'date': '2024-01-01', 'equity': 100000},
        {'date': '2024-02-01', 'equity': 110000},
        {'date': '2024-03-01', 'equity': 105000},
        {'date': '2024-04-01', 'equity': 115000}
    ]
    
    # Generate drawdown
    engine = BacktestEngine()
    drawdown_series = engine._generate_drawdown_series(equity_curve)
    
    # Validate
    assert len(drawdown_series) == len(equity_curve), "Should have same length as equity curve"
    assert drawdown_series[0]['drawdown'] == 0, "Should start at 0 drawdown"
    assert all(point['drawdown'] <= 0 for point in drawdown_series), "Drawdown should be non-positive"
    
    print(f"✓ Drawdown calculation: max={min(p['drawdown'] for p in drawdown_series):.2%}")

@pytest.mark.asyncio
async def test_monthly_returns():
    """Test monthly returns aggregation"""
    from backtesting.engine import BacktestEngine, Trade
    from datetime import datetime
    
    # Create trades across multiple months
    trades = [
        Trade("AAPL", 100, datetime(2024, 1, 1), 95, 110, "BUY", 10),
        Trade("AAPL", 110, datetime(2024, 1, 15), 105, 120, "BUY", 10),
        Trade("AAPL", 105, datetime(2024, 2, 1), 100, 115, "BUY", 10)
    ]
    
    # Set exit dates and PnL
    trades[0].exit_date = datetime(2024, 1, 10)
    trades[0].pnl_pct = 0.05
    
    trades[1].exit_date = datetime(2024, 1, 20)
    trades[1].pnl_pct = 0.03
    
    trades[2].exit_date = datetime(2024, 2, 15)
    trades[2].pnl_pct = -0.02
    
    # Generate monthly returns
    engine = BacktestEngine()
    monthly_returns = engine._generate_monthly_returns(trades)
    
    # Validate
    assert '2024-01' in monthly_returns, "Should have January returns"
    assert '2024-02' in monthly_returns, "Should have February returns"
    assert monthly_returns['2024-01'] == 0.08, "January should sum two trades"
    assert monthly_returns['2024-02'] == -0.02, "February should have one trade"
    
    print(f"✓ Monthly returns: {monthly_returns}")

# ============================================================================
# TEST 4: Backtest Explainer
# ============================================================================

@pytest.mark.asyncio
async def test_explanation_generation():
    """Test AI explanation generation"""
    from agents.backtest_explainer import backtest_explainer
    
    # Sample metrics
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
        strategy_description="Buy when RSI drops below 30",
        metrics=metrics,
        symbol="AAPL",
        period="2023-01-01 to 2025-01-01"
    )
    
    # Validate
    assert explanation is not None, "Should generate explanation"
    assert len(explanation) > 100, "Explanation should be substantial"
    assert "RSI" in explanation or "strategy" in explanation.lower(), "Should mention strategy"
    
    word_count = len(explanation.split())
    print(f"✓ Explanation generated: {word_count} words")
    print(f"  Preview: {explanation[:150]}...")

# ============================================================================
# TEST 5: End-to-End Backtest
# ============================================================================

@pytest.mark.asyncio
async def test_end_to_end_backtest():
    """Test complete end-to-end backtest with all features"""
    from backtesting.engine import BacktestEngine
    from backtesting.builder import strategy_builder
    from backtesting.templates import get_template
    from data.risk import calculate_var, calculate_cvar
    from agents.backtest_explainer import backtest_explainer
    
    # Use a pre-built template
    strategy_def = get_template('rsi_oversold')
    assert strategy_def is not None, "Template should exist"
    
    # Build strategy
    strategy_func = strategy_builder.build_strategy(strategy_def)
    
    # Run backtest with visuals
    engine = BacktestEngine()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    results = await engine.run_backtest(
        symbol="AAPL",
        start_date=start_date,
        end_date=end_date,
        strategy_fn=strategy_func,
        initial_capital=100000,
        include_visuals=True
    )
    
    # Validate core metrics
    assert 'total_return_pct' in results, "Should have return"
    assert 'win_rate' in results, "Should have win rate"
    assert 'sharpe_ratio' in results, "Should have Sharpe"
    assert 'num_trades' in results, "Should have trade count"
    
    # Validate visuals
    if results.get('num_trades', 0) > 0:
        assert 'visuals' in results, "Should have visuals"
        assert 'equity_curve' in results['visuals'], "Should have equity curve"
        assert 'drawdown_series' in results['visuals'], "Should have drawdown"
        assert 'monthly_returns' in results['visuals'], "Should have monthly returns"
        
        print(f"✓ Backtest executed: {results['num_trades']} trades")
        print(f"  Return: {results['total_return_pct']:.2%}")
        print(f"  Win rate: {results['win_rate']:.2%}")
        print(f"  Sharpe: {results['sharpe_ratio']:.2f}")
        print(f"  Visual data points: {len(results['visuals']['equity_curve'])}")
        
        # Calculate VaR
        returns = [t['pnl_pct'] for t in results['trades'] if t.get('pnl_pct')]
        if returns:
            var_95 = calculate_var(returns, 0.95)
            cvar_95 = calculate_cvar(returns, 0.95)
            print(f"  VaR (95%): {var_95:.2%}")
            print(f"  CVaR (95%): {cvar_95:.2%}")
            
            # Generate explanation
            explanation = await backtest_explainer.generate_explanation(
                strategy_name=strategy_def['name'],
                strategy_description=strategy_def['description'],
                metrics=results,
                symbol="AAPL",
                period=f"{start_date} to {end_date}"
            )
            
            assert explanation is not None, "Should generate explanation"
            print(f"  Explanation: {len(explanation.split())} words")
    else:
        print("⚠ No trades generated (this can happen with recent data)")

# ============================================================================
# TEST 6: Natural Language End-to-End
# ============================================================================

@pytest.mark.asyncio
async def test_natural_language_end_to_end():
    """Test complete workflow with natural language input"""
    from agents.strategy_translator import strategy_translator
    from backtesting.engine import BacktestEngine
    from backtesting.builder import strategy_builder
    
    # Step 1: Translate
    strategy_def = await strategy_translator.translate_strategy(
        natural_language="buy when RSI is below 30",
        symbol="NVDA"
    )
    
    print(f"✓ Step 1 - Translated to: {strategy_def['name']}")
    
    # Step 2: Build
    strategy_func = strategy_builder.build_strategy(strategy_def)
    print(f"✓ Step 2 - Strategy function built")
    
    # Step 3: Backtest
    engine = BacktestEngine()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    results = await engine.run_backtest(
        symbol="NVDA",
        start_date=start_date,
        end_date=end_date,
        strategy_fn=strategy_func,
        initial_capital=100000,
        include_visuals=True
    )
    
    print(f"✓ Step 3 - Backtest completed: {results['num_trades']} trades")
    
    # Step 4: Risk metrics
    from data.risk import calculate_var, calculate_cvar
    returns = [t['pnl_pct'] for t in results['trades'] if t.get('pnl_pct')]
    if returns:
        var_95 = calculate_var(returns, 0.95)
        cvar_95 = calculate_cvar(returns, 0.95)
        print(f"✓ Step 4 - Risk metrics: VaR={var_95:.2%}, CVaR={cvar_95:.2%}")
    
    # Step 5: Explanation
    from agents.backtest_explainer import backtest_explainer
    explanation = await backtest_explainer.generate_explanation(
        strategy_name=strategy_def['name'],
        strategy_description=strategy_def['description'],
        metrics=results,
        symbol="NVDA",
        period=f"{start_date} to {end_date}"
    )
    
    print(f"✓ Step 5 - Explanation generated: {len(explanation)} chars")
    print(f"\n{'='*60}")
    print("COMPLETE WORKFLOW SUCCESS")
    print(f"{'='*60}")

# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ENHANCED BACKTESTING TEST SUITE")
    print("="*60 + "\n")
    
    # Run synchronous tests
    print("TEST 1: VaR Calculation")
    print("-" * 60)
    test_var_calculation()
    test_cvar_calculation()
    test_risk_metrics_bundle()
    test_empty_returns()
    
    # Run async tests
    print("\nTEST 2: Strategy Translation")
    print("-" * 60)
    asyncio.run(test_strategy_translation_simple())
    asyncio.run(test_strategy_translation_2week_low())
    asyncio.run(test_strategy_validation())
    
    print("\nTEST 3: Visual Data Generation")
    print("-" * 60)
    asyncio.run(test_equity_curve_generation())
    asyncio.run(test_drawdown_calculation())
    asyncio.run(test_monthly_returns())
    
    print("\nTEST 4: Backtest Explainer")
    print("-" * 60)
    asyncio.run(test_explanation_generation())
    
    print("\nTEST 5: End-to-End Backtest")
    print("-" * 60)
    asyncio.run(test_end_to_end_backtest())
    
    print("\nTEST 6: Natural Language End-to-End")
    print("-" * 60)
    asyncio.run(test_natural_language_end_to_end())
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60 + "\n")

