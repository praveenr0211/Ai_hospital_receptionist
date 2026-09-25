"""The Voice Bridge: Real-time coordination between Exotel AgentStream and Gemini Live.

Connects telephony audio streaming to Gemini Live multimodal reasoning, binds
authoritative Phase 5/4/2 tools, and handles sub-millisecond barge-in interruptions.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

from app.db.session import SessionLocal
from app.models.call import Call
from app.models.enums import CallOutcome
from app.voice.session import VoiceSession, CallStatus, voice_session_store
from app.voice.lifecycle import CallLifecycleManager
from app.voice.audio import AudioProcessor
from app.voice.providers.exotel import exotel_provider, ExotelProvider
from app.voice.gemini_live import GeminiLiveSession, GeminiEvent
from app.voice.transfer import transfer_coordinator

# Import authoritative Phase 5 tools
from app.agent.tools.medical_tools import route_medical_symptoms
from app.agent.tools.doctor_tools import find_doctors_by_specialty
from app.agent.tools.availability_tools import check_doctor_availability, find_alternative_slots
from app.agent.tools.appointment_tools import (
    book_appointment_tool,
    cancel_appointment_tool,
    reschedule_appointment_tool,
)
from app.agent.tools.patient_tools import find_patient_by_phone, create_patient

logger = logging.getLogger("voice.bridge")


class VoiceBridge:
    """Orchestrates bidirectional audio streaming, interruption handling, and tool execution."""

    def __init__(self, websocket: WebSocket, call_id: str) -> None:
        self.websocket = websocket
        self.call_id = call_id
        self.stream_id: Optional[str] = None
        self.session: Optional[VoiceSession] = None
        self.gemini_session: Optional[GeminiLiveSession] = None
        self.media_encoding: str = "audio/x-mulaw"
        self._is_speaking = False
        self._running = False
        self._db_call_id: Optional[int] = None
        self._gemini_task: Optional[asyncio.Task] = None

    async def run(self) -> None:
        """Start the bidirectional voice streaming bridge."""
        self._running = True
        # Retrieve or initialize voice session
        self.session = voice_session_store.get(self.call_id)
        if not self.session:
            self.session = voice_session_store.create(
                call_id=self.call_id,
                phone_number="UNKNOWN"
            )

        # Initialize Gemini Live session in the background so Exotel socket loop starts immediately
        is_mock = True if self.call_id.startswith("test_") else None
        self.gemini_session = GeminiLiveSession(is_mock=is_mock)
        asyncio.create_task(self._init_gemini_and_events())

        try:
            # Process Exotel WebSocket events immediately without blocking on external APIs
            while self._running:
                raw_text = await self.websocket.receive_text()
                event_data = ExotelProvider.parse_event(raw_text)
                await self._handle_exotel_event(event_data)
                if not self._running:
                    break
        except WebSocketDisconnect:
            logger.info("Exotel WebSocket disconnected for call %s", self.call_id)
        except Exception as exc:
            logger.error("Error in VoiceBridge for call %s: %s", self.call_id, exc)
        finally:
            self._running = False
            if self._gemini_task:
                self._gemini_task.cancel()
            await self._cleanup()
            try:
                await self.websocket.close()
            except Exception:
                pass

    async def _init_gemini_and_events(self) -> None:
        """Establish Gemini Live connection and start background event listener."""
        try:
            if self.gemini_session:
                await self.gemini_session.connect()
                self._gemini_task = asyncio.create_task(self._process_gemini_events())
        except Exception as exc:
            logger.error("Failed to connect Gemini Live for call %s: %s", self.call_id, exc)

    # -------------------------------------------------------------
    # Exotel Event Handling (Caller -> Server)
    # -------------------------------------------------------------
    async def _handle_exotel_event(self, event: Dict[str, Any]) -> None:
        event_name = event.get("event")
        if event_name != "media":
            logger.info("Call %s: Received Exotel event '%s'", self.call_id, event_name)

        if event_name == "connected":
            logger.info("Call %s: Exotel connected", self.call_id)
            if self.session and self.session.status == CallStatus.INCOMING:
                CallLifecycleManager.transition(self.session, CallStatus.CONNECTING)

        elif event_name == "start":
            start_data = event.get("start", {})
            self.stream_id = (
                start_data.get("streamSid")
                or start_data.get("stream_sid")
                or event.get("streamSid")
                or event.get("stream_sid")
                or self.stream_id
            )
            caller_phone = (
                start_data.get("from")
                or start_data.get("From")
                or event.get("from")
                or "UNKNOWN"
            )
            incoming_sid = (
                start_data.get("callSid")
                or start_data.get("call_sid")
                or start_data.get("CallSid")
                or event.get("callSid")
                or event.get("call_sid")
            )
            media_format = start_data.get("mediaFormat", {})
            if media_format and "encoding" in media_format:
                self.media_encoding = media_format.get("encoding", "audio/x-mulaw")
            logger.info(
                "Call %s: Stream started for caller %s (stream %s, encoding %s)",
                self.call_id, caller_phone, self.stream_id, self.media_encoding
            )

            if incoming_sid:
                self.call_id = incoming_sid
                self.session = voice_session_store.get(incoming_sid) or voice_session_store.create(
                    call_id=incoming_sid, phone_number=caller_phone
                )

            if self.session:
                self.session.stream_id = self.stream_id
                self.session.phone_number = caller_phone
                CallLifecycleManager.transition(self.session, CallStatus.ACTIVE)

            # Persist call start in PostgreSQL calls table
            self._init_db_call_record(caller_phone)

            # Trigger initial greeting once Gemini Live is connected
            asyncio.create_task(self._trigger_greeting())

        elif event_name == "media":
            # Incoming audio from caller
            if not self.stream_id:
                self.stream_id = event.get("streamSid") or event.get("stream_sid")
            media_data = event.get("media", {})
            payload = media_data.get("payload", "")
            if payload and self.gemini_session:
                raw_bytes = AudioProcessor.decode_base64_payload(payload)
                if raw_bytes:
                    # Transcode 8kHz mu-law from PSTN to 16kHz PCM for Gemini if needed
                    if "mulaw" in self.media_encoding.lower():
                        pcm_bytes = AudioProcessor.mulaw_to_pcm16k(raw_bytes)
                    else:
                        pcm_bytes = raw_bytes

                    await self.gemini_session.send_audio(pcm_bytes)

        elif event_name == "stop":
            logger.info("Call %s: Received stop event from Exotel", self.call_id)
            if self.session and self.session.status not in (CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.HUMAN_TRANSFER):
                CallLifecycleManager.transition(self.session, CallStatus.COMPLETED)
            try:
                with SessionLocal() as db:
                    call_rec = db.query(Call).filter(
                        (Call.provider_call_id == self.call_id) | (Call.session_id == f"voice_{self.call_id}")
                    ).first()
                    if call_rec:
                        now = datetime.now(timezone.utc)
                        call_rec.ended_at = now
                        if call_rec.started_at:
                            call_rec.duration_seconds = int((now - call_rec.started_at).total_seconds())
                        call_rec.call_status = CallStatus.COMPLETED.value
                        db.commit()
            except Exception as exc:
                logger.error("Failed to update call record on stop: %s", exc)
            self._running = False

    async def _trigger_greeting(self) -> None:
        """Wait for Gemini connection and trigger initial spoken greeting."""
        try:
            for _ in range(50):  # Wait up to 2.5 seconds for Gemini Live connection
                if self.gemini_session and self.gemini_session._connected:
                    break
                await asyncio.sleep(0.05)

            if self.gemini_session and self.gemini_session._connected:
                logger.info("Call %s: Triggering initial greeting from Gemini Live...", self.call_id)
                await self.gemini_session.send_text(
                    "The caller has just connected to Apollo Hospital. Greet the caller warmly and ask how you can help them today."
                )
            else:
                logger.warning("Call %s: Gemini Live did not connect in time for greeting.", self.call_id)
        except Exception as exc:
            logger.error("Call %s: Error triggering greeting: %s", self.call_id, exc)

    # -------------------------------------------------------------
    # Gemini Event Handling (Gemini -> Caller)
    # -------------------------------------------------------------
    async def _process_gemini_events(self) -> None:
        """Stream audio frames and tool calls from Gemini Live to Exotel."""
        try:
            if not self.gemini_session:
                return

            async for event in self.gemini_session.receive_events():
                if not self._running:
                    break

                if event.event_type == "audio" and event.audio_pcm:
                    # Wait for stream_id from Exotel 'start' event if not yet received
                    for _ in range(40):
                        if self.stream_id or not self._running:
                            break
                        await asyncio.sleep(0.05)

                    if self.stream_id and self._running:
                        self._is_speaking = True
                        # Transcode 24kHz linear PCM to 8kHz mu-law for telephony if needed
                        if "mulaw" in self.media_encoding.lower():
                            out_audio = AudioProcessor.pcm24k_to_mulaw(event.audio_pcm)
                        else:
                            out_audio = AudioProcessor.pcm24k_to_pcm16k(event.audio_pcm)

                        media_frame = ExotelProvider.create_media_frame(
                            stream_sid=self.stream_id,
                            pcm_bytes=out_audio
                        )
                        await self.websocket.send_text(media_frame)
                        logger.info("Sent audio frame (%d bytes) to Exotel stream %s", len(out_audio), self.stream_id)

                elif event.event_type == "text" and event.text:
                    logger.info("AI Receptionist: %s", event.text)

                elif event.event_type == "interrupted":
                    # Gemini VAD detected caller speaking
                    logger.info("Caller interrupted AI playback. Flushing audio.")
                    await self._interrupt_playback()

                elif event.event_type == "turn_complete":
                    self._is_speaking = False

                elif event.event_type == "tool_call" and event.tool_calls:
                    for call_spec in event.tool_calls:
                        call_id = call_spec.get("id", "call_1")
                        func_name = call_spec.get("name", "")
                        func_args = call_spec.get("args", {})
                        logger.info("Executing Gemini tool %s (call_id=%s)", func_name, call_id)
                        result = await self._dispatch_tool_call(func_name, func_args)
                        await self.gemini_session.send_tool_result(call_id, func_name, result)

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("Error processing Gemini events for call %s: %s", self.call_id, exc)

    # -------------------------------------------------------------
    # Barge-In / Interruption Handler
    # -------------------------------------------------------------
    async def _interrupt_playback(self) -> None:
        """Send Exotel 'clear' frame to instantly flush caller playback buffer."""
        if not self.stream_id:
            return
        self._is_speaking = False
        try:
            clear_frame = ExotelProvider.create_clear_frame(self.stream_id)
            await self.websocket.send_text(clear_frame)
            logger.debug("Sent barge-in clear frame to Exotel stream %s", self.stream_id)
        except Exception as exc:
            logger.warning("Failed to send clear frame: %s", exc)

    # -------------------------------------------------------------
    # Authoritative Tool Dispatching (Phases 5, 4, 2, 1)
    # -------------------------------------------------------------
    async def _dispatch_tool_call(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch Gemini function call to authoritative deterministic systems."""
        with SessionLocal() as db:
            try:
                # 1. Medical Symptom Routing & Clinical Safety (Phase 4)
                if function_name == "route_medical_symptoms":
                    symptoms = args.get("symptoms", "")
                    routing_res = route_medical_symptoms(symptoms)
                    
                    # Update call record with detected specialty
                    if self._db_call_id and routing_res.specialty:
                        call_rec = db.query(Call).filter(Call.id == self._db_call_id).first()
                        if call_rec:
                            call_rec.specialty_detected = routing_res.specialty
                            db.commit()

                    # Critical Emergency Protocol: Halt booking and escalate immediately!
                    if routing_res.emergency_detected or routing_res.escalation_required:
                        logger.warning("EMERGENCY DETECTED during voice call %s: %s", self.call_id, routing_res.reasoning)
                        if self.session:
                            self.session.mark_transferred("Emergency medical condition detected")
                        await transfer_coordinator.transfer_to_human(
                            self.call_id,
                            reason=f"Emergency: {routing_res.reasoning}"
                        )

                    return routing_res.model_dump()

                # 2. Doctor Discovery
                elif function_name == "find_doctors_by_specialty":
                    spec = args.get("specialty", "")
                    doc_res = find_doctors_by_specialty(db=db, specialty=spec)
                    return doc_res.model_dump()

                # 3. Availability Check (Phase 2)
                elif function_name == "check_doctor_availability":
                    doc_id = int(args.get("doctor_id", 1))
                    date_val = args.get("date", "")
                    avail_res = check_doctor_availability(db=db, doctor_id=doc_id, date_val=date_val)
                    return avail_res.model_dump()

                # 4. Book Appointment (Phase 2 Transactional Booking)
                elif function_name == "book_appointment":
                    pat_id = int(args.get("patient_id", 1))
                    doc_id = int(args.get("doctor_id", 1))
                    date_val = args.get("date", "")
                    start_time = args.get("start_time", "")
                    reason = args.get("reason", "Voice appointment")
                    booking_res = book_appointment_tool(
                        db=db,
                        patient_id=pat_id,
                        doctor_id=doc_id,
                        appointment_date=date_val,
                        start_time=start_time,
                        reason=reason
                    )
                    return booking_res.model_dump()

                # 5. Cancel Appointment
                elif function_name == "cancel_appointment":
                    appt_id = int(args.get("appointment_id", 1))
                    reason = args.get("reason", "Cancelled via phone call")
                    cancel_res = cancel_appointment_tool(db=db, appointment_id=appt_id, reason=reason)
                    return cancel_res.model_dump()

                # 6. Reschedule Appointment
                elif function_name == "reschedule_appointment":
                    appt_id = int(args.get("appointment_id", 1))
                    new_date = args.get("new_date", "")
                    new_time = args.get("new_start_time", "")
                    reschedule_res = reschedule_appointment_tool(
                        db=db,
                        appointment_id=appt_id,
                        new_date=new_date,
                        new_start_time=new_time
                    )
                    return reschedule_res.model_dump()

                # 7. Patient Lookup
                elif function_name == "find_patient_by_phone":
                    phone = args.get("phone", "")
                    pat_res = find_patient_by_phone(db=db, phone=phone)
                    return pat_res.model_dump()

                # 8. Human Escalation (Real Telephone Transfer)
                elif function_name == "request_human_escalation":
                    reason = args.get("reason", "Caller requested operator")
                    await transfer_coordinator.transfer_to_human(self.call_id, reason=reason)
                    return {"success": True, "transferred": True, "message": "Call transfer initiated."}

                else:
                    return {"success": False, "error": f"Unknown tool: {function_name}"}

            except Exception as exc:
                logger.error("Error executing tool %s: %s", function_name, exc)
                return {"success": False, "error": str(exc)}

    # -------------------------------------------------------------
    # Database Record Lifecycle
    # -------------------------------------------------------------
    def _init_db_call_record(self, caller_phone: str) -> None:
        """Create call entry in PostgreSQL database."""
        try:
            with SessionLocal() as db:
                call_record = Call(
                    phone_number=caller_phone,
                    provider="exotel",
                    provider_call_id=self.call_id,
                    stream_id=self.stream_id,
                    session_id=f"voice_{self.call_id}",
                    call_status=CallStatus.ACTIVE.value,
                    started_at=datetime.now(timezone.utc),
                    answered_at=datetime.now(timezone.utc),
                    intent="VOICE_CALL",
                    outcome=CallOutcome.APPOINTMENT_BOOKED
                )
                db.add(call_record)
                db.commit()
                db.refresh(call_record)
                self._db_call_id = call_record.id
        except Exception as exc:
            logger.error("Failed to insert call record into database: %s", exc)

    async def _cleanup(self) -> None:
        """Clean up streaming session and persist final call metrics."""
        now = datetime.now(timezone.utc)
        if self.session:
            if self.session.status not in (CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.HUMAN_TRANSFER):
                try:
                    CallLifecycleManager.transition(self.session, CallStatus.COMPLETED)
                except Exception:
                    self.session.mark_completed()

        if self.gemini_session:
            await self.gemini_session.close()

        # Update database with final metrics
        if self._db_call_id:
            try:
                with SessionLocal() as db:
                    call_rec = db.query(Call).filter(Call.id == self._db_call_id).first()
                    if call_rec:
                        call_rec.ended_at = now
                        if call_rec.started_at:
                            call_rec.duration_seconds = int((now - call_rec.started_at).total_seconds())
                        if self.session:
                            call_rec.call_status = self.session.status.value
                        db.commit()
            except Exception as exc:
                logger.error("Failed to update final call record in DB: %s", exc)
