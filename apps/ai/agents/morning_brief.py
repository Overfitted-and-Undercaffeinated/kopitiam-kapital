"""
Morning Brief Generator
Personalized pre-market analysis with voice narration
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Flexible imports
try:
    from ..sentiment.aggregator import sentiment_aggregator
    from ..retrievers.exa_client import exa_client
    from ..memory.mem0_service import mem0_service
    from ..utils.clients import get_openai_client
    from ..utils.cost_tracker import cost_tracker
    from ..utils.disclaimers import add_disclaimer_to_brief
    from ..voice.brief_narrator import brief_narrator
    from ..utils.market_hours import market_hours
except ImportError:
    from sentiment.aggregator import sentiment_aggregator
    from retrievers.exa_client import exa_client
    from memory.mem0_service import mem0_service
    from utils.clients import get_openai_client
    from utils.cost_tracker import cost_tracker
    from utils.disclaimers import add_disclaimer_to_brief
    from voice.brief_narrator import brief_narrator
    from utils.market_hours import market_hours

logger = logging.getLogger(__name__)

class MorningBriefAgent:
    """
    Generate personalized morning market briefs
    
    Features:
    - Watchlist sentiment analysis
    - Pre-market movers identification
    - Personalized insights from Mem0
    - Voice narration with ElevenLabs
    - <2 minute read/listen time
    """
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = "gpt-4o-mini"
        logger.info("Initialized Morning Brief Agent")
    
    async def generate_brief(
        self,
        watchlist: List[str],
        market: str,
        user_id: str,
        include_voice: bool = True
    ) -> Dict:
        """
        Generate morning market brief
        
        Args:
            watchlist: List of symbols to analyze
            market: Market name (US, SGX, etc)
            user_id: User ID for personalization
            include_voice: Whether to generate voice narration
        
        Returns:
            {
                'type': 'morning',
                'text': str,
                'audio_base64': Optional[str],
                'symbols_analyzed': List[str],
                'sentiment_summary': Dict,
                'generated_at': str
            }
        """
        logger.info(f"Generating morning brief for {user_id}, watchlist: {watchlist}, market: {market}")
        
        # Validate watchlist
        if not watchlist or len(watchlist) == 0:
            raise ValueError("Watchlist cannot be empty. Please provide at least one symbol.")
        
        try:
            # Step 1: Get user profile from Mem0
            user_policy = await mem0_service.get_policy(user_id)
            greeting = self._get_personalized_greeting(user_policy)
            
            # Step 2: Analyze watchlist sentiment
            watchlist_analysis = []
            
            for symbol in watchlist:
                sentiment = await sentiment_aggregator.get_sentiment(
                    symbol=symbol,
                    user_id=user_id
                )
                watchlist_analysis.append({
                    'symbol': symbol,
                    'sentiment_score': sentiment['overall_score'],
                    'direction': sentiment['direction'],
                    'trending': sentiment['trending']
                })
            
            # Step 3: Identify top movers from watchlist
            sorted_by_sentiment = sorted(watchlist_analysis, key=lambda x: x['sentiment_score'], reverse=True)
            top_bullish = sorted_by_sentiment[:3]
            top_bearish = sorted_by_sentiment[-3:]
            
            # Step 4: Get broader market context with Exa
            market_context = await self._get_market_context(market)
            
            # Step 5: Generate brief text with GPT-4o-mini
            brief_text = await self._generate_brief_text(
                greeting=greeting,
                market=market,
                watchlist_analysis=watchlist_analysis,
                top_bullish=top_bullish,
                top_bearish=top_bearish,
                market_context=market_context,
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
            
            # Step 7: Prepare sentiment summary
            sentiment_summary = {
                'average_sentiment': sum(s['sentiment_score'] for s in watchlist_analysis) / len(watchlist_analysis),
                'bullish_count': sum(1 for s in watchlist_analysis if s['direction'] == 'bullish'),
                'bearish_count': sum(1 for s in watchlist_analysis if s['direction'] == 'bearish'),
                'trending_count': sum(1 for s in watchlist_analysis if s['trending'])
            }
            
            return {
                'type': 'morning',
                'text': brief_text,
                'audio_base64': audio_base64,
                'symbols_analyzed': watchlist,
                'sentiment_summary': sentiment_summary,
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating morning brief: {e}")
            raise
    
    def _get_personalized_greeting(self, user_policy: Dict) -> str:
        """Generate personalized greeting based on user profile"""
        risk_tolerance = user_policy.get('risk_tolerance', 'moderate')
        
        if risk_tolerance == 'conservative':
            return "Good morning! Here's your cautious market overview"
        elif risk_tolerance == 'aggressive':
            return "Good morning! Here's your high-conviction market overview"
        else:
            return "Good morning! Here's your market overview"
    
    async def _get_market_context(self, market: str) -> str:
        """Get broader market context using Exa"""
        try:
            # Search for pre-market news
            query = f"{market} market pre-market movers news today"
            
            results = await exa_client.search_fast(
                query=query,
                num_results=3
            )
            
            if results:
                # Extract key headlines
                headlines = [r.get('title', '') for r in results[:3]]
                return " ".join(headlines[:2])  # Top 2 headlines
            else:
                return "Market opening soon"
        
        except Exception as e:
            logger.error(f"Failed to get market context: {e}")
            return "Market opening soon"
    
    async def _generate_brief_text(
        self,
        greeting: str,
        market: str,
        watchlist_analysis: List[Dict],
        top_bullish: List[Dict],
        top_bearish: List[Dict],
        market_context: str,
        user_id: str
    ) -> str:
        """
        Generate brief text with GPT-4o-mini
        
        Target: <400 words, ~2 minute read
        """
        # Build watchlist summary
        watchlist_items = []
        for item in watchlist_analysis:
            direction_emoji = "↑" if item['direction'] == 'bullish' else "↓" if item['direction'] == 'bearish' else "→"
            trending_note = " (TRENDING)" if item['trending'] else ""
            watchlist_items.append(
                f"- {item['symbol']}: {item['sentiment_score']:.2f} {direction_emoji}{trending_note}"
            )
        
        # Create prompt for GPT
        prompt = f"""Generate a concise morning market brief (MAX 350 words, ~2 minute read).

Greeting: {greeting}
Market: {market}
Market Context: {market_context}

Watchlist Sentiment:
{chr(10).join(watchlist_items)}

Top Bullish: {', '.join(s['symbol'] for s in top_bullish[:3])}
Top Bearish: {', '.join(s['symbol'] for s in top_bearish[:3])}

Create a brief that:
1. Starts with the greeting
2. Mentions market overview context briefly
3. Highlights watchlist analysis (1 line per symbol with insight)
4. Points out top bullish and bearish from watchlist
5. Ends with 1-2 sentence key insight or market thesis
6. Is concise, professional, and under 350 words
7. Uses natural language suitable for voice narration

Format for voice narration - avoid special characters, use natural speech."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional market analyst creating concise morning briefs. Be clear, concise, and insightful. Maximum 350 words."},
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
                    service="openai-morning-brief",
                    tokens_input=response.usage.prompt_tokens,
                    tokens_output=response.usage.completion_tokens,
                    metadata={"watchlist_size": len(watchlist_analysis)}
                )
            
            logger.info(f"Generated morning brief: {len(brief_text)} chars")
            return brief_text
        
        except Exception as e:
            logger.error(f"Failed to generate brief text: {e}")
            # Fallback to simple text
            return self._generate_fallback_brief(greeting, market, watchlist_analysis)
    
    def _generate_fallback_brief(
        self,
        greeting: str,
        market: str,
        watchlist_analysis: List[Dict]
    ) -> str:
        """Simple fallback brief if GPT fails"""
        lines = [f"{greeting}\n"]
        lines.append(f"Market: {market}\n")
        lines.append("\nYour Watchlist:")
        
        for item in watchlist_analysis:
            lines.append(f"- {item['symbol']}: {item['sentiment_score']:.2f} ({item['direction']})")
        
        avg_sentiment = sum(s['sentiment_score'] for s in watchlist_analysis) / len(watchlist_analysis)
        lines.append(f"\nAverage sentiment: {avg_sentiment:.2f}")
        
        return "\n".join(lines)

# Global instance
morning_brief_agent = MorningBriefAgent()

