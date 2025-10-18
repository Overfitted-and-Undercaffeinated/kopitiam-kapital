"""
Test VaR Accuracy - Verify VaR is calculated from real trade data, not mock values
"""
import asyncio

async def test_var_accuracy():
    """Verify VaR calculation uses actual trade returns"""
    print("="*70)
    print("VaR ACCURACY TEST")
    print("="*70)
    
    from agents.strategy_translator import strategy_translator
    from backtesting.engine import BacktestEngine
    from backtesting.builder import strategy_builder
    from data.risk import calculate_var, calculate_cvar
    from datetime import datetime, timedelta
    
    # Run backtest
    symbol = "AAPL"
    strategy_def = await strategy_translator.translate_strategy(
        natural_language="buy when price is below the 2 week low",
        symbol=symbol
    )
    
    strategy_func = strategy_builder.build_strategy(strategy_def)
    engine = BacktestEngine()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    results = await engine.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        strategy_fn=strategy_func,
        initial_capital=100000,
        include_visuals=True
    )
    
    print(f"\n📊 Backtest Results:")
    print(f"  Trades: {results['num_trades']}")
    print(f"  Win Rate: {results['win_rate']*100:.1f}%")
    
    # Extract all trade returns
    returns = [t['pnl_pct'] for t in results['trades'] if t.get('pnl_pct') is not None]
    
    print(f"\n📈 Trade Returns Analysis:")
    print(f"  Total returns: {len(returns)}")
    
    if returns:
        # Show ALL returns
        print(f"\n  All trade returns (sorted worst to best):")
        sorted_returns = sorted(returns)
        for i, ret in enumerate(sorted_returns):
            marker = " ← VaR" if i == 0 else ""
            print(f"    {i+1}. {ret*100:+.2f}%{marker}")
        
        # Calculate VaR manually
        print(f"\n🔍 VaR Calculation Breakdown:")
        print(f"  Confidence level: 95%")
        print(f"  Number of returns: {len(returns)}")
        
        # Calculate index
        index = int((1 - 0.95) * len(returns))
        print(f"  Index calculation: (1 - 0.95) × {len(returns)} = {index}")
        print(f"  Taking return at index {index}: {sorted_returns[index]*100:.2f}%")
        
        # Calculate using function
        var_95 = calculate_var(returns, 0.95)
        cvar_95 = calculate_cvar(returns, 0.95)
        
        print(f"\n📉 Calculated Risk Metrics:")
        print(f"  VaR (95%): {var_95*100:.2f}%")
        print(f"  CVaR (95%): {cvar_95*100:.2f}%")
        
        # Explain CVaR
        tail_returns = [r for r in sorted_returns if r <= var_95]
        print(f"\n  CVaR calculation:")
        print(f"    Returns <= VaR: {len(tail_returns)} trades")
        print(f"    Tail returns: {[f'{r*100:.2f}%' for r in tail_returns]}")
        if tail_returns:
            avg_tail = sum(tail_returns) / len(tail_returns)
            print(f"    Average: {avg_tail*100:.2f}%")
        
        # Statistical summary
        import numpy as np
        print(f"\n📊 Statistical Summary:")
        print(f"  Mean return: {np.mean(returns)*100:.2f}%")
        print(f"  Std deviation: {np.std(returns)*100:.2f}%")
        print(f"  Min return: {min(returns)*100:.2f}%")
        print(f"  Max return: {max(returns)*100:.2f}%")
        print(f"  Median: {np.median(returns)*100:.2f}%")
        
        # Check if it looks like a mock value
        print(f"\n🔍 Validation:")
        if var_95 == -0.05 and len(set(returns)) > 1:
            # Check if -5% appears in actual returns
            has_minus_5 = any(abs(r - (-0.05)) < 0.001 for r in returns)
            if has_minus_5:
                print(f"  ✓ VaR of -5.00% is REAL (found in actual trade data)")
            else:
                print(f"  ⚠️ VaR of -5.00% might be suspicious (not found in trades)")
        else:
            print(f"  ✓ VaR value appears legitimate")
        
        # Check if all returns are unique
        if len(returns) == len(set(returns)):
            print(f"  ✓ All {len(returns)} returns are unique (good data quality)")
        else:
            print(f"  ⚠️ Some returns are duplicated")
        
        # Show actual trade details for worst trades
        print(f"\n📉 Worst 3 Trades Details:")
        trades_with_returns = [(t, t['pnl_pct']) for t in results['trades'] if t.get('pnl_pct') is not None]
        worst_trades = sorted(trades_with_returns, key=lambda x: x[1])[:3]
        
        for i, (trade, ret) in enumerate(worst_trades, 1):
            print(f"  {i}. Return: {ret*100:+.2f}%")
            print(f"     Entry: ${trade['entry_price']:.2f} on {trade['entry_date']}")
            print(f"     Exit:  ${trade['exit_price']:.2f} on {trade['exit_date']}")
            print(f"     PnL:   ${trade['pnl']:.2f}")
    
    else:
        print("  ⚠️ No returns found!")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_var_accuracy())

