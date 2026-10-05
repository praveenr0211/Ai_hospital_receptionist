import pytest
from app.schemas.medical_routing import UrgencyLevel, RoutingConfidence
from app.services.medical.safety_service import evaluate_safety

def test_safety_emergency_blocks_booking():
    decision = evaluate_safety(
        emergency_detected=True,
        urgency_str="emergency",
        confidence=RoutingConfidence.HIGH,
        clarification_required=False,
        matched_emergency_rules=["severe_breathing_difficulty"]
    )
    assert decision.booking_allowed is False
    assert decision.escalation_required is True
    assert decision.urgency == UrgencyLevel.EMERGENCY
    assert "unsafe" in decision.reason.lower()

def test_safety_urgent_blocks_booking():
    decision = evaluate_safety(
        emergency_detected=False,
        urgency_str="urgent",
        confidence=RoutingConfidence.HIGH,
        clarification_required=False,
        matched_emergency_rules=[]
    )
    assert decision.booking_allowed is False
    assert decision.escalation_required is True
    assert decision.urgency == UrgencyLevel.URGENT

def test_safety_ambiguity_blocks_booking_without_emergency():
    decision = evaluate_safety(
        emergency_detected=False,
        urgency_str="routine",
        confidence=RoutingConfidence.LOW,
        clarification_required=True,
        matched_emergency_rules=[]
    )
    assert decision.booking_allowed is False
    assert decision.escalation_required is False
    assert decision.urgency == UrgencyLevel.ROUTINE

def test_safety_medium_confidence_blocks_booking():
    decision = evaluate_safety(
        emergency_detected=False,
        urgency_str="routine",
        confidence=RoutingConfidence.MEDIUM,
        clarification_required=True,
        matched_emergency_rules=[]
    )
    assert decision.booking_allowed is False
    assert decision.escalation_required is False

def test_safety_routine_high_confidence_permits_booking():
    decision = evaluate_safety(
        emergency_detected=False,
        urgency_str="routine",
        confidence=RoutingConfidence.HIGH,
        clarification_required=False,
        matched_emergency_rules=[]
    )
    assert decision.booking_allowed is True
    assert decision.escalation_required is False
    assert decision.urgency == UrgencyLevel.ROUTINE
