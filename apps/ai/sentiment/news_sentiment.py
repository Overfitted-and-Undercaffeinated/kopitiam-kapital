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
{{
  "score": 0.75,
  "reasoning": "Brief explanation of why this score"
}}

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
            # Use better query to get actual news articles, not stock quote pages
            query = f"{symbol} latest news analysis earnings revenue -'stock price' -'stock quote'"
            
            articles = await exa_client.search_fast(
                query=query,
                num_results=15,  # Get more to compensate for filtering
                user_id=user_id
            )
            
            if not articles:
                logger.warning(f"No news articles found for {symbol}")
                return self._empty_sentiment(symbol)
            
            # Step 2: Score each article
            scored_articles = []
            
            for article in articles[:5]:  # Score top 5 only (cost control)
                try:
                    # Skip articles with no content (just titles/stock quotes)
                    article_text = article.get('text', '')
                    article_title = article.get('title', '')
                    
                    # Skip if article is just a stock quote page or has minimal content
                    skip_keywords = ['stock quote', 'stock price', 'latest stock news', 'annual income statement']
                    if any(keyword in article_title.lower() for keyword in skip_keywords):
                        logger.debug(f"Skipping non-news article: {article_title}")
                        continue
                    
                    # Skip if no meaningful content
                    if len(article_text) < 50 and len(article_title) < 50:
                        logger.debug(f"Skipping article with insufficient content: {article_title}")
                        continue
                    
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
                    logger.error(f"Failed to score article '{article.get('title', 'N/A')[:50]}...': {type(e).__name__}: {str(e)[:100]}")
                    import traceback
                    logger.debug(f"Full traceback:\n{traceback.format_exc()}")
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
            # Get article content
            article_text = article.get('text', '').strip()
            article_title = article.get('title', '')
            article_highlights = article.get('highlights', [])
            
            logger.debug(f"Scoring article: {article_title[:50]}... (text: {len(article_text)} chars, highlights: {len(article_highlights) if article_highlights else 0})")
            
            # Check for paywall/error content
            paywall_indicators = ['oops, something went wrong', 'upgrade now', 'subscribe', 'login required']
            is_paywall = any(indicator in article_text.lower() for indicator in paywall_indicators)
            
            # Use highlights if available and not paywall, otherwise use text or title
            if article_highlights and not is_paywall:
                # Highlights are usually the best content
                content_to_analyze = ' '.join(article_highlights[:3])[:500]
            elif len(article_text) > 50 and not is_paywall:
                # Use text if substantial and not paywalled
                content_to_analyze = article_text[:500]
            else:
                # Fall back to title + any available snippet
                content_to_analyze = f"{article_title}. {article_text[:200]}"
            
            # Build prompt
            logger.debug(f"Building prompt with: title_len={len(article_title)}, content_len={len(content_to_analyze)}, symbol={symbol}")
            
            try:
                prompt = SENTIMENT_SCORING_PROMPT.format(
                    title=article_title,
                    text=content_to_analyze,
                    symbol=symbol
                )
                logger.debug(f"Prompt built successfully, length: {len(prompt)}")
            except KeyError as ke:
                logger.error(f"KeyError in format(): {ke}. Template placeholders might be wrong.")
                logger.error(f"SENTIMENT_SCORING_PROMPT has: {SENTIMENT_SCORING_PROMPT[:200]}")
                raise
            
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
            
            if not content or not content.strip():
                raise ValueError("Empty response from Groq")
            
            logger.debug(f"Raw Groq response (first 200 chars): {repr(content[:200])}")
            
            # Try to parse JSON
            try:
                result = json.loads(content)
                logger.debug(f"Successfully parsed JSON. Keys: {list(result.keys())}, Score: {result.get('score', 'MISSING')}")
            except json.JSONDecodeError as je:
                logger.warning(f"Invalid JSON from Groq (pos {je.pos}): {content[:150]}")
                # Try to extract score from text if possible
                if '"score"' in content and ':' in content:
                    # Attempt to extract score value
                    import re
                    score_match = re.search(r'"score"\s*:\s*([\d.]+)', content)
                    if score_match:
                        score = float(score_match.group(1))
                        logger.info(f"Extracted score {score} from malformed JSON")
                        return {'score': max(0.0, min(1.0, score)), 'reasoning': 'Extracted from malformed JSON'}
                # If can't extract, re-raise
                logger.error(f"Could not extract score from: {content}")
                raise je
            
            # Validate result has expected keys
            if 'score' not in result:
                logger.warning(f"Groq response missing 'score' key: {result}")
                return {'score': 0.5, 'reasoning': 'Invalid response format'}
            
            # Groq is free, but log for analytics
            if user_id:
                await cost_tracker.log_cost(
                    user_id=user_id,
                    service="groq-sentiment-scoring",
                    tokens_input=len(prompt) // 4,
                    tokens_output=len(content) // 4
                )
            
            return {
                'score': max(0.0, min(1.0, float(result['score']))),  # Clamp to 0-1
                'reasoning': result.get('reasoning', 'No reasoning provided')
            }
            
        except Exception as e:
            logger.debug(f"Scoring error details for '{article.get('title', 'N/A')[:50]}...': {type(e).__name__}: {str(e)[:200]}")
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

