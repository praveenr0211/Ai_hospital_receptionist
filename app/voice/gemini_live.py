"""Gemini Live async streaming client and tool definitions.

Supports bidirectional PCM audio streaming, live function calling into
Phase 5/4/2 deterministic systems, interruption signals, and speech output.
"""

import asyncio
import logging
from typing import AsyncIterator, Dict, Any, Optional, List
from dataclasses import dataclass

from app.config import settings
from app.voice.audio import AudioProcessor

logger = logging.getLogger("voice.gemini_live")


RECEPTIONIST_SYSTEM_INSTRUCTION = """You are an intelligent, empathetic AI Hospital Receptionist.
Your primary role is to answer patient phone calls, understand their healthcare needs, check doctor schedules, and coordinate appointments.

CRITICAL CLINICAL & OPERATIONAL RULES:
1. YOU ARE NOT A DOCTOR. Never diagnose medical conditions or recommend medications.
2. MEDICAL SAFETY FIRST: When a patient describes symptoms, ALWAYS call `route_medical_symptoms`.
   If the response indicates an emergency (`CALL_911_OR_EMERGENCY` or `escalation_required=true`):
   - STOP normal appointment booking immediately.
   - Advise the caller to seek emergency medical attention or call 108/911.
   - Call `request_human_escalation` to transfer the call immediately.
3. NO HALLUCINATION: Never invent doctors, dates, or time slots. Always query the authoritative availability tool.
4. EXPLICIT CONFIRMATION: Never book an appointment without the caller's explicit confirmation ("Yes", "Confirm", "Please book it").
5. CONCISE SPOKEN RESPONSES: Keep your spoken answers brief, warm, and natural for telephone conversation.
"""

# Gemini Tool declarations matching Phase 5 agent capabilities
GEMINI_FUNCTION_DECLARATIONS = [
    {
        "name": "route_medical_symptoms",
        "description": "Assess patient symptoms, detect potential emergencies, and determine the appropriate medical specialty.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "symptoms": {"type": "STRING", "description": "The symptoms described by the patient."}
            },
            "required": ["symptoms"]
        }
    },
    {
        "name": "find_doctors_by_specialty",
        "description": "Find active doctors for a medical specialty.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "specialty": {"type": "STRING", "description": "Medical specialty name, e.g. Cardiology, Dermatology."}
            },
            "required": ["specialty"]
        }
    },
    {
        "name": "check_doctor_availability",
        "description": "Check open appointment slots for a specific doctor on a given date (YYYY-MM-DD).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "doctor_id": {"type": "INTEGER", "description": "The doctor's unique ID."},
                "date": {"type": "STRING", "description": "Date in YYYY-MM-DD format."}
            },
            "required": ["doctor_id", "date"]
        }
    },
    {
        "name": "book_appointment",
        "description": "Book a confirmed appointment slot for a registered patient.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "patient_id": {"type": "INTEGER", "description": "Registered patient ID."},
                "doctor_id": {"type": "INTEGER", "description": "Doctor ID."},
                "date": {"type": "STRING", "description": "Date in YYYY-MM-DD format."},
                "start_time": {"type": "STRING", "description": "Start time in HH:MM format."},
                "reason": {"type": "STRING", "description": "Reason for visit or symptoms."}
            },
            "required": ["patient_id", "doctor_id", "date", "start_time"]
        }
    },
    {
        "name": "cancel_appointment",
        "description": "Cancel an existing appointment.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "appointment_id": {"type": "INTEGER", "description": "Appointment ID to cancel."},
                "reason": {"type": "STRING", "description": "Reason for cancellation."}
            },
            "required": ["appointment_id"]
        }
    },
    {
        "name": "reschedule_appointment",
        "description": "Reschedule an existing appointment to a new date and time.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "appointment_id": {"type": "INTEGER", "description": "Existing appointment ID."},
                "new_date": {"type": "STRING", "description": "Target date in YYYY-MM-DD format."},
                "new_start_time": {"type": "STRING", "description": "Target start time in HH:MM format."}
            },
            "required": ["appointment_id", "new_date", "new_start_time"]
        }
    },
    {
        "name": "find_patient_by_phone",
        "description": "Look up an existing patient record by telephone number.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "phone": {"type": "STRING", "description": "Phone number with or without country code."}
            },
            "required": ["phone"]
        }
    },
    {
        "name": "request_human_escalation",
        "description": "Transfer the phone call to a human receptionist or medical operator.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "reason": {"type": "STRING", "description": "Reason for escalating to human operator."}
            },
            "required": ["reason"]
        }
    }
]


@dataclass
class GeminiEvent:
    """Event emitted by Gemini Live connection."""
    event_type: str  # "audio", "text", "tool_call", "interrupted", "turn_complete"
    audio_pcm: Optional[bytes] = None
    text: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class GeminiLiveSession:
    """Manages persistent asynchronous Gemini Live streaming session."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, is_mock: Optional[bool] = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_LIVE_MODEL
        self._connected = False
        self._client = None
        self._live_session = None
        self._is_mock = is_mock if is_mock is not None else not bool(self.api_key)
        self._mock_queue: asyncio.Queue[GeminiEvent] = asyncio.Queue()

    async def connect(self) -> None:
        """Establish async Gemini Live connection."""
        if not self._is_mock:
            try:
                from google import genai
                from google.genai import types

                self._client = genai.Client(api_key=self.api_key, http_options={"api_version": "v1alpha"})
                model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
                
                config = types.LiveConnectConfig(
                    response_modalities=["AUDIO"],
                    system_instruction=types.Content(parts=[types.Part(text=RECEPTIONIST_SYSTEM_INSTRUCTION)]),
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                        )
                    ),
                    tools=[{"function_declarations": GEMINI_FUNCTION_DECLARATIONS}]
                )
                self._live_context = self._client.aio.live.connect(
                    model=model_name,
                    config=config
                )
                self._live_session = await self._live_context.__aenter__()
                self._connected = True
                logger.info("Connected to live Gemini Live API with model %s", model_name)
                return
            except Exception as exc:
                logger.warning("Failed to connect to real Gemini Live API (%s). Falling back to mock live session.", exc)
                self._is_mock = True

        self._connected = True
        logger.info("Initialized mock Gemini Live session for local testing.")
        
        # Enqueue initial greeting for mock mode
        greeting_audio = AudioProcessor.generate_silence(duration_ms=400, sample_rate=24000)
        self._mock_queue.put_nowait(
            GeminiEvent(event_type="text", text="Hello, you have reached City Hospital appointment desk. How may I help you today?")
        )
        self._mock_queue.put_nowait(
            GeminiEvent(event_type="audio", audio_pcm=greeting_audio)
        )
        self._mock_queue.put_nowait(
            GeminiEvent(event_type="turn_complete")
        )

    async def send_audio(self, pcm_bytes: bytes) -> None:
        """Send 16kHz PCM audio chunk to Gemini."""
        if not self._connected:
            return

        if not self._is_mock and self._live_session:
            from google.genai import types
            await self._live_session.send(
                input=types.LiveClientRealtimeInput(
                    media_chunks=[types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")]
                )
            )

    async def send_tool_result(self, call_id: str, function_name: str, response: Dict[str, Any]) -> None:
        """Send tool execution response back to Gemini Live."""
        if not self._connected:
            return

        if not self._is_mock and self._live_session:
            from google.genai import types
            await self._live_session.send(
                input=types.LiveClientToolResponse(
                    function_responses=[
                        types.FunctionResponse(
                            name=function_name,
                            id=call_id,
                            response=response
                        )
                    ]
                )
            )

    async def receive_events(self) -> AsyncIterator[GeminiEvent]:
        """Stream events (audio output, tool calls, transcripts) from Gemini Live."""
        if not self._connected:
            return

        if not self._is_mock and self._live_session:
            async for response in self._live_session.receive():
                server_content = getattr(response, "server_content", None)
                if server_content:
                    model_turn = getattr(server_content, "model_turn", None)
                    if model_turn:
                        for part in getattr(model_turn, "parts", []):
                            # Audio chunk (24kHz PCM)
                            inline_data = getattr(part, "inline_data", None)
                            if inline_data and getattr(inline_data, "data", None):
                                yield GeminiEvent(event_type="audio", audio_pcm=inline_data.data)

                            # Text transcript
                            text = getattr(part, "text", None)
                            if text:
                                yield GeminiEvent(event_type="text", text=text)

                    # Interruption detection
                    if getattr(server_content, "interrupted", False):
                        yield GeminiEvent(event_type="interrupted")

                    if getattr(server_content, "turn_complete", False):
                        yield GeminiEvent(event_type="turn_complete")

                # Function / Tool call
                tool_call = getattr(response, "tool_call", None)
                if tool_call:
                    function_calls = getattr(tool_call, "function_calls", [])
                    calls = []
                    for fc in function_calls:
                        calls.append({
                            "id": getattr(fc, "id", "call_1"),
                            "name": getattr(fc, "name", ""),
                            "args": getattr(fc, "args", {})
                        })
                    if calls:
                        yield GeminiEvent(event_type="tool_call", tool_calls=calls)
            return

        # Mock Mode Event Loop: yields events from the mock queue
        while self._connected:
            try:
                event = await asyncio.wait_for(self._mock_queue.get(), timeout=0.2)
                yield event
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def close(self) -> None:
        """Close Gemini Live streaming session."""
        self._connected = False
        if hasattr(self, "_live_context") and self._live_context:
            try:
                await self._live_context.__aexit__(None, None, None)
            except Exception:
                pass
        self._live_session = None
        self._live_context = None
