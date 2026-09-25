"""Telephony interface and abstract provider definitions."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class InboundCallRequest(BaseModel):
    """Normalized payload representing an incoming phone call."""
    call_sid: str
    from_phone: str
    to_phone: str
    stream_url: Optional[str] = None
    extra_params: Dict[str, Any] = {}


class TelephonyProvider(ABC):
    """Abstract base class for telephony providers (e.g. Exotel, Mock)."""

    @abstractmethod
    def build_inbound_response(self, call_sid: str, stream_url: str) -> str:
        """Construct the response (e.g. Exotel Flow/Voicebot XML or JSON) to establish WebSocket streaming."""
        pass

    @abstractmethod
    async def transfer_call(self, call_sid: str, destination_phone: str) -> bool:
        """Initiate transfer of an active call to a human operator."""
        pass

    @abstractmethod
    async def end_call(self, call_sid: str) -> bool:
        """Explicitly hang up or terminate an active call."""
        pass
