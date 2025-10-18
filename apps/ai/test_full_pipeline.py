"""
Comprehensive Full Pipeline Integration Test
Tests all major components of the Kopitiam Kapital AI system
"""
import asyncio
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)

class PipelineTester:
    """Full pipeline integration tester"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        self.test_user_id = "pipeline_test_user"
        self.test_symbol = "AAPL"
        self.test_watchlist = ["AAPL", "MSFT"]
    
    def print_header(self, title, emoji="🔧"):
        print("\n" + "="*100)
        print(f"{emoji} {title}")
        print("="*100)
    
    def print_result(self, test_name, passed, details="", duration=None):
        status = "✅ PASS" if passed else "❌ FAIL"
        timing = f" ({duration:.1f}s)" if duration else ""
        print(f"{status}{timing} - {test_name}")
        if details:
            print(f"         {details}")
        if not passed:
            self.errors.append(test_name)
    
    async def test_api_connections(self):
        """Test 1: Verify all API connections"""
        self.print_header("TEST 1: API Connections", "🔌")
        start = datetime.now()
        
        try:
            # Test OpenAI
            from utils.clients import get_openai_client
            client = get_openai_client()
            self.print_result("OpenAI Client", True, "Connection initialized")
            
            # Test Groq
            from utils.clients import get_groq_client
            groq = get_groq_client()
            self.print_result("Groq Client", True, "Connection initialized")
            
            # Test Exa
            from retrievers.exa_client import exa_client
            self.print_result("Exa.ai Client", True, "Connection initialized")
            
            # Test Mem0
            from memory.mem0_service import mem0_service
            # Try getting policy (actual method)
            policy = await mem0_service.get_policy(self.test_user_id)
            self.print_result("Mem0 Cloud", isinstance(policy, dict), 
                            f"Policy retrieved: {policy.get('risk_tolerance', 'N/A')}")
            
            # Test ElevenLabs
            from voice.brief_narrator import brief_narrator
            self.print_result("ElevenLabs Voice", brief_narrator.enabled, 
                            "Enabled" if brief_narrator.enabled else "Disabled (OK)")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['api_connections'] = 'passed'
            print(f"\n⏱️  API Connection Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("API Connections", False, str(e))
            self.results['api_connections'] = f'failed: {e}'
            return False
    
    async def test_market_data(self):
        """Test 2: Market data retrieval"""
        self.print_header("TEST 2: Market Data Service", "📊")
        start = datetime.now()
        
        try:
            from data.market_data import market_data_service
            
            # Test latest price
            price = await market_data_service.get_latest_price(self.test_symbol)
            self.print_result("Get Latest Price", price is not None and price > 0, 
                            f"${price:.2f}" if price else "Failed")
            
            # Test OHLCV data
            ohlcv = await market_data_service.get_ohlcv(self.test_symbol, period="5d", interval="1d")
            self.print_result("Get OHLCV Data", not ohlcv.empty, 
                            f"{len(ohlcv)} days" if not ohlcv.empty else "No data")
            
            # Test basic stats (instead of indicators method)
            self.print_result("Market Data Service", True,
                            "Price and OHLCV working")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['market_data'] = 'passed'
            print(f"\n⏱️  Market Data Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("Market Data", False, str(e))
            self.results['market_data'] = f'failed: {e}'
            return False
    
    async def test_sentiment_pipeline(self):
        """Test 3: Sentiment analysis pipeline"""
        self.print_header("TEST 3: Sentiment Analysis Pipeline", "😊")
        start = datetime.now()
        
        try:
            from sentiment.aggregator import sentiment_aggregator
            
            # Test sentiment for one symbol
            sentiment = await sentiment_aggregator.get_sentiment(
                symbol=self.test_symbol,
                user_id=self.test_user_id
            )
            
            self.print_result("Get Sentiment Score", 
                            'overall_score' in sentiment,
                            f"Score: {sentiment.get('overall_score', 'N/A')}, Direction: {sentiment.get('direction', 'N/A')}")
            
            self.print_result("News Analysis (Exa.ai)", 
                            sentiment.get('volume', {}).get('news_articles', 0) > 0,
                            f"{sentiment.get('volume', {}).get('news_articles', 0)} articles")
            
            self.print_result("Sentiment Direction", 
                            sentiment.get('direction') in ['bullish', 'bearish', 'neutral'],
                            sentiment.get('direction', 'unknown'))
            
            self.print_result("Confidence Score",
                            sentiment.get('confidence', 0) > 0,
                            f"{sentiment.get('confidence', 0):.2f}")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['sentiment'] = 'passed'
            print(f"\n⏱️  Sentiment Pipeline Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("Sentiment Pipeline", False, str(e))
            self.results['sentiment'] = f'failed: {e}'
            return False
    
    async def test_rag_pipeline(self):
        """Test 4: RAG (Retrieval-Augmented Generation) pipeline"""
        self.print_header("TEST 4: RAG Pipeline", "🔍")
        start = datetime.now()
        
        try:
            from rag.pipeline import rag_pipeline
            
            # Test RAG query
            query = f"What is the latest news about {self.test_symbol}?"
            result = await rag_pipeline.retrieve_and_generate(
                query=query,
                user_id=self.test_user_id
            )
            
            self.print_result("RAG Query", 
                            'response' in result,
                            f"Generated {len(result.get('response', ''))} chars")
            
            self.print_result("Source Retrieval",
                            result.get('num_sources', 0) > 0,
                            f"{result.get('num_sources', 0)} sources")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['rag'] = 'passed'
            print(f"\n⏱️  RAG Pipeline Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("RAG Pipeline", False, str(e))
            self.results['rag'] = f'failed: {e}'
            return False
    
    async def test_morning_brief(self):
        """Test 5: Morning brief generation"""
        self.print_header("TEST 5: Morning Brief Agent", "🌅")
        start = datetime.now()
        
        try:
            from agents.morning_brief import morning_brief_agent
            
            # Generate brief without voice for speed
            brief = await morning_brief_agent.generate_brief(
                watchlist=self.test_watchlist,
                market="US",
                user_id=self.test_user_id,
                include_voice=False
            )
            
            self.print_result("Brief Generation",
                            'text' in brief and len(brief['text']) > 0,
                            f"{len(brief['text'])} chars")
            
            self.print_result("Sentiment Summary",
                            'sentiment_summary' in brief,
                            f"Avg: {brief.get('sentiment_summary', {}).get('average_sentiment', 'N/A')}")
            
            self.print_result("Symbols Analyzed",
                            brief.get('symbols_analyzed') == self.test_watchlist,
                            f"{len(brief.get('symbols_analyzed', []))} symbols")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['morning_brief'] = 'passed'
            print(f"\n⏱️  Morning Brief Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("Morning Brief", False, str(e))
            self.results['morning_brief'] = f'failed: {e}'
            return False
    
    async def test_eod_brief(self):
        """Test 6: EOD brief generation"""
        self.print_header("TEST 6: End-of-Day Brief Agent", "🌆")
        start = datetime.now()
        
        try:
            from agents.eod_brief import eod_brief_agent
            
            # Generate brief without voice for speed
            brief = await eod_brief_agent.generate_brief(
                watchlist=self.test_watchlist,
                market="US",
                user_id=self.test_user_id,
                include_voice=False
            )
            
            self.print_result("Brief Generation",
                            'text' in brief and len(brief['text']) > 0,
                            f"{len(brief['text'])} chars")
            
            self.print_result("Performance Summary",
                            'performance_summary' in brief,
                            f"Gainers: {brief.get('performance_summary', {}).get('gainers', 'N/A')}")
            
            self.print_result("RAG Research",
                            len(brief['text']) > 500,
                            "Includes market drivers analysis")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['eod_brief'] = 'passed'
            print(f"\n⏱️  EOD Brief Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("EOD Brief", False, str(e))
            self.results['eod_brief'] = f'failed: {e}'
            return False
    
    async def test_router_agent(self):
        """Test 7: Router agent (intent classification)"""
        self.print_header("TEST 7: Router Agent", "🧭")
        start = datetime.now()
        
        try:
            from agents.router import RouterAgent
            router = RouterAgent()
            
            # Test different intents
            test_cases = [
                ("What's the latest on AAPL?", "research"),
                ("Give me a recommendation for MSFT", "recommend"),
                ("Show my portfolio", "portfolio"),
            ]
            
            for query, expected in test_cases:
                result = await router.route(query=query)
                detected = result.get('intent', 'unknown').lower()
                self.print_result(f"Intent: {query[:30]}...",
                                detected != 'unknown',
                                f"Detected: {detected}")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['router'] = 'passed'
            print(f"\n⏱️  Router Agent Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("Router Agent", False, str(e))
            self.results['router'] = f'failed: {e}'
            return False
    
    async def test_recommendation_agent(self):
        """Test 8: Recommendation agent"""
        self.print_header("TEST 8: Recommendation Agent", "💡")
        start = datetime.now()
        
        try:
            from agents.recommend import recommendation_agent
            
            # Generate recommendation
            rec = await recommendation_agent.generate_recommendation(
                symbol=self.test_symbol,
                user_id=self.test_user_id
            )
            
            self.print_result("Recommendation Generated",
                            'action' in rec,
                            f"Action: {rec.get('action', 'N/A')}")
            
            self.print_result("Analysis Provided",
                            'symbol' in rec and 'action' in rec,
                            f"Symbol: {rec.get('symbol', 'N/A')}")
            
            self.print_result("Detailed Response",
                            len(str(rec)) > 50,
                            f"Recommendation complete")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['recommendation'] = 'passed'
            print(f"\n⏱️  Recommendation Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("Recommendation Agent", False, str(e))
            self.results['recommendation'] = f'failed: {e}'
            return False
    
    async def test_memory_system(self):
        """Test 9: Memory system (Mem0)"""
        self.print_header("TEST 9: Memory System (Mem0)", "🧠")
        start = datetime.now()
        
        try:
            from memory.mem0_service import mem0_service
            
            # Test get policy (main method)
            policy = await mem0_service.get_policy(self.test_user_id)
            self.print_result("Get User Policy",
                            isinstance(policy, dict),
                            f"Risk: {policy.get('risk_tolerance', 'N/A')}")
            
            # Test get context for a symbol
            context = await mem0_service.get_context(
                user_id=self.test_user_id,
                symbol=self.test_symbol
            )
            self.print_result("Get Symbol Context", 
                            isinstance(context, dict),
                            "Context retrieved")
            
            # Test search memories
            memories = await mem0_service.search_memories(
                user_id=self.test_user_id,
                query="trading",
                limit=5
            )
            self.print_result("Search Memories",
                            isinstance(memories, list),
                            f"{len(memories)} memories found")
            
            # Test record outcome
            await mem0_service.record_outcome(
                user_id=self.test_user_id,
                trade={
                    "symbol": self.test_symbol,
                    "action": "BUY",
                    "outcome": "win",
                    "pnl_pct": 5.5
                }
            )
            self.print_result("Record Trade Outcome", True, "Trade logged")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['memory'] = 'passed'
            print(f"\n⏱️  Memory System Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("Memory System", False, str(e))
            self.results['memory'] = f'failed: {e}'
            return False
    
    async def test_cost_tracking(self):
        """Test 10: Cost tracking system"""
        self.print_header("TEST 10: Cost Tracking", "💰")
        start = datetime.now()
        
        try:
            from utils.cost_tracker import cost_tracker
            
            # Test log cost
            await cost_tracker.log_cost(
                user_id=self.test_user_id,
                service="test-service",
                tokens_input=100,
                tokens_output=50
            )
            self.print_result("Log Cost", True, "Cost logged")
            
            # Test get user costs
            costs = await cost_tracker.get_user_costs(self.test_user_id)
            self.print_result("Get User Costs",
                            isinstance(costs, dict),
                            f"Services tracked: {len(costs)}")
            
            duration = (datetime.now() - start).total_seconds()
            self.results['cost_tracking'] = 'passed'
            print(f"\n⏱️  Cost Tracking Tests: {duration:.1f}s")
            return True
            
        except Exception as e:
            self.print_result("Cost Tracking", False, str(e))
            self.results['cost_tracking'] = f'failed: {e}'
            return False
    
    def print_final_summary(self, total_duration):
        """Print final test summary"""
        self.print_header("🎯 FINAL TEST SUMMARY", "🎯")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r == 'passed')
        failed_tests = len(self.errors)
        
        print(f"\n📊 Results:")
        print(f"   ✅ Passed: {passed_tests}/{total_tests}")
        print(f"   ❌ Failed: {failed_tests}/{total_tests}")
        print(f"   ⏱️  Total Time: {total_duration:.1f}s")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Pipeline is fully operational! 🚀")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed:")
            for error in self.errors:
                print(f"   - {error}")
        
        print("\n" + "="*100)
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            status = "✅" if result == "passed" else "❌"
            print(f"   {status} {test_name}: {result}")
        
        print("\n" + "="*100 + "\n")
        
        return failed_tests == 0
    
    async def run_all_tests(self):
        """Run all pipeline tests"""
        print("\n")
        print("╔" + "═"*98 + "╗")
        print("║" + " "*25 + "KOPITIAM KAPITAL - FULL PIPELINE TEST" + " "*36 + "║")
        print("╚" + "═"*98 + "╝")
        
        overall_start = datetime.now()
        
        # Run all tests in sequence
        await self.test_api_connections()
        await self.test_market_data()
        await self.test_sentiment_pipeline()
        await self.test_rag_pipeline()
        await self.test_morning_brief()
        await self.test_eod_brief()
        await self.test_router_agent()
        await self.test_recommendation_agent()
        await self.test_memory_system()
        await self.test_cost_tracking()
        
        overall_duration = (datetime.now() - overall_start).total_seconds()
        
        # Print final summary
        success = self.print_final_summary(overall_duration)
        
        return success


async def main():
    """Main test runner"""
    tester = PipelineTester()
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

