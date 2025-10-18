"""Pydantic schemas for API requests and responses"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum

# ============================================================================
# ROUTER SCHEMAS
# ============================================================================

class IntentType(str, Enum):
    """Intent classification types"""
    RESEARCH = "RESEARCH"          # Market research, news, analysis
    RECOMMEND = "RECOMMEND"        # Generate trading recommendation
    PORTFOLIO = "PORTFOLIO"        # View/manage portfolio
    ALERTS = "ALERTS"              # Check alerts, set up monitoring
    EXPLAIN = "EXPLAIN"            # Educational explanations
    SETTINGS = "SETTINGS"          # User preferences, configuration

class UrgencyLevel(str, Enum):
    """Urgency classification"""
    LOW = "low"          # General inquiry, no time pressure
    MEDIUM = "medium"    # Standard trading question
    HIGH = "high"        # Time-sensitive, market-moving event

class RouterRequest(BaseModel):
    """Router request schema"""
    query: str = Field(..., min_length=1, max_length=500, description="User query text")
    user_id: Optional[str] = Field(None, description="Optional user ID for context")

class RouterResponse(BaseModel):
    """Router classification response"""
    intent: IntentType = Field(..., description="Classified intent")
    entities: List[str] = Field(default_factory=list, description="Extracted entities (tickers, sectors, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM, description="Query urgency level")
    reasoning: Optional[str] = Field(None, description="Brief explanation of classification")
    
    @field_validator('entities')
    @classmethod
    def clean_entities(cls, v: List[str]) -> List[str]:
        """Clean and deduplicate entities"""
        # Remove duplicates, strip whitespace, uppercase tickers
        cleaned = []
        seen = set()
        for entity in v:
            entity = entity.strip().upper()
            if entity and entity not in seen:
                cleaned.append(entity)
                seen.add(entity)
        return cleaned

# ============================================================================
# TRADING SCHEMAS
# ============================================================================

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

class BriefRequest(BaseModel):
    """Request schema for market briefs"""
    watchlist: List[str] = Field(..., min_length=1, max_length=20, description="List of symbols to analyze")
    market: str = Field(..., description="Market name (US, SGX, LSE, etc)")
    user_id: str
    include_voice: bool = True

class BriefResponse(BaseModel):
    """Response schema for market briefs"""
    type: str  # "morning" or "eod"
    text: str
    audio_base64: Optional[str] = None
    symbols_analyzed: List[str]
    sentiment_summary: Optional[dict] = None
    performance_summary: Optional[dict] = None
    generated_at: str

