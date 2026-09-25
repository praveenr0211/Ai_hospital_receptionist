from app.services.medical.routing_service import route_symptoms
from app.schemas.tool_results import MedicalRoutingToolResult

def route_medical_symptoms(symptom_text: str) -> MedicalRoutingToolResult:
    """
    Route patient symptoms via the Phase 4 Clinical Medical Routing & Safety Engine.
    
    Deterministically determines specialty, screens for red-flag emergencies,
    calculates routing confidence, and decides whether routine booking is safe.
    """
    if not symptom_text or not symptom_text.strip():
        return MedicalRoutingToolResult(
            success=False,
            specialty=None,
            confidence="low",
            emergency_detected=False,
            booking_allowed=False,
            escalation_required=False,
            reasoning="Empty symptom text provided.",
            error="Empty symptom description.",
        )
    
    result = route_symptoms(symptom_text.strip())
    
    return MedicalRoutingToolResult(
        success=True,
        specialty=result.selected_specialty,
        confidence=result.confidence.value if hasattr(result.confidence, "value") else str(result.confidence),
        emergency_detected=result.emergency_detected,
        booking_allowed=result.booking_allowed,
        escalation_required=result.escalation_required,
        normalized_symptoms=result.normalized_symptoms,
        clarification_cue=result.clarification_question,
        reasoning=result.safety_message,
    )
