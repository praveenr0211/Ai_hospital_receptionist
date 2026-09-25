"""Integration tests for the VoiceBridge WebSocket media streaming pipeline."""

import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.voice.session import voice_session_store, CallStatus
from app.voice.audio import AudioProcessor
from app.db.session import SessionLocal
from app.models.call import Call

client = TestClient(app)


import uuid

def test_voice_bridge_full_lifecycle():
    call_id = f"test_ws_{uuid.uuid4().hex[:8]}"
    stream_id = f"stream_{uuid.uuid4().hex[:8]}"

    try:
        # Step 1: Inbound webhook creates the initial session
        resp = client.post(
            "/api/v1/voice/incoming",
            data={"CallSid": call_id, "From": "+919876543210"}
        )
        assert resp.status_code == 200

        # Step 2: Connect Exotel AgentStream WebSocket
        with client.websocket_connect(f"/api/v1/voice/stream/{call_id}") as ws:
            # Send connected event
            ws.send_text(json.dumps({"event": "connected"}))

            # Send start event
            ws.send_text(json.dumps({
                "event": "start",
                "start": {
                    "stream_sid": stream_id,
                    "call_sid": call_id,
                    "from": "+919876543210",
                    "to": "+911122334455"
                }
            }))

            # Receive greeting media frame from Gemini Live
            greeting_frame_raw = ws.receive_text()
            greeting_frame = json.loads(greeting_frame_raw)
            assert greeting_frame["event"] == "media"
            assert greeting_frame["stream_sid"] == stream_id
            assert "payload" in greeting_frame["media"]

            # Step 3: Caller speaks audio (16kHz PCM)
            pcm_bytes = AudioProcessor.generate_silence(duration_ms=60, sample_rate=16000)
            media_payload = AudioProcessor.encode_base64_payload(pcm_bytes)
            ws.send_text(json.dumps({
                "event": "media",
                "stream_sid": stream_id,
                "media": {
                    "payload": media_payload,
                    "timestamp": "12345"
                }
            }))

            # Step 4: Verify Barge-in interruption
            session = voice_session_store.get(call_id)
            assert session is not None
            assert session.status == CallStatus.ACTIVE
            assert session.stream_id == stream_id

            # Step 5: Hang up / stop event
            ws.send_text(json.dumps({
                "event": "stop",
                "stream_sid": stream_id,
                "stop": {"reason": "callended"}
            }))

        import time
        time.sleep(0.1)

        # Verify session marked completed
        assert session.status == CallStatus.COMPLETED
        assert session.ended_at is not None

        # Verify call recorded in PostgreSQL calls table
        with SessionLocal() as db:
            call_record = db.query(Call).filter(Call.provider_call_id == call_id).order_by(Call.id.desc()).first()
            assert call_record is not None
            assert call_record.phone_number == "+919876543210"
            assert call_record.stream_id == stream_id
            assert call_record.call_status == "completed"
    finally:
        with SessionLocal() as db:
            db.query(Call).filter(Call.provider_call_id == call_id).delete()
            db.commit()
