"""API client initialization and management"""
from openai import OpenAI, AsyncOpenAI
from anthropic import Anthropic
import logging
from .config import get_settings

logger = logging.getLogger(__name__)

class APIClients:
    """Centralized API client management"""
    
    _groq_client = None
    _openai_client = None
    _anthropic_client = None
    
    @classmethod
    def get_groq(cls) -> OpenAI:
        """
        Get or create Groq client using OpenAI SDK.
        
        Groq is OpenAI-compatible, so we use OpenAI's SDK with custom base_url.
        See: https://console.groq.com/docs/overview
        """
        if cls._groq_client is None:
            settings = get_settings()
            cls._groq_client = OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            logger.info("Initialized Groq client (OpenAI-compatible)")
        return cls._groq_client
    
    @classmethod
    def get_openai(cls) -> AsyncOpenAI:
        """Get or create OpenAI async client"""
        if cls._openai_client is None:
            settings = get_settings()
            cls._openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("Initialized OpenAI client")
        return cls._openai_client
    
    @classmethod
    def get_anthropic(cls) -> Anthropic:
        """Get or create Anthropic client"""
        if cls._anthropic_client is None:
            settings = get_settings()
            cls._anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
            logger.info("Initialized Anthropic client")
        return cls._anthropic_client

# Convenience functions
def get_groq_client() -> OpenAI:
    """Get Groq client instance (OpenAI-compatible)"""
    return APIClients.get_groq()

def get_openai_client() -> AsyncOpenAI:
    """Get OpenAI client instance"""
    return APIClients.get_openai()

def get_anthropic_client() -> Anthropic:
    """Get Anthropic client instance"""
    return APIClients.get_anthropic()

