"""Sentiment analysis modules"""
from .aggregator import sentiment_aggregator, SentimentAggregator
from .news_sentiment import news_sentiment_analyzer, NewsSentimentAnalyzer
from .social_scraper import social_sentiment_analyzer, SocialSentimentAnalyzer

__all__ = [
    "sentiment_aggregator",
    "SentimentAggregator",
    "news_sentiment_analyzer",
    "NewsSentimentAnalyzer",
    "social_sentiment_analyzer",
    "SocialSentimentAnalyzer"
]

