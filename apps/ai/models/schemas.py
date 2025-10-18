"""Pydantic schemas for API requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Source(BaseModel):
    """Source citation"""
    title: str
    url: str
    published: Optional[str] = None

class RecommendationRequest(BaseModel):
    """Request for generating a recommendation"""
    user_id: str
    symbol: Optional[str] = None

class RecommendationResponse(BaseModel):
    """Trading recommendation response"""
    action: str = Field(..., description="BUY, SELL, or HOLD")
    symbol: str
    entry: float
    stop: float
    target: float
    size_pct_nav: float
    thesis: str
    risks: str
    confidence: float
    sources: List[Source]
    timestamp: datetime

class MorningBriefRequest(BaseModel):
    """Request for morning brief"""
    user_id: str

class MorningBriefResponse(BaseModel):
    """Morning brief response"""
    summary: str
    market_overview: str
    portfolio_status: dict
    recommendations: List[RecommendationResponse]
    audio_url: Optional[str] = None
    timestamp: datetime

