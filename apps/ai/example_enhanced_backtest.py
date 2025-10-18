"""
Quick Start Example: Enhanced Backtesting with Natural Language

This script demonstrates how to use the enhanced backtesting feature
with natural language strategy input.
"""
import asyncio
import httpx
import json

# API endpoint (update if running on different host/port)
BASE_URL = "http://localhost:8000"

async def example_1_natural_language():
    """Example 1: Natural language strategy with full features"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Natural Language Strategy")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/backtest/run",
            json={
                "symbol": "AAPL",
                "natural_language_strategy": "buy when price is below the 2 week low",
                "include_visuals": True,
                "include_voice": True,
                "user_id": "demo_user"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✓ Strategy: {result['strategy']['name']}")
            print(f"✓ Period: {result['period']}")
            print(f"\nPerformance Metrics:")
            print(f"  - Total Return: {result['metrics']['total_return_pct']*100:.2f}%")
            print(f"  - Win Rate: {result['metrics']['win_rate']*100:.1f}%")
            print(f"  - Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
            print(f"  - Max Drawdown: {result['metrics']['max_drawdown']*100:.2f}%")
            print(f"  - VaR (95%): {result['metrics']['var_95']*100:.2f}%")
            print(f"  - CVaR (95%): {result['metrics']['cvar_95']*100:.2f}%")
            print(f"  - Number of Trades: {result['metrics']['num_trades']}")
            
            print(f"\nVisual Data:")
            print(f"  - Equity Curve Points: {len(result['metrics']['visuals']['equity_curve'])}")
            print(f"  - Drawdown Points: {len(result['metrics']['visuals']['drawdown_series'])}")
            print(f"  - Monthly Returns: {len(result['metrics']['visuals']['monthly_returns'])} months")
            
            print(f"\nExplanation Preview:")
            print(f"  {result['explanation'][:200]}...")
            
            if 'voice_audio_base64' in result:
                print(f"\n✓ Voice narration included ({len(result['voice_audio_base64'])} chars)")
            
            return result
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  {response.text}")

async def example_2_fast_no_voice():
    """Example 2: Fast analysis without voice (5-7 seconds)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Fast Analysis (No Voice)")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/backtest/run",
            json={
                "symbol": "NVDA",
                "natural_language_strategy": "buy on MACD bullish crossover",
                "include_voice": False  # Skip voice for faster response
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Strategy: {result['strategy']['name']}")
            print(f"✓ Return: {result['metrics']['total_return_pct']*100:.2f}%")
            print(f"✓ Response includes visuals: {'visuals' in result['metrics']}")
            print(f"✓ Voice included: {'voice_audio_base64' in result}")
        else:
            print(f"✗ Error: {response.status_code}")

async def example_3_template():
    """Example 3: Use pre-built template"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Pre-built Template")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/backtest/run",
            json={
                "symbol": "MSFT",
                "strategy_template_id": "rsi_oversold",
                "include_visuals": True,
                "include_voice": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Template: {result['strategy']['name']}")
            print(f"✓ Description: {result['strategy']['description']}")
            print(f"✓ Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
        else:
            print(f"✗ Error: {response.status_code}")

async def example_4_multiple_strategies():
    """Example 4: Compare multiple strategies"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Compare Multiple Strategies")
    print("="*60)
    
    strategies = [
        "buy when RSI is below 30",
        "buy when price crosses above 50 day moving average",
        "buy on MACD bullish crossover"
    ]
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for strategy_desc in strategies:
            print(f"\nTesting: {strategy_desc}")
            
            response = await client.post(
                f"{BASE_URL}/backtest/run",
                json={
                    "symbol": "TSLA",
                    "natural_language_strategy": strategy_desc,
                    "include_voice": False  # Skip voice for speed
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                results.append({
                    'strategy': result['strategy']['name'],
                    'return': result['metrics']['total_return_pct'],
                    'sharpe': result['metrics']['sharpe_ratio'],
                    'win_rate': result['metrics']['win_rate']
                })
                print(f"  ✓ Return: {result['metrics']['total_return_pct']*100:.2f}%")
            else:
                print(f"  ✗ Failed: {response.status_code}")
    
    # Compare results
    if results:
        print("\n" + "-"*60)
        print("COMPARISON")
        print("-"*60)
        best_return = max(results, key=lambda x: x['return'])
        best_sharpe = max(results, key=lambda x: x['sharpe'])
        
        print(f"Best Return: {best_return['strategy']} ({best_return['return']*100:.2f}%)")
        print(f"Best Sharpe: {best_sharpe['strategy']} ({best_sharpe['sharpe']:.2f})")

async def example_5_custom_date_range():
    """Example 5: Custom date range"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Custom Date Range")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/backtest/run",
            json={
                "symbol": "GOOGL",
                "natural_language_strategy": "buy when RSI is below 30",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "initial_capital": 50000,
                "include_voice": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Period: {result['period']}")
            print(f"✓ Initial Capital: ${result['initial_capital']:,.0f}")
            print(f"✓ Final Capital: ${result['initial_capital'] + result['metrics']['total_return']:,.0f}")
            print(f"✓ Profit: ${result['metrics']['total_return']:,.0f}")
        else:
            print(f"✗ Error: {response.status_code}")

async def example_6_save_voice():
    """Example 6: Save voice narration to file"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Save Voice Narration")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/backtest/run",
            json={
                "symbol": "AAPL",
                "natural_language_strategy": "buy when RSI is below 30",
                "include_voice": True,
                "user_id": "demo_user"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if 'voice_audio_base64' in result:
                # Decode base64 and save to file
                import base64
                audio_data = base64.b64decode(result['voice_audio_base64'])
                
                filename = f"backtest_explanation_{result['symbol']}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio_data)
                
                print(f"\n✓ Voice narration saved to: {filename}")
                print(f"✓ File size: {len(audio_data):,} bytes")
                print(f"✓ Play with: mpg123 {filename}")
            else:
                print("\n⚠ Voice narration not available")
        else:
            print(f"✗ Error: {response.status_code}")

async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "ENHANCED BACKTESTING EXAMPLES" + " "*19 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Run examples
        await example_1_natural_language()
        await example_2_fast_no_voice()
        await example_3_template()
        await example_4_multiple_strategies()
        await example_5_custom_date_range()
        await example_6_save_voice()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except httpx.ConnectError:
        print("\n✗ ERROR: Cannot connect to API server")
        print("  Make sure the server is running:")
        print("  cd apps/ai && uvicorn main:app --reload")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())

