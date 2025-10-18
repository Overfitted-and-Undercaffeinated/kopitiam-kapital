"""
Test Morning and EOD Briefs - Focus on Output Review
"""
import asyncio
import logging
from datetime import datetime

# Configure minimal logging
logging.basicConfig(level=logging.WARNING)

# Import the agents
from agents.morning_brief import morning_brief_agent
from agents.eod_brief import eod_brief_agent

# Test configuration
TEST_USER_ID = "demo_user_001"
TEST_WATCHLIST = ["AAPL", "MSFT", "NVDA"]
TEST_MARKET = "US"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*100)
    print(f"  {title}")
    print("="*100 + "\n")


def print_brief_details(brief_type, result):
    """Print detailed brief information"""
    print(f"📊 Brief Type: {result['type'].upper()}")
    print(f"📅 Generated: {result['generated_at']}")
    print(f"🎯 Symbols: {', '.join(result['symbols_analyzed'])}")
    print(f"📏 Length: {len(result['text'])} characters")
    
    if brief_type == 'morning':
        sentiment = result['sentiment_summary']
        print(f"\n📈 Sentiment Summary:")
        print(f"   • Average: {sentiment['average_sentiment']:.2f}")
        print(f"   • Bullish: {sentiment['bullish_count']}")
        print(f"   • Bearish: {sentiment['bearish_count']}")
        print(f"   • Trending: {sentiment['trending_count']}")
    else:
        perf = result['performance_summary']
        print(f"\n📊 Performance Summary:")
        print(f"   • Gainers: {perf['gainers']}")
        print(f"   • Losers: {perf['losers']}")
        print(f"   • Avg Change: {perf['average_change']:.2f}%")
        print(f"   • Sentiment Improved: {perf['sentiment_improved']}")
        print(f"   • Sentiment Declined: {perf['sentiment_declined']}")
    
    has_audio = result.get('audio_base64') is not None
    print(f"🎤 Voice Narration: {'✅ Generated' if has_audio else '❌ Not included'}")
    if has_audio:
        print(f"   • Audio size: {len(result['audio_base64'])} chars (base64)")


async def test_morning_brief():
    """Test morning brief generation"""
    print_section("🌅 MORNING BRIEF TEST")
    
    print(f"Testing with:")
    print(f"  • User ID: {TEST_USER_ID}")
    print(f"  • Watchlist: {TEST_WATCHLIST}")
    print(f"  • Market: {TEST_MARKET}")
    print(f"  • Voice: Enabled\n")
    
    print("⏳ Generating morning brief...\n")
    
    result = await morning_brief_agent.generate_brief(
        watchlist=TEST_WATCHLIST,
        market=TEST_MARKET,
        user_id=TEST_USER_ID,
        include_voice=True
    )
    
    print("✅ MORNING BRIEF GENERATED!\n")
    print_brief_details('morning', result)
    
    print("\n" + "─"*100)
    print("📄 MORNING BRIEF CONTENT:")
    print("─"*100 + "\n")
    print(result['text'])
    print("\n" + "─"*100)
    
    return result


async def test_eod_brief():
    """Test EOD brief generation"""
    print_section("🌆 END-OF-DAY BRIEF TEST")
    
    print(f"Testing with:")
    print(f"  • User ID: {TEST_USER_ID}")
    print(f"  • Watchlist: {TEST_WATCHLIST}")
    print(f"  • Market: {TEST_MARKET}")
    print(f"  • Voice: Enabled\n")
    
    print("⏳ Generating EOD brief...\n")
    
    result = await eod_brief_agent.generate_brief(
        watchlist=TEST_WATCHLIST,
        market=TEST_MARKET,
        user_id=TEST_USER_ID,
        include_voice=True
    )
    
    print("✅ EOD BRIEF GENERATED!\n")
    print_brief_details('eod', result)
    
    print("\n" + "─"*100)
    print("📄 EOD BRIEF CONTENT:")
    print("─"*100 + "\n")
    print(result['text'])
    print("\n" + "─"*100)
    
    return result


async def main():
    """Main test runner"""
    print("\n")
    print("╔" + "═"*98 + "╗")
    print("║" + " "*30 + "BRIEF AGENTS OUTPUT REVIEW" + " "*42 + "║")
    print("╚" + "═"*98 + "╝")
    
    start_time = datetime.now()
    
    try:
        # Test Morning Brief
        morning_result = await test_morning_brief()
        
        # Test EOD Brief
        eod_result = await test_eod_brief()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print_section("✅ TEST SUMMARY")
        print(f"✅ Both briefs generated successfully!")
        print(f"⏱️  Total time: {duration:.1f} seconds")
        print(f"\n📊 Morning Brief: {len(morning_result['text'])} chars")
        print(f"📊 EOD Brief: {len(eod_result['text'])} chars")
        
        if morning_result.get('audio_base64') and eod_result.get('audio_base64'):
            print(f"\n🎤 Both briefs include voice narration")
        
        print("\n" + "="*100 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

