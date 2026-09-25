import pytest
from app.services.medical.routing_service import route_symptoms
from app.schemas.medical_routing import UrgencyLevel, RoutingConfidence

def test_route_routine_dentistry():
    res = route_symptoms("I have had severe toothache for two days")
    assert res.selected_specialty == "Dentistry"
    assert res.confidence == RoutingConfidence.HIGH
    assert res.urgency == UrgencyLevel.ROUTINE
    assert res.emergency_detected is False
    assert res.booking_allowed is True
    assert res.escalation_required is False
    assert "tooth_pain" in res.normalized_symptoms

def test_route_routine_dermatology():
    res = route_symptoms("Red itchy skin rash on both my arms")
    assert res.selected_specialty == "Dermatology"
    assert res.confidence == RoutingConfidence.HIGH
    assert res.booking_allowed is True
    assert res.emergency_detected is False

def test_route_routine_orthopedics():
    res = route_symptoms("Terrible lower back pain and stiff joints")
    assert res.selected_specialty == "Orthopedics"
    assert res.confidence == RoutingConfidence.HIGH
    assert res.booking_allowed is True

def test_route_routine_ophthalmology():
    res = route_symptoms("My eye is hurting and I have blurry vision")
    assert res.selected_specialty == "Ophthalmology"
    assert res.confidence == RoutingConfidence.HIGH
    assert res.booking_allowed is True

def test_route_routine_urology():
    res = route_symptoms("Burning urination and frequent urination for a week")
    assert res.selected_specialty == "Urology"
    assert res.confidence == RoutingConfidence.HIGH
    assert res.booking_allowed is True

def test_route_emergency_respiratory():
    res = route_symptoms("I cannot breathe and I am gasping for air")
    assert res.emergency_detected is True
    assert res.urgency == UrgencyLevel.EMERGENCY
    assert res.booking_allowed is False
    assert res.escalation_required is True
    assert res.selected_specialty is None
    assert "severe_breathing_difficulty" in res.matched_rules
    assert res.safety_message is not None

def test_route_emergency_cardiac():
    res = route_symptoms("Severe chest pain radiating to my left arm")
    assert res.emergency_detected is True
    assert res.urgency == UrgencyLevel.EMERGENCY
    assert res.booking_allowed is False
    assert res.escalation_required is True
    assert "acute_chest_pain_cardiac" in res.matched_rules

def test_route_emergency_stroke():
    res = route_symptoms("My father has sudden facial drooping and slurred speech sudden")
    assert res.emergency_detected is True
    assert res.booking_allowed is False
    assert res.escalation_required is True
    assert "stroke_symptoms" in res.matched_rules

def test_route_ambiguous_vague_input():
    res = route_symptoms("I don't feel well today")
    assert res.confidence == RoutingConfidence.LOW
    assert res.selected_specialty is None
    assert res.booking_allowed is False
    assert res.clarification_required is True
    assert res.clarification_question is not None

def test_route_multi_specialty_headache():
    res = route_symptoms("I have a persistent headache since yesterday")
    assert res.confidence == RoutingConfidence.MEDIUM
    assert res.selected_specialty is None
    assert "Neurology" in res.possible_specialties
    assert "General Medicine" in res.possible_specialties
    assert res.booking_allowed is False
    assert res.clarification_required is True

def test_route_with_explicit_human_request():
    res = route_symptoms("I have a toothache and please connect me to a receptionist")
    assert res.selected_specialty == "Dentistry"
    assert res.escalation_required is True
    assert res.emergency_detected is False
