"""
News sentiment analysis via Exa.ai
Scores financial news articles for bullish/bearish sentiment
"""
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import json

# Flexible imports
try:
    from ..retrievers.exa_client import exa_client
    from ..utils.clients import get_groq_client
    from ..utils.cost_tracker import cost_tracker
    from ..utils.config import settings
except ImportError:
    from retrievers.exa_client import exa_client
    from utils.clients import get_groq_client
    from utils.cost_tracker import cost_tracker
    from utils.config import settings

logger = logging.getLogger(__name__)

# Simple sentiment scoring prompt
SENTIMENT_SCORING_PROMPT = """You are a financial sentiment analyzer. 

Analyze this article and return a sentiment score for the mentioned stock.

Score:
- 0.0 = Very Bearish (bad news, sell recommendation, negative outlook)
- 0.3 = Bearish (concerns, risks, downgrades)
- 0.5 = Neutral (mixed or factual reporting)
- 0.7 = Bullish (positive news, opportunities)
- 1.0 = Very Bullish (strong buy signals, major positive developments)

Return ONLY a JSON object:
{
  "score": 0.75,
  "reasoning": "Brief explanation of why this score"
}

Article title: {title}
Article content: {text}
Symbol: {symbol}"""

class NewsSentimentAnalyzer:
    """
    Analyze news sentiment using Exa.ai + LLM scoring
    
    Process:
    1. Search Exa for latest news on symbol
    2. Score each article with LLM (0-1 scale)
    3. Aggregate to overall news sentiment
    4. Return top articles with scores
    """
    
    def __init__(self):
        self.client = get_groq_client()  # Use free Groq for scoring
        self.model = "llama-3.3-70b-versatile"
        logger.info("Initialized News Sentiment Analyzer with Groq")
    
    async def analyze(
        self,
        symbol: str,
        lookback_hours: int = 24,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Analyze news sentiment for a symbol
        
        Args:
            symbol: Stock ticker
            lookback_hours: How far back to look (default: 24 hours)
            user_id: Optional user ID for cost tracking
        
        Returns:
            {
                'score': float (0-1),
                'article_count': int,
                'articles': List[Dict],  # Top 5 scored articles
                'trending': bool
            }
        """
        logger.info(f"Analyzing news sentiment for {symbol} (last {lookback_hours}h)")
        
        try:
            # Step 1: Search Exa for latest news
            query = f"{symbol} stock news earnings analysis"
            
            articles = await exa_client.search_fast(
                query=query,
                num_results=10,  # Get more, score top 5
                user_id=user_id
            )
            
            if not articles:
                logger.warning(f"No news articles found for {symbol}")
                return self._empty_sentiment(symbol)
            
            # Step 2: Score each article
            scored_articles = []
            
            for article in articles[:5]:  # Score top 5 only (cost control)
                try:
                    score_result = await self._score_article(
                        article=article,
                        symbol=symbol,
                        user_id=user_id
                    )
                    
                    scored_articles.append({
                        'title': article['title'],
                        'url': article['url'],
                        'published_date': article.get('published_date'),
                        'text': article.get('text', '')[:200],  # Snippet only
                        'sentiment_score': score_result['score'],
                        'sentiment_reasoning': score_result['reasoning']
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to score article: {e}")
                    # Continue with other articles
            
            if not scored_articles:
                return self._empty_sentiment(symbol)
            
            # Step 3: Aggregate scores
            avg_score = sum(a['sentiment_score'] for a in scored_articles) / len(scored_articles)
            
            # Step 4: Detect trending
            trending = len(articles) > 15  # More than 15 articles in 24h = trending
            
            logger.info(
                f"News sentiment for {symbol}: {avg_score:.2f} "
                f"({len(scored_articles)} articles, trending={trending})"
            )
            
            return {
                'score': avg_score,
                'article_count': len(scored_articles),
                'articles': scored_articles,
                'trending': trending,
                'source': 'news'
            }
            
        except Exception as e:
            logger.error(f"News sentiment analysis failed: {e}")
            return self._empty_sentiment(symbol)
    
    async def _score_article(
        self,
        article: Dict,
        symbol: str,
        user_id: Optional[str]
    ) -> Dict:
        """
        Score a single article using LLM
        
        Args:
            article: Article dict from Exa
            symbol: Stock symbol
            user_id: User ID for cost tracking
        
        Returns:
            {score: float, reasoning: str}
        """
        try:
            # Build prompt
            prompt = SENTIMENT_SCORING_PROMPT.format(
                title=article['title'],
                text=article.get('text', article['title'])[:500],  # First 500 chars
                symbol=symbol
            )
            
            # Call Groq (free, fast)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Groq is free, but log for analytics
            if user_id:
                await cost_tracker.log_cost(
                    user_id=user_id,
                    service="groq-sentiment-scoring",
                    tokens_input=len(prompt) // 4,
                    tokens_output=len(content) // 4
                )
            
            return {
                'score': max(0.0, min(1.0, result.get('score', 0.5))),  # Clamp to 0-1
                'reasoning': result.get('reasoning', 'No reasoning provided')
            }
            
        except Exception as e:
            logger.error(f"Failed to score article '{article.get('title', 'N/A')}': {e}")
            # Neutral score on failure
            return {'score': 0.5, 'reasoning': 'Scoring failed, defaulting to neutral'}
    
    def _empty_sentiment(self, symbol: str) -> Dict:
        """Return empty/neutral sentiment when no data available"""
        return {
            'score': 0.5,
            'article_count': 0,
            'articles': [],
            'trending': False,
            'source': 'news'
        }

# Global instance
news_sentiment_analyzer = NewsSentimentAnalyzer()

