"""
ElevenLabs Voice Narrator for Market Briefs
Converts text briefs to natural speech
"""
import logging
import base64
from typing import Optional
import httpx

# Flexible imports
try:
    from ..utils.config import settings
    from ..utils.cost_tracker import cost_tracker
    from ..utils.http_client import http_client_manager
except ImportError:
    from utils.config import settings
    from utils.cost_tracker import cost_tracker
    from utils.http_client import http_client_manager

logger = logging.getLogger(__name__)

class BriefNarrator:
    """
    ElevenLabs voice narration for market briefs
    
    Features:
    - Natural voice synthesis
    - Streaming for faster response
    - Cost tracking
    - Graceful fallback if voice fails
    """
    
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.voice_id = getattr(settings, 'kopi_colt_voice_id', None)
        self.base_url = "https://api.elevenlabs.io/v1"
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            logger.info("Initialized ElevenLabs voice narrator")
        else:
            logger.warning("ElevenLabs not configured - voice disabled")
    
    async def generate_voice(
        self,
        text: str,
        voice_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Generate voice narration from text
        
        Args:
            text: Text to narrate
            voice_id: ElevenLabs voice ID (uses default if None)
            user_id: User ID for cost tracking
        
        Returns:
            Audio bytes (MP3) or None if failed
        """
        if not self.enabled:
            logger.debug("ElevenLabs disabled - no voice generated")
            return None
        
        try:
            # Use provided voice or default
            vid = voice_id or self.voice_id
            
            if not vid:
                logger.warning("No voice ID configured")
                return None
            
            # ElevenLabs TTS endpoint
            url = f"{self.base_url}/text-to-speech/{vid}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",  # Fast, high quality
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            # Use shared HTTP client for connection pooling
            client = await http_client_manager.get_client()
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                audio_bytes = response.content
                
                # Track cost (~$0.30 per 1K characters)
                char_count = len(text)
                estimated_cost = (char_count / 1000) * 0.30
                
                if user_id:
                    await cost_tracker.log_cost(
                        user_id=user_id,
                        service="elevenlabs-tts",
                        tokens_input=0,
                        tokens_output=char_count,
                        metadata={"voice_id": vid, "chars": char_count, "estimated_cost": estimated_cost}
                    )
                
                logger.info(f"Generated voice narration: {char_count} chars, ~${estimated_cost:.2f}")
                return audio_bytes
            
            else:
                logger.error(f"ElevenLabs error {response.status_code}: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Voice generation failed: {e}")
            return None
    
    def encode_audio(self, audio_bytes: bytes) -> str:
        """Encode audio bytes to base64 for JSON response"""
        return base64.b64encode(audio_bytes).decode('utf-8')

# Global instance
brief_narrator = BriefNarrator()

