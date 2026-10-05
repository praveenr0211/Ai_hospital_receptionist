from enum import Enum
from pydantic import BaseModel, Field

class UrgencyLevel(str, Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class RoutingConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class MedicalRoutingRequest(BaseModel):
    symptom_text: str = Field(..., min_length=2, max_length=2000, description="Patient symptom description in natural language")
    patient_id: int | None = Field(default=None, description="Optional patient ID if identified")
    call_id: int | None = Field(default=None, description="Optional call ID if initiated via phone call")

class NormalizedSymptom(BaseModel):
    original_text: str
    normalized_terms: list[str]
    body_area: str | None = None
    duration: str | None = None
    severity: str | None = None

class SafetyDecision(BaseModel):
    booking_allowed: bool
    escalation_required: bool
    urgency: UrgencyLevel
    reason: str

class EscalationDecision(BaseModel):
    required: bool
    reason: str | None = None
    priority: str = "normal"  # normal, urgent, critical

class MedicalRoutingResponse(BaseModel):
    normalized_symptoms: list[str] = Field(default_factory=list, description="Extracted standard symptom concepts")
    possible_specialties: list[str] = Field(default_factory=list, description="Candidate medical departments")
    selected_specialty: str | None = Field(default=None, description="Primary mapped specialty if resolved")
    confidence: RoutingConfidence = Field(..., description="Confidence level: high, medium, low")
    urgency: UrgencyLevel = Field(..., description="Clinical triage urgency: routine, urgent, emergency")
    emergency_detected: bool = Field(..., description="True if red-flag life safety indicators matched")
    booking_allowed: bool = Field(..., description="True if automated appointment booking is clinically safe to proceed")
    escalation_required: bool = Field(..., description="True if caller must be transferred to human clinical staff")
    clarification_required: bool = Field(..., description="True if symptom description is too vague to route safely")
    clarification_question: str | None = Field(default=None, description="Targeted question to ask patient if clarification is needed")
    safety_message: str | None = Field(default=None, description="Clinical guidance message for patient or operator")
    matched_rules: list[str] = Field(default_factory=list, description="Auditable rule IDs triggered during routing")
