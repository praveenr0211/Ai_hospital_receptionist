import re
from app.schemas.medical_routing import EscalationDecision, SafetyDecision, UrgencyLevel
from app.services.medical.normalization_service import clean_text

HUMAN_AGENT_REQUEST_PATTERNS = [
    r"\bspeak to (a )?(human|person|agent|representative|operator|doctor|nurse|receptionist)\b",
    r"\btalk to (a )?(human|person|agent|representative|operator|doctor|nurse|receptionist)\b",
    r"\btransfer (me )?to (a )?(human|person|agent|operator|representative|doctor|nurse|receptionist)\b",
    r"\bhuman (agent|operator|please)\b",
    r"\bconnect (me )?to (a )?(human|person|agent|operator|representative|receptionist)\b"
]

def check_explicit_human_request(text: str) -> bool:
    cleaned = clean_text(text)
    for pat in HUMAN_AGENT_REQUEST_PATTERNS:
        if re.search(pat, cleaned):
            return True
    return False


def determine_escalation(
    raw_text: str,
    safety_decision: SafetyDecision,
    emergency_priority: str
) -> EscalationDecision:
    """
    Decide whether this patient contact must be transferred to a human operator or clinical triage team.
    """
    # 1. Emergency condition
    if safety_decision.urgency == UrgencyLevel.EMERGENCY:
        return EscalationDecision(
            required=True,
            reason="Emergency red-flag symptoms detected; clinical intervention required immediately.",
            priority="critical"
        )

    # 2. Urgent condition
    if safety_decision.urgency == UrgencyLevel.URGENT:
        return EscalationDecision(
            required=True,
            reason="Urgent clinical indicators require nursing or staff review.",
            priority="urgent"
        )

    # 3. Explicit human agent request
    if check_explicit_human_request(raw_text):
        return EscalationDecision(
            required=True,
            reason="Patient explicitly requested to speak with a human receptionist/clinical staff.",
            priority="normal"
        )

    # 4. Standard safety escalation flag
    if safety_decision.escalation_required:
        return EscalationDecision(
            required=True,
            reason=safety_decision.reason,
            priority="normal"
        )

    return EscalationDecision(
        required=False,
        reason=None,
        priority="normal"
    )
