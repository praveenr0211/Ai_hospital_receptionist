import pytest
from app.services.medical.emergency_service import detect_emergencies

def test_detect_severe_breathing_difficulty():
    inputs = [
        "I can't breathe right now",
        "patient is gasping for air",
        "having severe difficulty breathing since 10 minutes",
        "unable to breathe properly and choking"
    ]
    for text in inputs:
        res = detect_emergencies(text)
        assert res["emergency_detected"] is True, f"Failed for '{text}'"
        assert res["urgency"] == "emergency"
        assert "severe_breathing_difficulty" in res["matched_rules"]
        assert res["safety_message"] is not None

def test_detect_acute_chest_pain_cardiac():
    inputs = [
        "I have severe chest pain",
        "crushing chest pain radiating to my left arm",
        "elephant on my chest and sweating profusely",
        "crushing pressure in chest"
    ]
    for text in inputs:
        res = detect_emergencies(text)
        assert res["emergency_detected"] is True, f"Failed for '{text}'"
        assert res["urgency"] == "emergency"
        assert "acute_chest_pain_cardiac" in res["matched_rules"]

def test_detect_stroke_symptoms():
    inputs = [
        "my mother has facial drooping and can't speak suddenly",
        "sudden paralysis on one side of body and arm weakness sudden",
        "sudden loss of vision and face drooping"
    ]
    for text in inputs:
        res = detect_emergencies(text)
        assert res["emergency_detected"] is True, f"Failed for '{text}'"
        assert "stroke_symptoms" in res["matched_rules"]

def test_detect_loss_of_consciousness():
    inputs = [
        "my friend passed out and is unresponsive",
        "loss of consciousness after hitting head",
        "patient is unconscious right now"
    ]
    for text in inputs:
        res = detect_emergencies(text)
        assert res["emergency_detected"] is True, f"Failed for '{text}'"
        assert "loss_of_consciousness" in res["matched_rules"]

def test_detect_uncontrolled_bleeding():
    inputs = [
        "deep cut with uncontrolled bleeding",
        "bleeding heavily won't stop from the arm",
        "coughing up large amounts of blood"
    ]
    for text in inputs:
        res = detect_emergencies(text)
        assert res["emergency_detected"] is True, f"Failed for '{text}'"
        assert "uncontrolled_bleeding" in res["matched_rules"]

def test_detect_anaphylaxis():
    inputs = [
        "my throat is swelling up after eating peanuts",
        "severe allergic reaction and tongue swelling",
        "swollen lips can't breathe"
    ]
    for text in inputs:
        res = detect_emergencies(text)
        assert res["emergency_detected"] is True, f"Failed for '{text}'"
        assert "anaphylaxis_allergy" in res["matched_rules"]

def test_negation_prevents_false_positive():
    negated_inputs = [
        "I have mild back pain with no severe chest pain",
        "patient denies loss of consciousness",
        "headache but not having difficulty breathing",
        "without uncontrolled bleeding, just a minor scrape"
    ]
    for text in negated_inputs:
        res = detect_emergencies(text)
        assert res["emergency_detected"] is False, f"False positive for negated '{text}'"

def test_routine_symptoms_not_flagged_as_emergency():
    routine_inputs = [
        "I have a mild toothache for 3 days",
        "itching and skin rash on my forearm",
        "red eyes and slight blurry vision",
        "earache and hard of hearing",
        "knee pain when climbing stairs"
    ]
    for text in routine_inputs:
        res = detect_emergencies(text)
        assert res["emergency_detected"] is False, f"False positive emergency for '{text}'"
        assert res["urgency"] == "routine"
