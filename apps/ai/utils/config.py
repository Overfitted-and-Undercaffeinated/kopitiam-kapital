"""Enhanced configuration management with feature flags"""
from pydantic_settings import BaseSettings
from typing import Optional, Literal
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    anthropic_api_key: str
    openai_api_key: str
    groq_api_key: str
    exa_api_key: str
    mem0_api_key: str
    elevenlabs_api_key: str
    alpha_vantage_api_key: Optional[str] = None
    rapidapi_key: Optional[str] = None  # For StockTwits via RapidAPI
    
    # Reddit API (PRAW)
    client_id: Optional[str] = None  # Reddit client ID
    client_secret: Optional[str] = None  # Reddit client secret
    user_agent: str = "KopitiamCapital/1.0"  # Reddit user agent
    
    # Supabase
    supabase_url: str
    supabase_service_key: str
    supabase_anon_key: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    jwt_secret: str
    
    # Environment
    python_env: str = "development"
    node_env: str = "development"
    
    # FEATURE FLAGS
    # Market Data Provider: "yfinance" (free, testing) or "alphavantage" (paid, demo)
    market_data_provider: Literal["yfinance", "alphavantage"] = "yfinance"
    
    # Testing Modes
    enable_api_calls: bool = True  # Set to False for testing without API calls
    use_mock_llm: bool = False  # Use mock LLM responses for testing
    use_mock_market_data: bool = True  # Use mock market data
    use_mock_exa: bool = False  # Use REAL Exa.ai API (was mocked before)
    stocktwits_enabled: bool = False  # StockTwits disabled (removed from sentiment analysis)
    
    # Advanced Features
    use_mem0: bool = True  # Use Mem0 for user memory and personalization
    use_mcp_risk_tools: bool = True  # Use MCP server for advanced risk calculations
    
    # Rate Limiting
    enable_rate_limiting: bool = False  # Disabled for development (Redis optional)
    exa_calls_per_hour: int = 500
    openai_calls_per_hour: int = 1000
    groq_calls_per_hour: int = 2000
    
    # Cost Tracking
    enable_cost_tracking: bool = True
    cost_alert_threshold_usd: float = 100.0  # Alert when user exceeds this
    
    # Cache TTL (seconds)
    cache_ttl_news: int = 3600 * 4  # 4 hours
    cache_ttl_filing: int = 3600 * 24 * 30  # 30 days
    cache_ttl_research: int = 3600 * 24 * 7  # 7 days
    
    # Market Hours
    enable_market_hours_check: bool = True
    monitor_only_during_market_hours: bool = True
    
    # Model Versioning
    router_version: str = "v1.0"
    recommendation_version: str = "v1.0"
    summarizer_version: str = "v1.0"
    
    # Compliance
    enable_disclaimers: bool = True
    
    # Multi-language (Note: UI translation is frontend engineer's scope)
    enable_auto_translate: bool = False  # Backend translation only
    
    class Config:
        # Try to load from project root .env first
        env_file = str(Path(__file__).parent.parent.parent.parent / ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env

# Singleton instance
_settings = None

def get_settings() -> Settings:
    """Get or create settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# For backward compatibility
settings = get_settings()

# Cost pricing (USD per unit)
COST_PRICING = {
    'gpt-4o': 0.00500,  # per 1K input tokens
    'gpt-4o-output': 0.01500,  # per 1K output tokens
    'gpt-4o-mini': 0.00015,  # per 1K input tokens
    'gpt-4o-mini-output': 0.00060,  # per 1K output tokens
    'claude-sonnet-4.5': 0.00300,  # per 1K input tokens
    'claude-sonnet-4.5-output': 0.01500,  # per 1K output tokens
    'groq-llama-3.3-70b': 0.00000,  # Free tier
    'exa-search': 0.01000,  # per search (estimate)
    'elevenlabs-tts': 0.00030,  # per character
}

