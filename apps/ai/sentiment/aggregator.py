"""
Sentiment aggregator - Exa.ai news sentiment only
No Reddit or StockTwits
"""
from typing import Dict, Optional, List
import logging
from datetime import datetime

# Flexible imports
try:
    from ..sentiment.news_sentiment import news_sentiment_analyzer
    from ..utils.config import settings
except ImportError:
    from sentiment.news_sentiment import news_sentiment_analyzer
    from utils.config import settings

logger = logging.getLogger(__name__)

# Sentiment weights - Exa.ai (News) only
WEIGHTS = {
    'news': 1.00,  # 100% weightage to Exa.ai news sentiment
}

class SentimentAggregator:
    """
    Aggregate sentiment from multiple sources
    
    Sources:
    1. News (Exa.ai + LLM scoring) - 100% weight
    
    Features:
    - Trending detection
    - Contrarian signals (>90% = potential reversal)
    - Confidence scoring
    
    Note: Reddit and StockTwits disabled for cleaner, faster results
    """
    
    def __init__(self):
        logger.info("Initialized Sentiment Aggregator (Exa.ai only)")
    
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
            # Fetch from news source only (Exa.ai)
            news_result = await news_sentiment_analyzer.analyze(symbol, lookback_hours, user_id)
            
            # Handle exceptions
            if isinstance(news_result, Exception):
                logger.error(f"News sentiment failed: {news_result}")
                news_result = {'score': 0.5, 'article_count': 0}
            
            # Extract individual scores
            news_score = news_result.get('score', 0.5)
            
            # Calculate weighted overall score (100% from news/Exa.ai)
            overall_score = news_score * WEIGHTS['news']
            
            # Detect signals
            trending = news_result.get('trending', False)  # Only from news now
            
            # Contrarian signal: >90% bullish or <10% bearish
            contrarian_signal = overall_score > 0.90 or overall_score < 0.10
            
            # Calculate confidence based on news article count
            # More articles = higher confidence
            article_count = news_result.get('article_count', 0)
            if article_count >= 5:
                confidence = 1.0
            elif article_count >= 3:
                confidence = 0.8
            elif article_count >= 1:
                confidence = 0.6
            else:
                confidence = 0.3
            
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
                },
                'volume': {
                    'news_articles': news_result.get('article_count', 0),
                },
                'trending': trending,
                'contrarian_signal': contrarian_signal,
                'confidence': round(confidence, 2),
                'top_sources': self._compile_top_sources(news_result),
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
    
    def _compile_top_sources(self, news_result: Dict) -> List[Dict]:
        """Compile top sources from news only (Reddit disabled)"""
        sources = []
        
        # Add top news articles (top 5 since Reddit is disabled)
        for article in news_result.get('articles', [])[:5]:
            sources.append({
                'type': 'news',
                'title': article['title'],
                'url': article['url'],
                'sentiment_score': article.get('sentiment_score', 0.5),
                'sentiment_reasoning': article.get('sentiment_reasoning', 'No reasoning available'),
                'published_date': article.get('published_date')
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
            },
            'volume': {
                'news_articles': 0,
            },
            'trending': False,
            'contrarian_signal': False,
            'confidence': 0.0,
            'top_sources': [],
            'timestamp': datetime.now().isoformat()
        }

# Global instance
sentiment_aggregator = SentimentAggregator()

