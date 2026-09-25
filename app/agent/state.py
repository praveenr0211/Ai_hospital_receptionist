from datetime import date, time
from typing import Any
from pydantic import BaseModel, Field
from app.schemas.agent import ConversationState, IntentType

class ConversationMessage(BaseModel):
    role: str # "user" | "assistant" | "system"
    content: str

class ReceptionistState(BaseModel):
    session_id: str

    # Conversation tracking
    current_state: ConversationState = "GREETING"
    previous_state: ConversationState | None = None

    # Patient details
    patient_id: int | None = None
    patient_name: str | None = None
    patient_phone: str | None = None

    # Intent
    intent: IntentType | None = None
    intent_confidence: str | None = None

    # Medical & routing
    symptom_text: str | None = None
    normalized_symptoms: list[str] = Field(default_factory=list)
    specialty: str | None = None
    routing_confidence: str | None = None
    emergency_detected: bool = False
    escalation_required: bool = False
    escalation_reason: str | None = None
    clarification_required: bool = False
    clarification_cue: str | None = None

    # Doctor selection & availability
    doctor_id: int | None = None
    doctor_name: str | None = None
    candidate_doctors: list[dict[str, Any]] = Field(default_factory=list)
    appointment_date: str | None = None # "YYYY-MM-DD"
    requested_time: str | None = None # "HH:MM"
    available_slots: list[dict[str, str]] = Field(default_factory=list)
    selected_slot: dict[str, str] | None = None

    # Appointment lifecycle & safety gate
    appointment_id: int | None = None
    existing_appointment_id: int | None = None # For cancellation/reschedule target
    awaiting_confirmation: bool = False
    confirmation_intent: str | None = None # e.g. "BOOKING", "CANCELLATION", "RESCHEDULE"

    # Memory and audit
    conversation_history: list[ConversationMessage] = Field(default_factory=list)
    last_tool_called: str | None = None
    last_tool_result: dict[str, Any] | None = None
    error_message: str | None = None

    def add_message(self, role: str, content: str) -> None:
        self.conversation_history.append(ConversationMessage(role=role, content=content))


class SessionStore:
    """Thread-safe in-memory session store with interface for Redis/external stores."""
    def __init__(self) -> None:
        self._store: dict[str, ReceptionistState] = {}

    def get_or_create(self, session_id: str, phone_number: str | None = None) -> ReceptionistState:
        if session_id not in self._store:
            state = ReceptionistState(session_id=session_id)
            if phone_number:
                state.patient_phone = phone_number
            self._store[session_id] = state
        else:
            if phone_number and not self._store[session_id].patient_phone:
                self._store[session_id].patient_phone = phone_number
        return self._store[session_id]

    def save(self, state: ReceptionistState) -> None:
        self._store[state.session_id] = state

    def clear(self, session_id: str) -> None:
        if session_id in self._store:
            del self._store[session_id]

    def reset_all(self) -> None:
        self._store.clear()

session_store = SessionStore()
