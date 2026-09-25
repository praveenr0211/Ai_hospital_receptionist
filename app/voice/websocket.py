"""WebSocket media streaming router handler."""

import logging
from fastapi import WebSocket
from app.voice.bridge import VoiceBridge

logger = logging.getLogger("voice.websocket")


async def handle_voice_stream(websocket: WebSocket, call_id: str) -> None:
    """Accept and handle real-time bidirectional WebSocket audio stream from Exotel."""
    await websocket.accept()
    logger.info("Accepted WebSocket connection for call %s", call_id)

    bridge = VoiceBridge(websocket=websocket, call_id=call_id)
    await bridge.run()
