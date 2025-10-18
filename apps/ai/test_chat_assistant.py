"""
Test script for the new unified chat assistant
Tests all major function types
"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_chat_orchestrator():
    """Test the chat orchestrator directly"""
    from agents.chat_orchestrator import chat_orchestrator
    
    test_cases = [
        {
            'name': 'Single Symbol Backtest',
            'message': 'backtest mean reversion strategy on AAPL',
            'user_id': 'test_user_1'
        },
        {
            'name': 'Multiple Symbol Backtest',
            'message': 'apply RSI oversold strategy to AAPL, TSLA, NVDA',
            'user_id': 'test_user_1'
        },
        {
            'name': 'Recommendation',
            'message': 'should I buy Microsoft?',
            'user_id': 'test_user_1'
        },
        {
            'name': 'Sentiment Research',
            'message': 'what\'s the sentiment on tech stocks?',
            'user_id': 'test_user_1'
        },
        {
            'name': 'Explanation',
            'message': 'what is RSI?',
            'user_id': 'test_user_1'
        },
        {
            'name': 'Portfolio Query',
            'message': 'show my portfolio',
            'user_id': 'test_user_1'
        }
    ]
    
    print("\n" + "="*80)
    print("TESTING CHAT ORCHESTRATOR")
    print("="*80 + "\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_cases)}: {test_case['name']}")
        print(f"Message: '{test_case['message']}'")
        print(f"{'='*80}\n")
        
        try:
            result = await chat_orchestrator.handle_message(
                message=test_case['message'],
                user_id=test_case['user_id']
            )
            
            print(f"✅ Success!")
            print(f"Intent: {result.get('intent', 'UNKNOWN')}")
            print(f"\nShort Response:")
            print(f"{result.get('short_response', 'N/A')[:200]}...")
            print(f"\nDetailed Response (first 500 chars):")
            print(f"{result.get('detailed_response', 'N/A')[:500]}...")
            
            # Check for chart data
            if result.get('metadata', {}).get('chart_data'):
                chart_data = result['metadata']['chart_data']
                print(f"\n📊 Chart Data:")
                for chart in chart_data:
                    symbol = chart.get('symbol', 'UNKNOWN')
                    num_points = len(chart.get('equity_curve', []))
                    print(f"  - {symbol}: {num_points} data points")
            
            print(f"\n{'='*80}\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Test failed: {e}", exc_info=True)
            print(f"\n{'='*80}\n")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80 + "\n")

async def test_single_backtest():
    """Test a single backtest in detail"""
    from agents.chat_orchestrator import chat_orchestrator
    
    print("\n" + "="*80)
    print("DETAILED BACKTEST TEST")
    print("="*80 + "\n")
    
    message = "backtest mean reversion on AAPL"
    user_id = "test_user_detailed"
    
    print(f"Testing: '{message}'")
    print("This may take 30-60 seconds...\n")
    
    try:
        result = await chat_orchestrator.handle_message(
            message=message,
            user_id=user_id
        )
        
        print("✅ Backtest Complete!\n")
        print(f"Intent: {result.get('intent')}")
        print(f"\nShort Response:\n{result.get('short_response')}\n")
        print(f"Detailed Response:\n{result.get('detailed_response')}\n")
        
        # Check metadata
        metadata = result.get('metadata', {})
        print(f"Metadata Keys: {list(metadata.keys())}")
        
        if 'chart_data' in metadata:
            print(f"\n📊 Chart Data Available:")
            for chart in metadata['chart_data']:
                symbol = chart.get('symbol')
                equity_curve = chart.get('equity_curve', [])
                print(f"\n  Symbol: {symbol}")
                print(f"  Data Points: {len(equity_curve)}")
                if equity_curve:
                    print(f"  Starting Equity: ${equity_curve[0]['equity']:,.2f}")
                    print(f"  Ending Equity: ${equity_curve[-1]['equity']:,.2f}")
                    total_return = equity_curve[-1]['equity'] - equity_curve[0]['equity']
                    print(f"  Total Return: ${total_return:+,.2f}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Backtest test failed: {e}", exc_info=True)

async def main():
    """Run all tests"""
    print("\n🧪 Starting Chat Assistant Tests\n")
    
    # Test 1: Single backtest in detail
    print("=" * 80)
    print("TEST 1: Detailed Single Backtest")
    print("=" * 80)
    await test_single_backtest()
    
    # Test 2: All function types
    print("\n\n" + "=" * 80)
    print("TEST 2: All Function Types")
    print("=" * 80)
    await test_chat_orchestrator()
    
    print("\n✅ All tests completed!\n")

if __name__ == "__main__":
    asyncio.run(main())

