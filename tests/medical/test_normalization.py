import pytest
from app.services.medical.normalization_service import (
    clean_text,
    extract_duration,
    extract_severity,
    is_vague_complaint,
    normalize_symptoms,
)

def test_clean_text_removes_punctuation_and_lowercases():
    raw = "Hello! I am HAVING... chest pain, since yesterday???"
    cleaned = clean_text(raw)
    assert cleaned == "hello i am having chest pain since yesterday"

def test_normalize_tooth_pain_synonyms():
    variations = [
        "tooth pain",
        "tooth ache",
        "toothache",
        "teeth hurting",
        "pain in my tooth",
        "wisdom tooth pain",
        "dental pain"
    ]
    for text in variations:
        res = normalize_symptoms(text)
        assert "tooth_pain" in res.normalized_terms, f"Failed for '{text}'"
        assert res.body_area == "mouth"

def test_normalize_chest_pain_synonyms():
    variations = [
        "chest pain",
        "pressure in chest",
        "chest discomfort",
        "heart pain",
        "tightness in chest"
    ]
    for text in variations:
        res = normalize_symptoms(text)
        assert "chest_pain" in res.normalized_terms, f"Failed for '{text}'"
        assert res.body_area == "chest"

def test_normalize_skin_rash_and_acne():
    res_rash = normalize_symptoms("I have a severe red rash on skin with itching")
    assert "skin_rash" in res_rash.normalized_terms
    assert res_rash.body_area == "skin"

    res_acne = normalize_symptoms("I am breaking out with facial pimples and acne")
    assert "acne" in res_acne.normalized_terms
    assert res_acne.body_area == "skin"

def test_normalize_joint_and_back_pain():
    res_knee = normalize_symptoms("severe knee pain and swollen joint")
    assert "joint_pain" in res_knee.normalized_terms
    assert res_knee.body_area == "joints"

    res_back = normalize_symptoms("terrible lower back pain and stiff neck")
    assert "back_pain" in res_back.normalized_terms
    assert res_back.body_area == "back"

def test_normalize_eye_and_ear_issues():
    res_eye = normalize_symptoms("my eye hurts and I have blurry vision")
    assert "eye_pain" in res_eye.normalized_terms
    assert "vision_problem" in res_eye.normalized_terms

    res_ear = normalize_symptoms("earache and ringing in ears")
    assert "ear_pain" in res_ear.normalized_terms
    assert "hearing_problem" in res_ear.normalized_terms

def test_normalize_stomach_urinary_menstrual():
    res_stomach = normalize_symptoms("acid reflux and stomach pain")
    assert "abdominal_pain" in res_stomach.normalized_terms

    res_urine = normalize_symptoms("burning urination and bladder pain")
    assert "urinary_problem" in res_urine.normalized_terms

    res_periods = normalize_symptoms("irregular periods and severe menstrual cramps")
    assert "menstrual_problem" in res_periods.normalized_terms

def test_extract_duration_patterns():
    assert extract_duration("headache for 2 days") == "for 2 days"
    assert extract_duration("chest discomfort since yesterday") == "since yesterday"
    assert extract_duration("ear pain for three weeks") == "for three weeks"
    assert extract_duration("toothache since morning") == "since morning"
    assert extract_duration("pain") is None

def test_extract_severity_patterns():
    assert extract_severity("severe tooth pain") == "severe"
    assert extract_severity("mild headache") == "mild"
    assert extract_severity("excruciating back pain") == "excruciating"
    assert extract_severity("just some tooth pain") is None

def test_is_vague_complaint_detection():
    vague_phrases = [
        "I don't feel well",
        "i feel sick",
        "feeling strange",
        "i have pain",
        "body pain",
        "something is wrong with me",
        "i feel bad"
    ]
    for phrase in vague_phrases:
        assert is_vague_complaint(phrase) is True, f"Expected '{phrase}' to be detected as vague"

def test_specific_complaint_not_vague():
    specific_phrases = [
        "I have a toothache",
        "my left eye is red and painful",
        "burning pain during urination",
        "knee pain after running"
    ]
    for phrase in specific_phrases:
        assert is_vague_complaint(phrase) is False, f"Expected '{phrase}' not to be vague"
