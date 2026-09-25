import re
from typing import Set
from app.schemas.agent import ConversationState

ALLOWED_TOOLS_PER_STATE: dict[ConversationState, Set[str]] = {
    "GREETING": set(),
    "IDENTIFY_PATIENT": {"find_patient_by_phone", "create_patient"},
    "UNDERSTAND_INTENT": set(),
    "COLLECT_SYMPTOMS": set(),
    "MEDICAL_ROUTING": {"route_medical_symptoms"},
    "EMERGENCY_HANDLING": {"request_human_escalation"},
    "FIND_DOCTOR": {"find_doctors_by_specialty"},
    "CHECK_AVAILABILITY": {"check_doctor_availability"},
    "OFFER_SLOTS": {"check_specific_slot", "find_alternative_slots"},
    # Safety Gate: WAIT_CONFIRMATION strictly forbids booking or mutative tools
    "WAIT_CONFIRMATION": set(),
    # Booking tool only executable in BOOK_APPOINTMENT state
    "BOOK_APPOINTMENT": {"book_appointment_tool"},
    "BOOKING_COMPLETE": set(),
    "CANCEL_APPOINTMENT": {"get_patient_appointments", "cancel_appointment_tool"},
    "RESCHEDULE_APPOINTMENT": {
        "get_patient_appointments",
        "check_doctor_availability",
        "check_specific_slot",
        "reschedule_appointment_tool",
    },
    "HUMAN_ESCALATION": {"request_human_escalation"},
    "CLARIFICATION": set(),
    "END": set(),
}

CONFIRMATION_POSITIVE_KEYWORDS = {
    "yes", "yeah", "yep", "sure", "please", "confirm", "proceed",
    "book it", "book", "go ahead", "do it", "agree", "correct", "fine"
}

CONFIRMATION_NEGATIVE_KEYWORDS = {
    "no", "nope", "cancel", "don't", "dont", "wait", "hold on", "stop", "nevermind", "change"
}

def is_tool_allowed(state: ConversationState, tool_name: str) -> bool:
    """Validate whether a tool is permitted to execute in the current state."""
    allowed = ALLOWED_TOOLS_PER_STATE.get(state, set())
    return tool_name in allowed

def parse_user_confirmation(user_input: str, confirmation_intent: str | None = None) -> bool | None:
    """
    Parse whether the user's input expresses explicit positive confirmation,
    negative rejection, or ambiguous text requiring clarification.
    """
    clean = user_input.strip().lower()

    if confirmation_intent == "CANCELLATION":
        if any(neg in clean for neg in ["no", "don't", "dont", "keep it", "nevermind"]):
            return False
        if any(pos in clean for pos in ["yes", "yeah", "yep", "sure", "cancel", "confirm", "proceed", "please", "do it"]):
            return True
        return None

    # Positive confirmation for booking/reschedule
    for pos in ["yes", "yeah", "yep", "sure", "please", "confirm", "proceed", "book it", "go ahead", "do it", "fine"]:
        if re.search(rf"\b{pos}\b", clean):
            return True

    # Negative rejection
    for neg in ["no", "nope", "cancel", "don't", "dont", "wait", "hold on", "stop", "nevermind", "change"]:
        if re.search(rf"\b{neg}\b", clean):
            return False

    return None
