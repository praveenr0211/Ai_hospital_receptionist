from typing import Callable, Tuple
from sqlalchemy.orm import Session
from app.agent.state import ReceptionistState
from app.schemas.agent import ConversationState, ActionRequired
from app.agent.nodes import (
    node_greeting,
    node_identify_patient,
    node_understand_intent,
    node_collect_symptoms,
    node_medical_routing,
    node_emergency_handling,
    node_find_doctor,
    node_check_availability,
    node_offer_slots,
    node_wait_confirmation,
    node_book_appointment,
    node_cancel_appointment,
    node_reschedule_appointment,
    node_human_escalation,
    node_clarification,
)
from app.agent.llm import classify_intent

NODE_DISPATCH: dict[ConversationState, Callable[[ReceptionistState, str, Session], Tuple[str, ActionRequired]]] = {
    "GREETING": node_greeting,
    "IDENTIFY_PATIENT": node_identify_patient,
    "UNDERSTAND_INTENT": node_understand_intent,
    "COLLECT_SYMPTOMS": node_collect_symptoms,
    "MEDICAL_ROUTING": node_medical_routing,
    "EMERGENCY_HANDLING": node_emergency_handling,
    "FIND_DOCTOR": node_find_doctor,
    "CHECK_AVAILABILITY": node_check_availability,
    "OFFER_SLOTS": node_offer_slots,
    "WAIT_CONFIRMATION": node_wait_confirmation,
    "BOOK_APPOINTMENT": node_book_appointment,
    "BOOKING_COMPLETE": node_greeting,
    "CANCEL_APPOINTMENT": node_cancel_appointment,
    "RESCHEDULE_APPOINTMENT": node_reschedule_appointment,
    "HUMAN_ESCALATION": node_human_escalation,
    "CLARIFICATION": node_clarification,
    "END": node_greeting,
}

def route_conversation(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    """
    Route conversation turn through the state machine.
    Handles global interrupts (emergency keywords or human escalation requests)
    before dispatching to the current state node.
    """
    # Global intent detection
    intent_check = classify_intent(user_message, state.current_state)
    if intent_check.intent != "UNKNOWN" or state.intent is None:
        state.intent = intent_check.intent
        state.intent_confidence = intent_check.confidence

    # Global interrupt 1: Check for emergency in any state
    if intent_check.intent == "EMERGENCY":
        state.previous_state = state.current_state
        state.current_state = "EMERGENCY_HANDLING"
        return node_emergency_handling(state, user_message, db)

    # Global interrupt 2: Check for direct human agent request (unless in confirmation)
    if intent_check.intent == "HUMAN_AGENT" and state.current_state != "WAIT_CONFIRMATION":
        state.previous_state = state.current_state
        state.current_state = "HUMAN_ESCALATION"
        return node_human_escalation(state, user_message, db)

    # Global interrupt 3: Cancellation request mid-flow
    if intent_check.intent == "CANCEL_APPOINTMENT" and state.current_state not in {"WAIT_CONFIRMATION", "CANCEL_APPOINTMENT"}:
        state.previous_state = state.current_state
        state.current_state = "CANCEL_APPOINTMENT"
        return node_cancel_appointment(state, user_message, db)

    # Global interrupt 4: Reschedule request mid-flow
    if intent_check.intent == "RESCHEDULE_APPOINTMENT" and state.current_state not in {"WAIT_CONFIRMATION", "RESCHEDULE_APPOINTMENT"}:
        state.previous_state = state.current_state
        state.current_state = "RESCHEDULE_APPOINTMENT"
        return node_reschedule_appointment(state, user_message, db)

    # Dispatch to handler for current state
    handler = NODE_DISPATCH.get(state.current_state, node_understand_intent)
    return handler(state, user_message, db)
