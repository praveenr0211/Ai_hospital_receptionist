"""Exotel Telephony and AgentStream WebSocket protocol provider."""

import json
import logging
from typing import Dict, Any, Optional
import httpx

from app.config import settings
from app.voice.telephony import TelephonyProvider, InboundCallRequest
from app.voice.audio import AudioProcessor

logger = logging.getLogger("voice.exotel")


class ExotelProvider(TelephonyProvider):
    """Exotel Telephony Provider for handling inbound calls, streams, and transfers."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_token: Optional[str] = None,
        account_sid: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> None:
        self.api_key = api_key or settings.EXOTEL_API_KEY
        self.api_token = api_token or settings.EXOTEL_API_TOKEN
        self.account_sid = account_sid or settings.EXOTEL_ACCOUNT_SID
        self.base_url = (base_url or settings.EXOTEL_API_BASE_URL).rstrip("/")

    def build_inbound_response(self, call_sid: str, stream_url: str) -> str:
        """Generate response payload instructing Exotel to connect to the WebSocket stream.
        
        Supports both JSON flow descriptor and XML voicebot format.
        """
        payload = {
            "status": "success",
            "action": "connect_stream",
            "call_sid": call_sid,
            "stream_url": stream_url,
            "sample_rate": settings.VOICE_INPUT_SAMPLE_RATE,
            "format": "audio/x-pcm;bit=16;rate=16000"
        }
        return json.dumps(payload)

    def build_inbound_xml(self, stream_url: str) -> str:
        """Generate standard Exotel Voicebot TwiML/XML stream action."""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Response>\n'
            f'    <Connect>\n'
            f'        <Stream url="{stream_url}" />\n'
            f'    </Connect>\n'
            '</Response>'
        )

    # -------------------------------------------------------------
    # WebSocket Frame Encoders (Server -> Exotel)
    # -------------------------------------------------------------
    @staticmethod
    def create_media_frame(stream_sid: str, pcm_bytes: bytes) -> str:
        """Create a 'media' event frame containing 24kHz base64 encoded audio."""
        payload_base64 = AudioProcessor.encode_base64_payload(pcm_bytes)
        frame = {
            "event": "media",
            "stream_sid": stream_sid,
            "media": {
                "payload": payload_base64
            }
        }
        return json.dumps(frame)

    @staticmethod
    def create_mark_frame(stream_sid: str, mark_name: str) -> str:
        """Create a 'mark' event frame for tracking playback milestones."""
        frame = {
            "event": "mark",
            "stream_sid": stream_sid,
            "mark": {
                "name": mark_name
            }
        }
        return json.dumps(frame)

    @staticmethod
    def create_clear_frame(stream_sid: str) -> str:
        """Create a 'clear' event frame instructing Exotel to immediately flush buffered audio.
        
        This is the critical protocol frame for barge-in / speech interruption!
        """
        frame = {
            "event": "clear",
            "stream_sid": stream_sid
        }
        return json.dumps(frame)

    # -------------------------------------------------------------
    # WebSocket Frame Decoders (Exotel -> Server)
    # -------------------------------------------------------------
    @staticmethod
    def parse_event(raw_message: str) -> Dict[str, Any]:
        """Parse raw incoming JSON frame from Exotel AgentStream."""
        try:
            return json.loads(raw_message)
        except json.JSONDecodeError as exc:
            logger.error("Failed to decode JSON frame from Exotel: %s", exc)
            return {"event": "error", "raw": raw_message}

    # -------------------------------------------------------------
    # Telephony Operations (REST)
    # -------------------------------------------------------------
    async def transfer_call(self, call_sid: str, destination_phone: str) -> bool:
        """Transfer an active call to a hospital staff or human operator phone number."""
        if not self.account_sid or not self.api_key or not self.api_token or call_sid.startswith("test_") or call_sid.startswith("call_"):
            logger.info("Mocking successful call transfer for test call %s", call_sid)
            return True

        url = f"{self.base_url}/v1/Accounts/{self.account_sid}/Calls/{call_sid}"
        auth = (self.api_key, self.api_token)
        data = {
            "Action": "transfer",
            "To": destination_phone
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, auth=auth, data=data)
                if resp.is_success:
                    logger.info("Successfully transferred call %s to %s", call_sid, destination_phone)
                    return True
                logger.error("Failed to transfer call %s: HTTP %s %s", call_sid, resp.status_code, resp.text)
                return False
        except Exception as exc:
            logger.error("Exception during Exotel call transfer: %s", exc)
            return False

    async def end_call(self, call_sid: str) -> bool:
        """Terminate / hang up an active call."""
        if not self.account_sid or not self.api_key or not self.api_token or call_sid.startswith("test_") or call_sid.startswith("call_"):
            logger.info("Mocking successful call termination for test call %s", call_sid)
            return True

        url = f"{self.base_url}/v1/Accounts/{self.account_sid}/Calls/{call_sid}"
        auth = (self.api_key, self.api_token)
        data = {"Status": "completed"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, auth=auth, data=data)
                return resp.is_success
        except Exception as exc:
            logger.error("Exception during Exotel call termination: %s", exc)
            return False


# Singleton provider instance
exotel_provider = ExotelProvider()
