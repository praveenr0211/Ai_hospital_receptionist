from app.schemas.tool_results import EscalationToolResult

def request_human_escalation(
    reason: str,
    escalation_type: str = "HUMAN_REQUEST",
) -> EscalationToolResult:
    """Escalate conversation to human hospital staff or emergency team."""
    team_mapping = {
        "EMERGENCY": "EMERGENCY_DESK",
        "HUMAN_REQUEST": "HUMAN_OPERATOR",
        "MEDICAL_UNCERTAINTY": "CLINICAL_TRIAGE",
        "BOOKING_FAILURE": "PATIENT_SUPPORT",
    }
    assigned_team = team_mapping.get(escalation_type, "HUMAN_OPERATOR")

    return EscalationToolResult(
        success=True,
        escalation_type=escalation_type,
        reason=reason,
        assigned_team=assigned_team,
    )
