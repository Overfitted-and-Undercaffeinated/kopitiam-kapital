"""
End-of-Day Brief Generator
Post-market analysis with performance tracking and AI insights
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Flexible imports
try:
    from ..sentiment.aggregator import sentiment_aggregator
    from ..retrievers.exa_client import exa_client
    from ..data.market_data import market_data_service
    from ..rag.pipeline import rag_pipeline
    from ..utils.clients import get_openai_client
    from ..utils.cost_tracker import cost_tracker
    from ..utils.disclaimers import add_disclaimer_to_brief
    from ..voice.brief_narrator import brief_narrator
except ImportError:
    from sentiment.aggregator import sentiment_aggregator
    from retrievers.exa_client import exa_client
    from data.market_data import market_data_service
    from rag.pipeline import rag_pipeline
    from utils.clients import get_openai_client
    from utils.cost_tracker import cost_tracker
    from utils.disclaimers import add_disclaimer_to_brief
    from voice.brief_narrator import brief_narrator

logger = logging.getLogger(__name__)

class EODBriefAgent:
    """
    Generate end-of-day market briefs
    
    Features:
    - Watchlist performance tracking (day's % change)
    - Sentiment analysis
    - AI research on why top movers moved
    - Tomorrow's outlook prediction
    - Voice narration with ElevenLabs
    - <2 minute read/listen time
    """
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = "gpt-4o-mini"
        logger.info("Initialized EOD Brief Agent")
    
    async def generate_brief(
        self,
        watchlist: List[str],
        market: str,
        user_id: str,
        include_voice: bool = True
    ) -> Dict:
        """
        Generate end-of-day market brief
        
        Args:
            watchlist: List of symbols to analyze
            market: Market name (US, SGX, etc)
            user_id: User ID for personalization
            include_voice: Whether to generate voice narration
        
        Returns:
            {
                'type': 'eod',
                'text': str,
                'audio_base64': Optional[str],
                'symbols_analyzed': List[str],
                'performance_summary': Dict,
                'generated_at': str
            }
        """
        logger.info(f"Generating EOD brief for {user_id}, watchlist: {watchlist}, market: {market}")
        
        try:
            # Step 1: Get EOD performance for watchlist
            performance_data = await self._get_watchlist_performance(watchlist)
            
            # Step 2: Get current sentiment for each symbol
            sentiment_data = []
            
            for symbol in watchlist:
                sentiment = await sentiment_aggregator.get_sentiment(
                    symbol=symbol,
                    user_id=user_id
                )
                perf = next((p for p in performance_data if p['symbol'] == symbol), None)
                
                sentiment_data.append({
                    'symbol': symbol,
                    'sentiment_score': sentiment['overall_score'],
                    'direction': sentiment['direction'],
                    'price_change_pct': perf['change_pct'] if perf else 0.0
                })
            
            # Step 3: Identify top movers
            sorted_by_performance = sorted(sentiment_data, key=lambda x: abs(x['price_change_pct']), reverse=True)
            top_movers = sorted_by_performance[:3]
            
            # Step 4: Research why top movers moved (using Exa + RAG)
            market_drivers = await self._research_market_drivers(top_movers[:2], user_id)  # Top 2 only
            
            # Step 5: Generate brief text with GPT-4o-mini
            brief_text = await self._generate_brief_text(
                market=market,
                sentiment_data=sentiment_data,
                top_movers=top_movers,
                market_drivers=market_drivers,
                user_id=user_id
            )
            
            # Add disclaimer
            brief_text = add_disclaimer_to_brief(brief_text)
            
            # Step 6: Generate voice narration
            audio_base64 = None
            if include_voice and brief_narrator.enabled:
                audio_bytes = await brief_narrator.generate_voice(
                    text=brief_text,
                    user_id=user_id
                )
                
                if audio_bytes:
                    audio_base64 = brief_narrator.encode_audio(audio_bytes)
                    logger.info(f"Voice narration generated: {len(audio_bytes)} bytes")
            
            # Step 7: Performance summary
            performance_summary = {
                'gainers': sum(1 for s in sentiment_data if s['price_change_pct'] > 0),
                'losers': sum(1 for s in sentiment_data if s['price_change_pct'] < 0),
                'average_change': sum(s['price_change_pct'] for s in sentiment_data) / len(sentiment_data),
                'sentiment_improved': sum(1 for s in sentiment_data if s['sentiment_score'] > 0.55),
                'sentiment_declined': sum(1 for s in sentiment_data if s['sentiment_score'] < 0.45)
            }
            
            return {
                'type': 'eod',
                'text': brief_text,
                'audio_base64': audio_base64,
                'symbols_analyzed': watchlist,
                'performance_summary': performance_summary,
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating EOD brief: {e}")
            raise
    
    async def _get_watchlist_performance(self, watchlist: List[str]) -> List[Dict]:
        """Get today's price performance for watchlist"""
        performance = []
        
        for symbol in watchlist:
            try:
                # Get today's data (intraday)
                current_price = await market_data_service.get_latest_price(symbol)
                
                # Get yesterday's close to calculate change
                historical = await market_data_service.get_ohlcv(symbol, period="2d", interval="1d")
                
                if current_price and not historical.empty and len(historical) >= 2:
                    historical.columns = historical.columns.str.lower()
                    yesterday_close = historical['close'].iloc[-2]
                    change_pct = ((current_price - yesterday_close) / yesterday_close) * 100
                else:
                    change_pct = 0.0
                
                performance.append({
                    'symbol': symbol,
                    'current_price': current_price,
                    'change_pct': change_pct
                })
            
            except Exception as e:
                logger.error(f"Failed to get performance for {symbol}: {e}")
                performance.append({
                    'symbol': symbol,
                    'current_price': 0.0,
                    'change_pct': 0.0
                })
        
        return performance
    
    async def _research_market_drivers(self, top_movers: List[Dict], user_id: str) -> List[Dict]:
        """Research why top movers moved using RAG pipeline"""
        drivers = []
        
        for mover in top_movers:
            symbol = mover['symbol']
            change = mover['price_change_pct']
            
            try:
                # Use RAG to research
                query = f"Why did {symbol} stock move {change:.1f}% today? What news or events drove this?"
                
                insight = await rag_pipeline.retrieve_and_generate(
                    query=query,
                    user_id=user_id
                )
                
                drivers.append({
                    'symbol': symbol,
                    'change_pct': change,
                    'insight': insight.get('response', 'No specific catalyst identified')[:150]  # Keep concise
                })
            
            except Exception as e:
                logger.error(f"Failed to research {symbol}: {e}")
                drivers.append({
                    'symbol': symbol,
                    'change_pct': change,
                    'insight': 'Analysis unavailable'
                })
        
        return drivers
    
    async def _generate_brief_text(
        self,
        market: str,
        sentiment_data: List[Dict],
        top_movers: List[Dict],
        market_drivers: List[Dict],
        user_id: str
    ) -> str:
        """
        Generate EOD brief text with GPT-4o-mini
        
        Target: <400 words, ~2 minute read
        """
        # Build performance summary
        perf_items = []
        for item in sentiment_data:
            change_str = f"+{item['price_change_pct']:.1f}%" if item['price_change_pct'] > 0 else f"{item['price_change_pct']:.1f}%"
            direction = "↑" if item['sentiment_score'] > 0.55 else "↓" if item['sentiment_score'] < 0.45 else "→"
            perf_items.append(
                f"- {item['symbol']}: {change_str} | Sentiment: {item['sentiment_score']:.2f} {direction}"
            )
        
        # Build drivers summary
        driver_items = []
        for driver in market_drivers:
            change_str = "surged" if driver['change_pct'] > 0 else "fell"
            driver_items.append(
                f"- {driver['symbol']} {change_str} {abs(driver['change_pct']):.1f}%: {driver['insight']}"
            )
        
        prompt = f"""Generate a concise end-of-day market brief (MAX 350 words, ~2 minute read).

Market Close: {market}

Watchlist Performance:
{chr(10).join(perf_items)}

Today's Key Drivers:
{chr(10).join(driver_items) if driver_items else '- No major catalysts identified'}

Create a brief that:
1. Opens with "Market close for {market}"
2. Summarizes watchlist performance
3. Explains what drove the top movers (use the insights provided)
4. Notes sentiment shifts
5. Ends with 1-2 sentence outlook for tomorrow
6. Is concise, professional, and under 350 words
7. Uses natural language suitable for voice narration

Format for voice - avoid special characters, use natural speech."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional market analyst creating concise EOD briefs. Be clear, actionable, and insightful. Maximum 350 words."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            brief_text = response.choices[0].message.content.strip()
            
            # Track cost
            if user_id:
                await cost_tracker.log_cost(
                    user_id=user_id,
                    service="openai-eod-brief",
                    tokens_input=response.usage.prompt_tokens,
                    tokens_output=response.usage.completion_tokens,
                    metadata={"watchlist_size": len(sentiment_data)}
                )
            
            logger.info(f"Generated EOD brief: {len(brief_text)} chars")
            return brief_text
        
        except Exception as e:
            logger.error(f"Failed to generate brief text: {e}")
            # Fallback
            return self._generate_fallback_brief(market, sentiment_data)
    
    def _generate_fallback_brief(self, market: str, sentiment_data: List[Dict]) -> str:
        """Simple fallback brief if GPT fails"""
        lines = [f"Market close for {market}\n"]
        lines.append("Your Watchlist Performance:")
        
        for item in sentiment_data:
            change_str = f"+{item['price_change_pct']:.1f}%" if item['price_change_pct'] > 0 else f"{item['price_change_pct']:.1f}%"
            lines.append(f"- {item['symbol']}: {change_str}, Sentiment: {item['sentiment_score']:.2f}")
        
        avg_change = sum(s['price_change_pct'] for s in sentiment_data) / len(sentiment_data)
        lines.append(f"\nAverage change: {avg_change:+.1f}%")
        
        return "\n".join(lines)

# Global instance
eod_brief_agent = EODBriefAgent()

