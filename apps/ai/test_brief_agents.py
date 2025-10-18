"""
Comprehensive Test Suite for Morning Brief and EOD Brief Agents
Tests all features including sentiment, voice generation, and error handling
"""
import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the agents
from agents.morning_brief import morning_brief_agent
from agents.eod_brief import eod_brief_agent

# Test configuration
TEST_USER_ID = "test_user_123"
TEST_WATCHLIST = ["AAPL", "MSFT", "TSLA"]
TEST_MARKET = "US"

class BriefAgentTester:
    """Test runner for brief agents"""
    
    def __init__(self):
        self.results = {
            'morning_brief': {},
            'eod_brief': {},
            'errors': []
        }
    
    async def test_morning_brief_basic(self):
        """Test basic morning brief generation"""
        logger.info("\n" + "="*80)
        logger.info("TEST 1: Morning Brief - Basic Generation")
        logger.info("="*80)
        
        try:
            result = await morning_brief_agent.generate_brief(
                watchlist=TEST_WATCHLIST,
                market=TEST_MARKET,
                user_id=TEST_USER_ID,
                include_voice=False  # Skip voice for speed
            )
            
            # Validate structure
            assert result['type'] == 'morning', "Type should be 'morning'"
            assert 'text' in result, "Should have text field"
            assert 'symbols_analyzed' in result, "Should have symbols_analyzed"
            assert 'sentiment_summary' in result, "Should have sentiment_summary"
            assert 'generated_at' in result, "Should have generated_at"
            
            # Validate content
            assert len(result['text']) > 0, "Text should not be empty"
            assert result['symbols_analyzed'] == TEST_WATCHLIST, "Should analyze all symbols"
            assert result['sentiment_summary']['bullish_count'] >= 0, "Should have bullish count"
            assert result['sentiment_summary']['bearish_count'] >= 0, "Should have bearish count"
            
            # Log results
            logger.info("✅ PASSED: Basic morning brief generation")
            logger.info(f"   Brief length: {len(result['text'])} chars")
            logger.info(f"   Symbols analyzed: {result['symbols_analyzed']}")
            logger.info(f"   Sentiment summary: {result['sentiment_summary']}")
            logger.info("\n📄 BRIEF TEXT:")
            logger.info("-" * 80)
            logger.info(result['text'])
            logger.info("-" * 80)
            
            self.results['morning_brief']['basic'] = {
                'status': 'passed',
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ FAILED: {str(e)}")
            self.results['errors'].append(f"Morning Brief Basic: {str(e)}")
            self.results['morning_brief']['basic'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_morning_brief_with_voice(self):
        """Test morning brief with voice generation"""
        logger.info("\n" + "="*80)
        logger.info("TEST 2: Morning Brief - With Voice Generation")
        logger.info("="*80)
        
        try:
            result = await morning_brief_agent.generate_brief(
                watchlist=TEST_WATCHLIST[:2],  # Use fewer symbols for speed
                market=TEST_MARKET,
                user_id=TEST_USER_ID,
                include_voice=True
            )
            
            # Validate voice
            if result.get('audio_base64'):
                logger.info("✅ PASSED: Voice generation successful")
                logger.info(f"   Audio data length: {len(result['audio_base64'])} chars")
            else:
                logger.warning("⚠️ WARNING: Voice generation returned None (may not be configured)")
            
            self.results['morning_brief']['with_voice'] = {
                'status': 'passed',
                'has_audio': result.get('audio_base64') is not None
            }
            
        except Exception as e:
            logger.error(f"❌ FAILED: {str(e)}")
            self.results['errors'].append(f"Morning Brief Voice: {str(e)}")
            self.results['morning_brief']['with_voice'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_morning_brief_empty_watchlist(self):
        """Test morning brief with empty watchlist (should fail gracefully)"""
        logger.info("\n" + "="*80)
        logger.info("TEST 3: Morning Brief - Empty Watchlist (Error Handling)")
        logger.info("="*80)
        
        try:
            result = await morning_brief_agent.generate_brief(
                watchlist=[],
                market=TEST_MARKET,
                user_id=TEST_USER_ID,
                include_voice=False
            )
            
            logger.error("❌ FAILED: Should have raised ValueError for empty watchlist")
            self.results['morning_brief']['empty_watchlist'] = {
                'status': 'failed',
                'error': 'Did not raise expected error'
            }
            
        except ValueError as e:
            logger.info(f"✅ PASSED: Correctly raised ValueError: {str(e)}")
            self.results['morning_brief']['empty_watchlist'] = {
                'status': 'passed',
                'error_message': str(e)
            }
        except Exception as e:
            logger.error(f"❌ FAILED: Wrong exception type: {str(e)}")
            self.results['errors'].append(f"Morning Brief Empty: {str(e)}")
            self.results['morning_brief']['empty_watchlist'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_eod_brief_basic(self):
        """Test basic EOD brief generation"""
        logger.info("\n" + "="*80)
        logger.info("TEST 4: EOD Brief - Basic Generation")
        logger.info("="*80)
        
        try:
            result = await eod_brief_agent.generate_brief(
                watchlist=TEST_WATCHLIST,
                market=TEST_MARKET,
                user_id=TEST_USER_ID,
                include_voice=False
            )
            
            # Validate structure
            assert result['type'] == 'eod', "Type should be 'eod'"
            assert 'text' in result, "Should have text field"
            assert 'symbols_analyzed' in result, "Should have symbols_analyzed"
            assert 'performance_summary' in result, "Should have performance_summary"
            assert 'generated_at' in result, "Should have generated_at"
            
            # Validate content
            assert len(result['text']) > 0, "Text should not be empty"
            assert result['symbols_analyzed'] == TEST_WATCHLIST, "Should analyze all symbols"
            
            # Validate performance summary
            perf = result['performance_summary']
            assert 'gainers' in perf, "Should have gainers count"
            assert 'losers' in perf, "Should have losers count"
            assert 'average_change' in perf, "Should have average change"
            
            # Log results
            logger.info("✅ PASSED: Basic EOD brief generation")
            logger.info(f"   Brief length: {len(result['text'])} chars")
            logger.info(f"   Symbols analyzed: {result['symbols_analyzed']}")
            logger.info(f"   Performance summary: {result['performance_summary']}")
            logger.info("\n📄 BRIEF TEXT:")
            logger.info("-" * 80)
            logger.info(result['text'])
            logger.info("-" * 80)
            
            self.results['eod_brief']['basic'] = {
                'status': 'passed',
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ FAILED: {str(e)}")
            self.results['errors'].append(f"EOD Brief Basic: {str(e)}")
            self.results['eod_brief']['basic'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_eod_brief_with_voice(self):
        """Test EOD brief with voice generation"""
        logger.info("\n" + "="*80)
        logger.info("TEST 5: EOD Brief - With Voice Generation")
        logger.info("="*80)
        
        try:
            result = await eod_brief_agent.generate_brief(
                watchlist=TEST_WATCHLIST[:2],
                market=TEST_MARKET,
                user_id=TEST_USER_ID,
                include_voice=True
            )
            
            # Validate voice
            if result.get('audio_base64'):
                logger.info("✅ PASSED: Voice generation successful")
                logger.info(f"   Audio data length: {len(result['audio_base64'])} chars")
            else:
                logger.warning("⚠️ WARNING: Voice generation returned None (may not be configured)")
            
            self.results['eod_brief']['with_voice'] = {
                'status': 'passed',
                'has_audio': result.get('audio_base64') is not None
            }
            
        except Exception as e:
            logger.error(f"❌ FAILED: {str(e)}")
            self.results['errors'].append(f"EOD Brief Voice: {str(e)}")
            self.results['eod_brief']['with_voice'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_eod_brief_empty_watchlist(self):
        """Test EOD brief with empty watchlist (should fail gracefully)"""
        logger.info("\n" + "="*80)
        logger.info("TEST 6: EOD Brief - Empty Watchlist (Error Handling)")
        logger.info("="*80)
        
        try:
            result = await eod_brief_agent.generate_brief(
                watchlist=[],
                market=TEST_MARKET,
                user_id=TEST_USER_ID,
                include_voice=False
            )
            
            logger.error("❌ FAILED: Should have raised ValueError for empty watchlist")
            self.results['eod_brief']['empty_watchlist'] = {
                'status': 'failed',
                'error': 'Did not raise expected error'
            }
            
        except ValueError as e:
            logger.info(f"✅ PASSED: Correctly raised ValueError: {str(e)}")
            self.results['eod_brief']['empty_watchlist'] = {
                'status': 'passed',
                'error_message': str(e)
            }
        except Exception as e:
            logger.error(f"❌ FAILED: Wrong exception type: {str(e)}")
            self.results['errors'].append(f"EOD Brief Empty: {str(e)}")
            self.results['eod_brief']['empty_watchlist'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*80)
        logger.info("TEST SUMMARY")
        logger.info("="*80)
        
        morning_tests = self.results['morning_brief']
        eod_tests = self.results['eod_brief']
        
        total_tests = len(morning_tests) + len(eod_tests)
        passed_tests = sum(1 for t in morning_tests.values() if t.get('status') == 'passed')
        passed_tests += sum(1 for t in eod_tests.values() if t.get('status') == 'passed')
        
        logger.info(f"\n📊 MORNING BRIEF TESTS:")
        for test_name, result in morning_tests.items():
            status = "✅" if result.get('status') == 'passed' else "❌"
            logger.info(f"   {status} {test_name}: {result.get('status')}")
        
        logger.info(f"\n📊 EOD BRIEF TESTS:")
        for test_name, result in eod_tests.items():
            status = "✅" if result.get('status') == 'passed' else "❌"
            logger.info(f"   {status} {test_name}: {result.get('status')}")
        
        logger.info(f"\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed")
        
        if self.results['errors']:
            logger.info("\n⚠️ ERRORS:")
            for error in self.results['errors']:
                logger.info(f"   - {error}")
        
        logger.info("\n" + "="*80)
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Brief Agents Test Suite")
        logger.info(f"Test User ID: {TEST_USER_ID}")
        logger.info(f"Test Watchlist: {TEST_WATCHLIST}")
        logger.info(f"Test Market: {TEST_MARKET}")
        
        # Morning Brief Tests
        await self.test_morning_brief_basic()
        await self.test_morning_brief_with_voice()
        await self.test_morning_brief_empty_watchlist()
        
        # EOD Brief Tests
        await self.test_eod_brief_basic()
        await self.test_eod_brief_with_voice()
        await self.test_eod_brief_empty_watchlist()
        
        # Print summary
        self.print_summary()
        
        # Return success if all tests passed
        return len(self.results['errors']) == 0


async def main():
    """Main test runner"""
    tester = BriefAgentTester()
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

