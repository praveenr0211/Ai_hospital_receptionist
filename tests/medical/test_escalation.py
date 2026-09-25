import pytest
from app.schemas.medical_routing import SafetyDecision, UrgencyLevel
from app.services.medical.escalation_service import determine_escalation, check_explicit_human_request

def test_explicit_human_request_patterns():
    phrases = [
        "I want to speak to a human please",
        "can I talk to a doctor",
        "please transfer me to a representative",
        "connect me to a receptionist",
        "human operator please"
    ]
    for p in phrases:
        assert check_explicit_human_request(p) is True

def test_escalation_for_emergency():
    safety = SafetyDecision(
        booking_allowed=False,
        escalation_required=True,
        urgency=UrgencyLevel.EMERGENCY,
        reason="Emergency detected"
    )
    esc = determine_escalation("severe chest pain", safety, emergency_priority="critical")
    assert esc.required is True
    assert esc.priority == "critical"

def test_escalation_for_urgent():
    safety = SafetyDecision(
        booking_allowed=False,
        escalation_required=True,
        urgency=UrgencyLevel.URGENT,
        reason="Urgent clinical indicators"
    )
    esc = determine_escalation("high fever with stiff neck", safety, emergency_priority="urgent")
    assert esc.required is True
    assert esc.priority == "urgent"

def test_escalation_for_explicit_human_request():
    safety = SafetyDecision(
        booking_allowed=True,
        escalation_required=False,
        urgency=UrgencyLevel.ROUTINE,
        reason="Routine appointment"
    )
    esc = determine_escalation("I have a toothache and want to speak to a human operator", safety, emergency_priority="normal")
    assert esc.required is True
    assert esc.priority == "normal"
    assert "human" in esc.reason.lower()

def test_no_escalation_for_routine_case():
    safety = SafetyDecision(
        booking_allowed=True,
        escalation_required=False,
        urgency=UrgencyLevel.ROUTINE,
        reason="Routine high confidence"
    )
    esc = determine_escalation("I have a toothache for two days", safety, emergency_priority="normal")
    assert esc.required is False
    assert esc.reason is None
