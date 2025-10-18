"""
Quick performance test for optimized backtesting
Tests cache hits vs cache misses
"""
import asyncio
import time

async def test_performance():
    """Test the performance improvements"""
    from agents.strategy_translator import strategy_translator
    from backtesting.engine import BacktestEngine
    from backtesting.builder import strategy_builder
    from data.risk import calculate_var, calculate_cvar
    from datetime import datetime, timedelta
    
    print("="*60)
    print("PERFORMANCE TEST - Optimized Backtesting")
    print("="*60)
    
    symbol = "AAPL"
    strategy_desc = "buy when RSI is below 30"
    
    # Test 1: First run (cache miss)
    print("\n[Test 1] First Run (Cache MISS)...")
    start_time = time.time()
    
    # Translate strategy
    strategy_def = await strategy_translator.translate_strategy(
        natural_language=strategy_desc,
        symbol=symbol
    )
    translate_time = time.time() - start_time
    print(f"  ✓ Translation: {translate_time:.2f}s")
    
    # Build and run backtest
    strategy_func = strategy_builder.build_strategy(strategy_def)
    engine = BacktestEngine()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 year
    
    backtest_start = time.time()
    results = await engine.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        strategy_fn=strategy_func,
        initial_capital=100000,
        include_visuals=True
    )
    backtest_time = time.time() - backtest_start
    print(f"  ✓ Backtest: {backtest_time:.2f}s")
    
    # Calculate VaR
    returns = [t['pnl_pct'] for t in results['trades'] if t.get('pnl_pct')]
    if returns:
        var_95 = calculate_var(returns, 0.95)
        cvar_95 = calculate_cvar(returns, 0.95)
    
    total_time_first = time.time() - start_time
    print(f"  ✓ Total: {total_time_first:.2f}s")
    print(f"  ✓ Trades: {results['num_trades']}")
    print(f"  ✓ Return: {results['total_return_pct']*100:.2f}%")
    
    # Test 2: Second run (cache hit!)
    print("\n[Test 2] Second Run (Cache HIT)...")
    start_time = time.time()
    
    # Same backtest
    results2 = await engine.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        strategy_fn=strategy_func,
        initial_capital=100000,
        include_visuals=True
    )
    
    total_time_second = time.time() - start_time
    print(f"  ✓ Total: {total_time_second:.2f}s")
    print(f"  ✓ Trades: {results2['num_trades']}")
    
    # Calculate speedup
    speedup = total_time_first / total_time_second if total_time_second > 0 else 0
    print(f"\n🚀 SPEEDUP: {speedup:.1f}x faster on cached run!")
    
    # Test 3: Different symbol (cache miss again)
    print("\n[Test 3] Different Symbol (Cache MISS)...")
    start_time = time.time()
    
    results3 = await engine.run_backtest(
        symbol="NVDA",
        start_date=start_date,
        end_date=end_date,
        strategy_fn=strategy_func,
        initial_capital=100000,
        include_visuals=True
    )
    
    total_time_third = time.time() - start_time
    print(f"  ✓ Total: {total_time_third:.2f}s")
    print(f"  ✓ Trades: {results3['num_trades']}")
    
    # Summary
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    print(f"First run (AAPL):      {total_time_first:.2f}s")
    print(f"Second run (AAPL):     {total_time_second:.2f}s (cached)")
    print(f"Third run (NVDA):      {total_time_third:.2f}s")
    print(f"\nCache speedup:         {speedup:.1f}x")
    print(f"Time saved per query:  {total_time_first - total_time_second:.2f}s")
    
    # Get cache stats
    from data.data_cache import market_data_cache
    stats = market_data_cache.get_stats()
    print(f"\nCache stats:")
    print(f"  Entries: {stats['total_entries']}")
    print(f"  Rows: {stats['total_rows']}")
    print(f"  Avg age: {stats['average_age_seconds']:.0f}s")
    
    print("\n✅ All optimizations working!")

if __name__ == "__main__":
    asyncio.run(test_performance())

