"""ElevenLabs text-to-speech client"""

class ElevenLabsClient:
    """Client for ElevenLabs voice synthesis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def synthesize(self, text: str, voice_id: str = "default"):
        """Synthesize text to speech"""
        # TODO: Implement ElevenLabs TTS
        pass
    
    async def get_voices(self):
        """Get available voices"""
        # TODO: Fetch available voices
        pass

