"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional

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
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    jwt_secret: str
    
    # Environment
    python_env: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

