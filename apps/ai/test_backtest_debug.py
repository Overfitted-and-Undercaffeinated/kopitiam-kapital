"""Debug backtest to see why so few trades"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def main():
    from backtesting.engine import BacktestEngine
    from backtesting.templates import get_template
    from backtesting.builder import strategy_builder
    from datetime import datetime, timedelta
    
    print("\n" + "="*80)
    print("BACKTEST DEBUG TEST")
    print("="*80)
    
    # Get RSI oversold strategy
    strategy_def = get_template('rsi_oversold')
    print(f"\nStrategy: {strategy_def['name']}")
    print(f"Description: {strategy_def.get('description', 'N/A')}")
    print(f"Entry rules: {strategy_def['entry_rules']}")
    print(f"Exit rules: {strategy_def['exit_rules']}")
    print(f"Risk management: {strategy_def['risk_management']}")
    
    # Build strategy
    strategy_func = strategy_builder.build_strategy(strategy_def)
    
    # Test with different time periods
    symbols = ['NVDA', 'AAPL', 'MSFT']
    
    for symbol in symbols:
        print(f"\n" + "-"*80)
        print(f"Testing {symbol}")
        print("-"*80)
        
        # Test 1 year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        engine = BacktestEngine()
        results = await engine.run_backtest(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            strategy_fn=strategy_func,
            initial_capital=100000
        )
        
        print(f"1-Year Backtest:")
        print(f"  Trades:      {results['num_trades']}")
        print(f"  Win Rate:    {results['win_rate']:.1%}")
        print(f"  Total Return: {results['total_return_pct']:.1%}")
        print(f"  Sharpe:      {results['sharpe_ratio']:.2f}")
        
        # Test 2 years for comparison
        start_date_2y = end_date - timedelta(days=730)
        
        results_2y = await engine.run_backtest(
            symbol=symbol,
            start_date=start_date_2y.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            strategy_fn=strategy_func,
            initial_capital=100000
        )
        
        print(f"\n2-Year Backtest:")
        print(f"  Trades:      {results_2y['num_trades']}")
        print(f"  Win Rate:    {results_2y['win_rate']:.1%}")
        print(f"  Total Return: {results_2y['total_return_pct']:.1%}")
        print(f"  Sharpe:      {results_2y['sharpe_ratio']:.2f}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())

