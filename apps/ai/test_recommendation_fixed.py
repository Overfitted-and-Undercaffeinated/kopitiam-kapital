"""Test recommendation with fixed sentiment scoring"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def main():
    from agents.recommend import recommendation_agent
    
    print("\n" + "="*80)
    print("TESTING RECOMMENDATION WITH FIXED SENTIMENT")
    print("="*80 + "\n")
    
    result = await recommendation_agent.generate_recommendation('NVDA', 'test_user')
    
    print("="*80)
    print("RECOMMENDATION RESULTS:")
    print("="*80)
    print(f"Symbol:    {result['symbol']}")
    print(f"Action:    {result['action']}")  
    print(f"Entry:     ${result['entry_price']:.2f}")
    print(f"Stop:      ${result['stop_loss']:.2f}")
    print(f"Target:    ${result['take_profit']:.2f}")
    print(f"\nSentiment:")
    print(f"  Score:      {result['sentiment']['score']}")
    print(f"  Direction:  {result['sentiment']['direction']}")
    print(f"  Confidence: {result['sentiment']['confidence']}")
    print(f"\nBacktest:")
    print(f"  Win Rate:   {result['backtest_validation']['win_rate']:.1%}")
    print(f"  Return:     {result['backtest_validation']['total_return_pct']:.1%}")
    print(f"  Trades:     {result['backtest_validation']['sample_size']}")
    print(f"\nReasoning:")
    print(result['reasoning'])
    print("="*80)
    
    # Check if results make sense
    if result['sentiment']['score'] > 0.6 and result['action'] == 'BUY':
        print("\n✓ RESULTS MAKE SENSE! Bullish sentiment → BUY recommendation")
    elif result['sentiment']['score'] < 0.4 and result['action'] == 'SELL':
        print("\n✓ RESULTS MAKE SENSE! Bearish sentiment → SELL recommendation")
    elif result['action'] == 'HOLD':
        print(f"\n✓ RESULTS MAKE SENSE! Neutral/weak signal → HOLD")
    else:
        print(f"\n⚠️  Check results: Sentiment {result['sentiment']['score']:.2f} but action is {result['action']}")

if __name__ == "__main__":
    asyncio.run(main())


