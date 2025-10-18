"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional
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

