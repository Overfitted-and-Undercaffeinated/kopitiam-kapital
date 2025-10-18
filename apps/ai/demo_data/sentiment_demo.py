"""
Pre-computed sentiment data for demo
🚨 WARNING: This is demo data, not real-time
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Pre-computed sentiment scores for 10 popular stocks
DEMO_SENTIMENT_DATA = {
    "NVDA": {
        "symbol": "NVDA",
        "overall_score": 0.82,
        "direction": "bullish",
        "sentiment_breakdown": {
            "news": 0.75,
            "reddit": 0.88,
            "stocktwits": 0.84
        },
        "volume": {
            "news_articles": 45,
            "reddit_mentions": 1823,
            "stocktwits_messages": 542
        },
        "trending": True,
        "contrarian_signal": False,
        "confidence": 0.78,
        "top_sources": [
            {
                "type": "news",
                "title": "NVIDIA Q4 Earnings Beat Expectations, AI Chip Demand Soars",
                "url": "https://example.com/nvda-earnings",
                "sentiment_score": 0.85,
                "published_date": "2025-01-17"
            },
            {
                "type": "reddit",
                "title": "NVDA to the moon! AI revolution is here 🚀",
                "url": "https://reddit.com/r/wallstreetbets/nvda_moon",
                "sentiment_score": 0.92,
                "engagement": 2450
            }
        ]
    },
    
    "TSLA": {
        "symbol": "TSLA",
        "overall_score": 0.68,
        "direction": "bullish",
        "sentiment_breakdown": {
            "news": 0.65,
            "reddit": 0.72,
            "stocktwits": 0.68
        },
        "volume": {
            "news_articles": 38,
            "reddit_mentions": 2156,
            "stocktwits_messages": 892
        },
        "trending": True,
        "contrarian_signal": False,
        "confidence": 0.72,
        "top_sources": []
    },
    
    "AAPL": {
        "symbol": "AAPL",
        "overall_score": 0.58,
        "direction": "neutral",
        "sentiment_breakdown": {
            "news": 0.60,
            "reddit": 0.55,
            "stocktwits": 0.59
        },
        "volume": {
            "news_articles": 52,
            "reddit_mentions": 876,
            "stocktwits_messages": 423
        },
        "trending": False,
        "contrarian_signal": False,
        "confidence": 0.85,
        "top_sources": []
    },
    
    "MSFT": {
        "symbol": "MSFT",
        "overall_score": 0.72,
        "direction": "bullish",
        "sentiment_breakdown": {
            "news": 0.70,
            "reddit": 0.74,
            "stocktwits": 0.73
        },
        "volume": {
            "news_articles": 41,
            "reddit_mentions": 654,
            "stocktwits_messages": 312
        },
        "trending": False,
        "contrarian_signal": False,
        "confidence": 0.88,
        "top_sources": []
    },
    
    "GOOGL": {
        "symbol": "GOOGL",
        "overall_score": 0.62,
        "direction": "bullish",
        "sentiment_breakdown": {
            "news": 0.65,
            "reddit": 0.58,
            "stocktwits": 0.63
        },
        "volume": {
            "news_articles": 35,
            "reddit_mentions": 445,
            "stocktwits_messages": 267
        },
        "trending": False,
        "contrarian_signal": False,
        "confidence": 0.80,
        "top_sources": []
    },
    
    "AMZN": {
        "symbol": "AMZN",
        "overall_score": 0.55,
        "direction": "neutral",
        "sentiment_breakdown": {
            "news": 0.52,
            "reddit": 0.58,
            "stocktwits": 0.56
        },
        "volume": {
            "news_articles": 29,
            "reddit_mentions": 523,
            "stocktwits_messages": 198
        },
        "trending": False,
        "contrarian_signal": False,
        "confidence": 0.82,
        "top_sources": []
    },
    
    "META": {
        "symbol": "META",
        "overall_score": 0.48,
        "direction": "neutral",
        "sentiment_breakdown": {
            "news": 0.45,
            "reddit": 0.51,
            "stocktwits": 0.49
        },
        "volume": {
            "news_articles": 33,
            "reddit_mentions": 712,
            "stocktwits_messages": 334
        },
        "trending": False,
        "contrarian_signal": False,
        "confidence": 0.75,
        "top_sources": []
    },
    
    "AMD": {
        "symbol": "AMD",
        "overall_score": 0.76,
        "direction": "bullish",
        "sentiment_breakdown": {
            "news": 0.72,
            "reddit": 0.81,
            "stocktwits": 0.75
        },
        "volume": {
            "news_articles": 27,
            "reddit_mentions": 1234,
            "stocktwits_messages": 456
        },
        "trending": True,
        "contrarian_signal": False,
        "confidence": 0.80,
        "top_sources": []
    },
    
    "PLTR": {
        "symbol": "PLTR",
        "overall_score": 0.85,
        "direction": "bullish",
        "sentiment_breakdown": {
            "news": 0.78,
            "reddit": 0.92,
            "stocktwits": 0.84
        },
        "volume": {
            "news_articles": 18,
            "reddit_mentions": 3421,
            "stocktwits_messages": 892
        },
        "trending": True,
        "contrarian_signal": False,
        "confidence": 0.68,
        "top_sources": []
    },
    
    "SPY": {
        "symbol": "SPY",
        "overall_score": 0.65,
        "direction": "bullish",
        "sentiment_breakdown": {
            "news": 0.68,
            "reddit": 0.61,
            "stocktwits": 0.66
        },
        "volume": {
            "news_articles": 61,
            "reddit_mentions": 987,
            "stocktwits_messages": 512
        },
        "trending": False,
        "contrarian_signal": False,
        "confidence": 0.90,
        "top_sources": []
    }
}

def get_demo_sentiment(symbol: str) -> dict:
    """
    Get demo sentiment data for a symbol
    
    🚨 WARNING: This returns pre-computed demo data
    
    Args:
        symbol: Stock ticker
    
    Returns:
        Sentiment data dict or None
    """
    if symbol in DEMO_SENTIMENT_DATA:
        logger.warning(f"🚨 DEMO MODE - Returning pre-computed sentiment for {symbol}")
        data = DEMO_SENTIMENT_DATA[symbol].copy()
        data['timestamp'] = datetime.now().isoformat()
        data['demo_mode'] = True
        return data
    
    return None

def list_demo_symbols() -> list:
    """Get list of symbols with demo data"""
    return list(DEMO_SENTIMENT_DATA.keys())

demo_sentiment_data = DEMO_SENTIMENT_DATA

