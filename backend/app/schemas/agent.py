from typing import Any, Literal
from pydantic import BaseModel, Field

IntentType = Literal[
    "BOOK_APPOINTMENT",
    "CHECK_AVAILABILITY",
    "CANCEL_APPOINTMENT",
    "RESCHEDULE_APPOINTMENT",
    "DOCTOR_INFORMATION",
    "GENERAL_HOSPITAL_QUERY",
    "HUMAN_AGENT",
    "EMERGENCY",
    "UNKNOWN",
]

IntentConfidence = Literal["high", "medium", "low"]

ConversationState = Literal[
    "GREETING",
    "IDENTIFY_PATIENT",
    "UNDERSTAND_INTENT",
    "COLLECT_SYMPTOMS",
    "MEDICAL_ROUTING",
    "EMERGENCY_HANDLING",
    "FIND_DOCTOR",
    "CHECK_AVAILABILITY",
    "OFFER_SLOTS",
    "WAIT_CONFIRMATION",
    "BOOK_APPOINTMENT",
    "BOOKING_COMPLETE",
    "CANCEL_APPOINTMENT",
    "RESCHEDULE_APPOINTMENT",
    "HUMAN_ESCALATION",
    "CLARIFICATION",
    "END",
]

ActionRequired = Literal[
    "USER_INPUT",
    "CONFIRMATION_REQUIRED",
    "HUMAN_ESCALATION",
    "COMPLETED",
]

class IntentResult(BaseModel):
    intent: IntentType
    confidence: IntentConfidence = "high"
    extracted_entities: dict[str, Any] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Unique conversation session ID")
    message: str = Field(..., min_length=1, description="User message text")
    phone_number: str | None = Field(default=None, description="Optional caller phone number")

class AgentResponse(BaseModel):
    session_id: str
    message: str
    state: ConversationState
    action_required: ActionRequired
    appointment_id: int | None = None
    escalation_required: bool = False
    data: dict[str, Any] | None = None
