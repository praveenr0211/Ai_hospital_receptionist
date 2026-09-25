"""Gemini provider wrapper for voice integration."""

from typing import Optional
from app.config import settings
from app.voice.gemini_live import GeminiLiveSession


class GeminiProvider:
    """Factory for creating and managing Gemini Live sessions."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_LIVE_MODEL

    def create_session(self) -> GeminiLiveSession:
        """Create a new unstarted Gemini Live session."""
        return GeminiLiveSession(api_key=self.api_key, model=self.model)


gemini_provider = GeminiProvider()
