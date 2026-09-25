"""Voice and Telephony REST & WebSocket API endpoints."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import (
    APIRouter,
    Request,
    Response,
    WebSocket,
    HTTPException,
    status,
    Depends
)
from pydantic import BaseModel, Field

from app.config import settings
from app.db.session import SessionLocal
from app.models.call import Call
from app.models.enums import CallOutcome
from app.voice.session import voice_session_store, CallStatus, VoiceSession
from app.voice.lifecycle import CallLifecycleManager
from app.voice.providers.exotel import exotel_provider
from app.voice.websocket import handle_voice_stream
from app.voice.transfer import transfer_coordinator
from app.voice.security import verify_telephony_webhook

logger = logging.getLogger("api.voice")

router = APIRouter(prefix="/voice", tags=["Voice & Telephony"])


class InboundWebhookPayload(BaseModel):
    """Payload sent by Exotel inbound call webhook."""
    CallSid: Optional[str] = Field(None, description="Exotel Call SID")
    From: Optional[str] = Field(None, description="Caller's phone number")
    To: Optional[str] = Field(None, description="ExoPhone number called")
    CallType: Optional[str] = Field("inbound", description="Direction/type of call")


class CallStatusPayload(BaseModel):
    """Payload sent by Exotel call status callbacks."""
    CallSid: str
    Status: str
    RecordingUrl: Optional[str] = None
    Duration: Optional[int] = None


class TransferRequest(BaseModel):
    """Payload to request manual call transfer."""
    reason: str = Field(default="Escalated by supervisor", description="Transfer reason")
    destination_phone: Optional[str] = Field(None, description="Target phone number")


@router.post("/incoming", summary="Handle incoming telephony webhook from Exotel")
async def handle_incoming_call(
    request: Request,
    _auth: bool = Depends(verify_telephony_webhook)
) -> Response:
    """Receive incoming call webhook from Exotel and respond with stream instructions."""
    # Exotel may send Form Data (x-www-form-urlencoded) or JSON
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

    call_sid = data.get("CallSid") or data.get("call_sid") or f"exotel_{int(datetime.now().timestamp())}"
    caller_phone = data.get("From") or data.get("from") or "UNKNOWN"

    logger.info("Incoming telephony call: CallSid=%s, From=%s", call_sid, caller_phone)

    # Register voice session
    session = voice_session_store.get(call_sid)
    if not session:
        session = voice_session_store.create(call_id=call_sid, phone_number=caller_phone)

    # Determine WebSocket stream URL
    base_ws_url = settings.VOICE_WS_URL.rstrip("/")
    stream_url = f"{base_ws_url}/{call_sid}"

    # Return Exotel XML or JSON based on Accept header
    accept = request.headers.get("accept", "")
    if "application/xml" in accept or "text/xml" in accept:
        xml_content = exotel_provider.build_inbound_xml(stream_url)
        return Response(content=xml_content, media_type="application/xml")

    json_response = exotel_provider.build_inbound_response(call_sid=call_sid, stream_url=stream_url)
    return Response(content=json_response, media_type="application/json")


@router.websocket("/stream")
@router.websocket("/stream/{call_id}")
async def voice_media_stream(websocket: WebSocket, call_id: Optional[str] = None) -> None:
    """Bidirectional WebSocket audio streaming bridge with Exotel AgentStream."""
    actual_call_id = call_id or websocket.query_params.get("CallSid") or f"exotel_{int(datetime.now().timestamp())}"
    await handle_voice_stream(websocket, actual_call_id)


@router.post("/status", summary="Exotel call status lifecycle callback")
async def handle_call_status(
    payload: CallStatusPayload,
    _auth: bool = Depends(verify_telephony_webhook)
) -> Dict[str, Any]:
    """Track call status updates (ringing, answered, completed, failed)."""
    call_sid = payload.CallSid
    exotel_status = payload.Status.lower()
    logger.info("Call status update: %s -> %s", call_sid, exotel_status)

    session = voice_session_store.get(call_sid)
    if session:
        if exotel_status in ("completed", "terminal"):
            session.mark_completed()
        elif exotel_status in ("failed", "busy", "no-answer"):
            session.mark_failed(f"Telephony status: {exotel_status}")

    # Update database record
    with SessionLocal() as db:
        call_record = db.query(Call).filter(
            (Call.provider_call_id == call_sid) | (Call.session_id == f"voice_{call_sid}")
        ).first()
        if call_record:
            call_record.call_status = exotel_status
            if payload.RecordingUrl:
                call_record.recording_url = payload.RecordingUrl
            if payload.Duration:
                call_record.duration_seconds = payload.Duration
            if exotel_status in ("completed", "terminal") and not call_record.ended_at:
                call_record.ended_at = datetime.now(timezone.utc)
            db.commit()

    return {"status": "ok", "call_sid": call_sid, "updated_status": exotel_status}


@router.get("/{call_id}", summary="Get real-time call session state")
def get_call_session(call_id: str) -> Dict[str, Any]:
    """Retrieve the current state of a voice call session."""
    session = voice_session_store.get(call_id)
    if not session:
        # Check database
        with SessionLocal() as db:
            call_record = db.query(Call).filter(
                (Call.provider_call_id == call_id) | (Call.id == int(call_id) if call_id.isdigit() else False)
            ).first()
            if not call_record:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")
            return {
                "call_id": call_record.provider_call_id or str(call_record.id),
                "phone_number": call_record.phone_number,
                "agent_session_id": call_record.session_id,
                "status": call_record.call_status or "completed",
                "duration_seconds": call_record.duration_seconds,
                "started_at": call_record.started_at,
                "ended_at": call_record.ended_at,
                "transferred": call_record.transfer_requested,
                "transfer_reason": call_record.transfer_reason
            }

    return session.model_dump()


@router.post("/{call_id}/transfer", summary="Transfer active call to human operator")
async def transfer_call(call_id: str, payload: TransferRequest) -> Dict[str, Any]:
    """Trigger an immediate phone transfer of an active call to a human operator."""
    success = await transfer_coordinator.transfer_to_human(
        call_id=call_id,
        reason=payload.reason,
        destination_phone=payload.destination_phone
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate call transfer with telephony provider"
        )
    return {"status": "transferred", "call_id": call_id, "reason": payload.reason}


@router.post("/{call_id}/end", summary="Terminate / hang up an active call")
async def end_call(call_id: str) -> Dict[str, Any]:
    """Terminate an ongoing phone call."""
    session = voice_session_store.get(call_id)
    if session:
        session.mark_completed()

    success = await exotel_provider.end_call(call_id)
    return {"status": "terminated", "call_id": call_id, "success": success}
