"""
Sentiment aggregator - combines all sentiment sources
Weights: News 40%, Reddit 30%, StockTwits 30%
"""
from typing import Dict, Optional, List
import logging
from datetime import datetime

# Flexible imports
try:
    from ..sentiment.news_sentiment import news_sentiment_analyzer
    from ..sentiment.social_scraper import social_sentiment_analyzer
    from ..utils.config import settings
except ImportError:
    from sentiment.news_sentiment import news_sentiment_analyzer
    from sentiment.social_scraper import social_sentiment_analyzer
    from utils.config import settings

logger = logging.getLogger(__name__)

# Sentiment weights
WEIGHTS = {
    'news': 0.40,
    'reddit': 0.30,
    'stocktwits': 0.30
}

class SentimentAggregator:
    """
    Aggregate sentiment from multiple sources
    
    Sources:
    1. News (Exa.ai + LLM scoring) - 40% weight
    2. Reddit (PRAW scraping) - 30% weight
    3. StockTwits (API) - 30% weight
    
    Features:
    - Weighted aggregation
    - Trending detection
    - Contrarian signals (>90% = potential reversal)
    - Confidence scoring
    """
    
    def __init__(self):
        logger.info("Initialized Sentiment Aggregator")
    
    async def get_sentiment(
        self,
        symbol: str,
        lookback_hours: int = 24,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Get aggregated sentiment for a symbol
        
        Args:
            symbol: Stock ticker
            lookback_hours: Hours to analyze
            user_id: Optional user ID
        
        Returns:
            Complete sentiment analysis with all sources
        """
        logger.info(f"Getting aggregated sentiment for {symbol}")
        
        try:
            # Fetch from all sources in parallel
            import asyncio
            
            news_task = news_sentiment_analyzer.analyze(symbol, lookback_hours, user_id)
            social_task = social_sentiment_analyzer.analyze(symbol, lookback_hours, user_id)
            
            news_result, social_result = await asyncio.gather(
                news_task,
                social_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(news_result, Exception):
                logger.error(f"News sentiment failed: {news_result}")
                news_result = {'score': 0.5, 'article_count': 0}
            
            if isinstance(social_result, Exception):
                logger.error(f"Social sentiment failed: {social_result}")
                social_result = {
                    'combined_score': 0.5,
                    'reddit': {'score': 0.5, 'mention_count': 0},
                    'stocktwits': {'score': 0.5, 'message_count': 0}
                }
            
            # Extract individual scores
            news_score = news_result.get('score', 0.5)
            reddit_score = social_result.get('reddit', {}).get('score', 0.5)
            stocktwits_score = social_result.get('stocktwits', {}).get('score', 0.5)
            
            # Calculate weighted overall score
            overall_score = (
                news_score * WEIGHTS['news'] +
                reddit_score * WEIGHTS['reddit'] +
                stocktwits_score * WEIGHTS['stocktwits']
            )
            
            # Detect signals
            trending = (
                news_result.get('trending', False) or
                social_result.get('trending', False)
            )
            
            # Contrarian signal: >90% bullish or <10% bearish
            contrarian_signal = overall_score > 0.90 or overall_score < 0.10
            
            # Calculate confidence
            # High confidence if all sources agree
            score_variance = self._calculate_variance([news_score, reddit_score, stocktwits_score])
            confidence = 1.0 - min(score_variance * 2, 1.0)  # Low variance = high confidence
            
            # Determine trend direction
            if overall_score > 0.65:
                direction = "bullish"
            elif overall_score < 0.35:
                direction = "bearish"
            else:
                direction = "neutral"
            
            result = {
                'symbol': symbol,
                'overall_score': round(overall_score, 2),
                'direction': direction,
                'sentiment_breakdown': {
                    'news': round(news_score, 2),
                    'reddit': round(reddit_score, 2),
                    'stocktwits': round(stocktwits_score, 2)
                },
                'volume': {
                    'news_articles': news_result.get('article_count', 0),
                    'reddit_mentions': social_result.get('reddit', {}).get('mention_count', 0),
                    'stocktwits_messages': social_result.get('stocktwits', {}).get('message_count', 0)
                },
                'trending': trending,
                'contrarian_signal': contrarian_signal,
                'confidence': round(confidence, 2),
                'top_sources': self._compile_top_sources(news_result, social_result),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(
                f"Sentiment for {symbol}: {overall_score:.2f} ({direction}), "
                f"confidence: {confidence:.2f}, trending: {trending}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment aggregation failed: {e}", exc_info=True)
            # Return neutral sentiment on error
            return self._neutral_sentiment(symbol)
    
    def _calculate_variance(self, scores: List[float]) -> float:
        """Calculate variance of scores (for confidence)"""
        if not scores:
            return 0.5
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        
        return variance
    
    def _compile_top_sources(self, news_result: Dict, social_result: Dict) -> List[Dict]:
        """Compile top sources from all channels"""
        sources = []
        
        # Add top news articles
        for article in news_result.get('articles', [])[:3]:
            sources.append({
                'type': 'news',
                'title': article['title'],
                'url': article['url'],
                'sentiment_score': article.get('sentiment_score', 0.5),
                'published_date': article.get('published_date')
            })
        
        # Add top Reddit posts
        for post in social_result.get('reddit', {}).get('top_posts', [])[:2]:
            sources.append({
                'type': 'reddit',
                'title': post['title'],
                'url': post['url'],
                'sentiment_score': post['score'],
                'engagement': post.get('upvotes', 0)
            })
        
        return sources
    
    def _neutral_sentiment(self, symbol: str) -> Dict:
        """Return neutral sentiment when analysis fails"""
        return {
            'symbol': symbol,
            'overall_score': 0.5,
            'direction': 'neutral',
            'sentiment_breakdown': {
                'news': 0.5,
                'reddit': 0.5,
                'stocktwits': 0.5
            },
            'volume': {
                'news_articles': 0,
                'reddit_mentions': 0,
                'stocktwits_messages': 0
            },
            'trending': False,
            'contrarian_signal': False,
            'confidence': 0.0,
            'top_sources': [],
            'timestamp': datetime.now().isoformat()
        }

# Global instance
sentiment_aggregator = SentimentAggregator()

