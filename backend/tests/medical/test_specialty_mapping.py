import pytest
from app.services.medical.specialty_mapper import map_symptoms_to_specialties

def test_map_single_clear_specialty():
    cases = [
        (["tooth_pain"], "Dentistry"),
        (["skin_rash"], "Dermatology"),
        (["chest_pain"], "Cardiology"),
        (["eye_pain"], "Ophthalmology"),
        (["ear_pain"], "ENT"),
        (["joint_pain"], "Orthopedics"),
        (["abdominal_pain"], "Gastroenterology"),
        (["urinary_problem"], "Urology"),
        (["menstrual_problem"], "Gynecology"),
        (["anxiety_depression"], "Psychiatry"),
    ]
    for terms, expected_spec in cases:
        res = map_symptoms_to_specialties(terms)
        assert res["confidence"] == "high"
        assert res["selected_specialty"] == expected_spec
        assert res["clarification_required"] is False
        assert len(res["matched_rules"]) >= 1

def test_map_multi_specialty_ambiguous_concept():
    # Headache maps to Neurology and General Medicine
    res = map_symptoms_to_specialties(["headache"])
    assert res["confidence"] == "medium"
    assert res["selected_specialty"] is None
    assert "Neurology" in res["possible_specialties"]
    assert "General Medicine" in res["possible_specialties"]
    assert res["clarification_required"] is True
    assert res["clarification_question"] is not None

def test_map_multiple_symptoms_reinforcing_same_specialty():
    # Both acne and skin_rash point to Dermatology
    res = map_symptoms_to_specialties(["acne", "skin_rash"])
    assert res["confidence"] == "high"
    assert res["selected_specialty"] == "Dermatology"
    assert res["clarification_required"] is False

def test_map_multiple_symptoms_different_specialties():
    # eye_pain (Ophthalmology) + tooth_pain (Dentistry) -> tied votes
    res = map_symptoms_to_specialties(["eye_pain", "tooth_pain"])
    assert res["confidence"] == "medium"
    assert res["selected_specialty"] is None
    assert "Ophthalmology" in res["possible_specialties"]
    assert "Dentistry" in res["possible_specialties"]
    assert res["clarification_required"] is True

def test_map_unknown_or_empty_symptoms():
    res_empty = map_symptoms_to_specialties([])
    assert res_empty["confidence"] == "low"
    assert res_empty["selected_specialty"] is None
    assert res_empty["clarification_required"] is True

def test_map_vague_input_forced_low_confidence():
    res_vague = map_symptoms_to_specialties(["headache"], is_vague=True)
    assert res_vague["confidence"] == "low"
    assert res_vague["selected_specialty"] is None
    assert res_vague["clarification_required"] is True
