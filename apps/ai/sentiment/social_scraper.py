"""
Social media sentiment scraper
Sources: Reddit (PRAW) + StockTwits (API)
"""
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import re

# Flexible imports
try:
    from ..utils.config import settings
    from ..utils.cost_tracker import cost_tracker
except ImportError:
    from utils.config import settings
    from utils.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)

# Bullish/bearish keywords for simple sentiment
BULLISH_KEYWORDS = [
    'bullish', 'buy', 'calls', 'moon', 'rocket', 'breakout', 'rally',
    'strong', 'beat', 'upgrade', 'positive', 'growth', 'momentum',
    'opportunity', 'undervalued', 'accumulate', 'long'
]

BEARISH_KEYWORDS = [
    'bearish', 'sell', 'puts', 'crash', 'dump', 'breakdown', 'decline',
    'weak', 'miss', 'downgrade', 'negative', 'loss', 'overvalued',
    'avoid', 'short', 'bubble'
]

class SocialSentimentAnalyzer:
    """
    Analyze social media sentiment from Reddit and StockTwits
    
    Features:
    - Reddit: r/wallstreetbets, r/stocks, r/investing
    - StockTwits: Public API
    - Keyword-based sentiment scoring
    - Volume and trending detection
    """
    
    def __init__(self):
        self.praw_client = None
        self.stocktwits_available = True
        
        # Initialize PRAW (Reddit)
        try:
            import praw
            
            # Get credentials from .env
            client_id = getattr(settings, 'client_id', None)
            client_secret = getattr(settings, 'client_secret', None)
            user_agent = getattr(settings, 'user_agent', 'meme-sentiment-analysis')
            
            if client_id and client_secret:
                self.praw_client = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                logger.info("Initialized PRAW for Reddit scraping")
            else:
                logger.warning("Reddit credentials not found in .env. Reddit sentiment disabled.")
        
        except ImportError:
            logger.warning("PRAW not installed. Install with: pip install praw")
        except Exception as e:
            logger.error(f"Failed to initialize PRAW: {e}")
    
    async def analyze(
        self,
        symbol: str,
        lookback_hours: int = 24,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Analyze social sentiment for a symbol
        
        Args:
            symbol: Stock ticker
            lookback_hours: Hours to look back (default: 24)
            user_id: Optional user ID
        
        Returns:
            {
                'reddit': {score, mention_count, top_posts},
                'stocktwits': {score, message_count},
                'combined_score': float,
                'total_mentions': int,
                'trending': bool
            }
        """
        logger.info(f"Analyzing social sentiment for {symbol}")
        
        # Parallel analysis
        reddit_result = await self._analyze_reddit(symbol, lookback_hours)
        stocktwits_result = await self._analyze_stocktwits(symbol)
        
        # Combine scores (50/50 weight)
        if reddit_result['mention_count'] > 0 and stocktwits_result['message_count'] > 0:
            combined_score = (reddit_result['score'] * 0.5) + (stocktwits_result['score'] * 0.5)
        elif reddit_result['mention_count'] > 0:
            combined_score = reddit_result['score']
        elif stocktwits_result['message_count'] > 0:
            combined_score = stocktwits_result['score']
        else:
            combined_score = 0.5  # Neutral if no data
        
        total_mentions = reddit_result['mention_count'] + stocktwits_result['message_count']
        
        # Trending if >100 mentions in 24h
        trending = total_mentions > 100
        
        return {
            'reddit': reddit_result,
            'stocktwits': stocktwits_result,
            'combined_score': combined_score,
            'total_mentions': total_mentions,
            'trending': trending,
            'source': 'social'
        }
    
    async def _analyze_reddit(self, symbol: str, lookback_hours: int) -> Dict:
        """
        Analyze Reddit sentiment
        
        Returns:
            {score, mention_count, top_posts}
        """
        if not self.praw_client:
            logger.warning("🚨 MOCK MODE - Reddit not configured, returning neutral")
            return {'score': 0.5, 'mention_count': 0, 'top_posts': []}
        
        try:
            subreddits = ['wallstreetbets', 'stocks', 'investing']
            all_mentions = []
            
            cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.praw_client.subreddit(subreddit_name)
                    
                    # Search for symbol mentions
                    for submission in subreddit.search(symbol, time_filter='day', limit=100):
                        # Check if recent enough
                        post_time = datetime.fromtimestamp(submission.created_utc)
                        
                        if post_time < cutoff_time:
                            continue
                        
                        # Combine title + selftext for analysis
                        text = f"{submission.title} {submission.selftext}"
                        
                        # Simple keyword-based sentiment
                        sentiment = self._calculate_keyword_sentiment(text)
                        
                        all_mentions.append({
                            'title': submission.title,
                            'url': f"https://reddit.com{submission.permalink}",
                            'score': sentiment,
                            'upvotes': submission.score,
                            'comments': submission.num_comments,
                            'subreddit': subreddit_name,
                            'created_at': post_time.isoformat()
                        })
                
                except Exception as e:
                    logger.error(f"Error scraping r/{subreddit_name}: {e}")
            
            if not all_mentions:
                return {'score': 0.5, 'mention_count': 0, 'top_posts': []}
            
            # Calculate average sentiment
            avg_sentiment = sum(m['score'] for m in all_mentions) / len(all_mentions)
            
            # Sort by engagement (upvotes * comments)
            top_posts = sorted(
                all_mentions,
                key=lambda x: x['upvotes'] * (x['comments'] + 1),
                reverse=True
            )[:5]
            
            logger.info(
                f"Reddit: {len(all_mentions)} mentions, "
                f"avg sentiment: {avg_sentiment:.2f}"
            )
            
            return {
                'score': avg_sentiment,
                'mention_count': len(all_mentions),
                'top_posts': top_posts
            }
            
        except Exception as e:
            logger.error(f"Reddit analysis failed: {e}")
            return {'score': 0.5, 'mention_count': 0, 'top_posts': []}
    
    async def _analyze_stocktwits(self, symbol: str) -> Dict:
        """
        Analyze StockTwits sentiment
        
        Uses StockTwits API which provides sentiment scores
        """
        try:
            import httpx
            
            # StockTwits API endpoint
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    logger.warning(f"StockTwits API error: {response.status_code}")
                    return {'score': 0.5, 'message_count': 0}
                
                data = response.json()
                messages = data.get('messages', [])
                
                if not messages:
                    return {'score': 0.5, 'message_count': 0}
                
                # StockTwits provides sentiment in each message
                sentiment_counts = {'bullish': 0, 'bearish': 0, 'neutral': 0}
                
                for msg in messages:
                    sentiment = msg.get('entities', {}).get('sentiment')
                    
                    if sentiment:
                        sentiment_type = sentiment.get('basic')
                        if sentiment_type:
                            sentiment_counts[sentiment_type.lower()] = sentiment_counts.get(sentiment_type.lower(), 0) + 1
                
                # Calculate score
                total_with_sentiment = sentiment_counts['bullish'] + sentiment_counts['bearish']
                
                if total_with_sentiment > 0:
                    bullish_pct = sentiment_counts['bullish'] / total_with_sentiment
                    score = bullish_pct  # Already 0-1
                else:
                    score = 0.5
                
                logger.info(
                    f"StockTwits: {len(messages)} messages, "
                    f"{sentiment_counts['bullish']} bullish, "
                    f"{sentiment_counts['bearish']} bearish, score: {score:.2f}"
                )
                
                return {
                    'score': score,
                    'message_count': len(messages),
                    'bullish_count': sentiment_counts['bullish'],
                    'bearish_count': sentiment_counts['bearish']
                }
        
        except Exception as e:
            logger.error(f"StockTwits analysis failed: {e}")
            return {'score': 0.5, 'message_count': 0}
    
    def _calculate_keyword_sentiment(self, text: str) -> float:
        """
        Simple keyword-based sentiment calculation
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment score 0-1
        """
        text_lower = text.lower()
        
        bullish_count = sum(1 for word in BULLISH_KEYWORDS if word in text_lower)
        bearish_count = sum(1 for word in BEARISH_KEYWORDS if word in text_lower)
        
        total = bullish_count + bearish_count
        
        if total == 0:
            return 0.5  # Neutral
        
        # Convert to 0-1 score
        bullish_pct = bullish_count / total
        
        return bullish_pct

# Global instance
social_sentiment_analyzer = SocialSentimentAnalyzer()

