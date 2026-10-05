import sys
from fastapi.testclient import TestClient
from app.main import app
from app.services.medical.routing_service import route_symptoms
from app.schemas.medical_routing import UrgencyLevel, RoutingConfidence

# Ensure clean UTF-8 console output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_medical_routing_verification():
    print("=" * 70)
    print("PHASE 4 — MEDICAL ROUTING & SAFETY ENGINE VERIFICATION")
    print("=" * 70)

    # -------------------------------------------------------------
    # [1] Routine Specialty Routing (High Confidence)
    # -------------------------------------------------------------
    print("\n[1] Routine Specialty Routing")
    routine_cases = [
        ("I have severe tooth ache since yesterday morning", "Dentistry", "tooth_pain"),
        ("Red itchy skin rash and acne breakouts on my face", "Dermatology", "skin_rash"),
        ("Severe knee pain and swollen joint when walking", "Orthopedics", "joint_pain"),
        ("Eye pain and blurry vision in my right eye", "Ophthalmology", "eye_pain"),
        ("Burning urination and pain in my bladder", "Urology", "urinary_problem"),
        ("Stomach ache, acid reflux and bloating after eating", "Gastroenterology", "abdominal_pain"),
    ]

    for text, expected_spec, expected_concept in routine_cases:
        res = route_symptoms(text)
        assert res.selected_specialty == expected_spec, f"Expected {expected_spec}, got {res.selected_specialty}"
        assert res.confidence == RoutingConfidence.HIGH
        assert res.urgency == UrgencyLevel.ROUTINE
        assert res.emergency_detected is False
        assert res.booking_allowed is True
        assert res.escalation_required is False
        assert expected_concept in res.normalized_symptoms
        print(f"    [PASS] '{text[:40]}...' -> {res.selected_specialty} (Confidence: HIGH, Booking: ALLOWED)")

    # -------------------------------------------------------------
    # [2] Red-Flag Emergency Screening (Booking Blocked + Escalation)
    # -------------------------------------------------------------
    print("\n[2] Red-Flag Emergency Detection & Life Safety Rules")
    emergency_cases = [
        ("I cannot breathe and I am gasping for air", "severe_breathing_difficulty"),
        ("Severe crushing chest pain radiating to my left arm", "acute_chest_pain_cardiac"),
        ("My mother has sudden facial drooping and slurred speech sudden", "stroke_symptoms"),
        ("Unresponsive and passed out on the floor", "loss_of_consciousness"),
        ("Deep wound with uncontrolled bleeding heavily won't stop", "uncontrolled_bleeding"),
        ("Throat is swelling up and severe allergic reaction", "anaphylaxis_allergy"),
    ]

    for text, expected_rule in emergency_cases:
        res = route_symptoms(text)
        assert res.emergency_detected is True, f"Failed to detect emergency for '{text}'"
        assert res.urgency == UrgencyLevel.EMERGENCY
        assert res.booking_allowed is False
        assert res.escalation_required is True
        assert expected_rule in res.matched_rules
        assert res.safety_message is not None
        print(f"    [PASS] '{text[:40]}...' -> EMERGENCY: {expected_rule} (Booking: BLOCKED, Escalation: CRITICAL)")

    # -------------------------------------------------------------
    # [3] Clinical Negation Handling (Preventing False Positives)
    # -------------------------------------------------------------
    print("\n[3] Clinical Negation Handling")
    negated_cases = [
        ("I have mild knee pain with no severe chest pain", "Orthopedics"),
        ("Headache but not having difficulty breathing", "Neurology"),
        ("Patient denies loss of consciousness, just has a toothache", "Dentistry"),
    ]

    for text, expected_spec in negated_cases:
        res = route_symptoms(text)
        assert res.emergency_detected is False, f"False positive emergency on negated text: '{text}'"
        print(f"    [PASS] Negated danger signs recognized: '{text[:45]}...' -> Emergency: FALSE")

    # -------------------------------------------------------------
    # [4] Multi-Specialty Ambiguity & Clarification Cues
    # -------------------------------------------------------------
    print("\n[4] Multi-Specialty Ambiguity Handling")
    ambiguous_cases = [
        ("I have had a throbbing headache for 3 days", ["Neurology", "General Medicine"]),
        ("Sore throat with scratchy throat", ["ENT", "General Medicine"]),
    ]

    for text, expected_specs in ambiguous_cases:
        res = route_symptoms(text)
        assert res.confidence == RoutingConfidence.MEDIUM
        assert res.selected_specialty is None
        assert res.clarification_required is True
        assert res.clarification_question is not None
        assert res.booking_allowed is False
        print(f"    [PASS] '{text[:40]}...' -> Multi-Specialty ({res.possible_specialties}) -> Clarification: REQUIRED")

    # -------------------------------------------------------------
    # [5] Vague / Insufficient Symptom Complaints
    # -------------------------------------------------------------
    print("\n[5] Vague Symptom Handling")
    vague_texts = [
        "I don't feel well today",
        "I feel sick and bad",
        "I have body pain everywhere",
    ]

    for text in vague_texts:
        res = route_symptoms(text)
        assert res.confidence == RoutingConfidence.LOW
        assert res.selected_specialty is None
        assert res.clarification_required is True
        assert res.booking_allowed is False
        print(f"    [PASS] Vague text '{text}' -> Confidence: LOW, Clarification: '{res.clarification_question[:50]}...'")

    # -------------------------------------------------------------
    # [6] Human Operator Escalation Requests
    # -------------------------------------------------------------
    print("\n[6] Human Escalation Detection")
    human_request = "I have a toothache and please connect me to a receptionist"
    res_human = route_symptoms(human_request)
    assert res_human.selected_specialty == "Dentistry"
    assert res_human.escalation_required is True
    assert res_human.emergency_detected is False
    print(f"    [PASS] '{human_request[:45]}...' -> Escalation: REQUIRED (Human Agent Requested)")

    # -------------------------------------------------------------
    # [7] FastAPI Endpoint /api/v1/medical-routing Verification
    # -------------------------------------------------------------
    print("\n[7] FastAPI REST API /api/v1/medical-routing Endpoint")
    client = TestClient(app)

    # 7.1 Routine HTTP request
    http_routine = client.post("/api/v1/medical-routing", json={
        "symptom_text": "I have broken tooth and gum pain",
        "patient_id": 1
    })
    assert http_routine.status_code == 200
    d_routine = http_routine.json()
    assert d_routine["selected_specialty"] == "Dentistry"
    assert d_routine["booking_allowed"] is True
    print("    [PASS] POST /api/v1/medical-routing (Routine): 200 OK -> Dentistry (Booking: ALLOWED)")

    # 7.2 Emergency HTTP request
    http_emerg = client.post("/api/v1/medical-routing", json={
        "symptom_text": "Cannot breathe and gasping for air"
    })
    assert http_emerg.status_code == 200
    d_emerg = http_emerg.json()
    assert d_emerg["emergency_detected"] is True
    assert d_emerg["booking_allowed"] is False
    assert d_emerg["escalation_required"] is True
    print("    [PASS] POST /api/v1/medical-routing (Emergency): 200 OK -> Emergency: TRUE (Booking: BLOCKED)")

    # 7.3 Clarification HTTP request
    http_clarif = client.post("/api/v1/medical-routing", json={
        "symptom_text": "I feel strange and not well"
    })
    assert http_clarif.status_code == 200
    d_clarif = http_clarif.json()
    assert d_clarif["clarification_required"] is True
    assert d_clarif["booking_allowed"] is False
    print("    [PASS] POST /api/v1/medical-routing (Vague): 200 OK -> Clarification: REQUIRED")

    # 7.4 Input validation error (422)
    http_val = client.post("/api/v1/medical-routing", json={"symptom_text": ""})
    assert http_val.status_code == 422
    assert http_val.json()["error"]["code"] == "VALIDATION_ERROR"
    print("    [PASS] POST /api/v1/medical-routing (Empty): 422 VALIDATION_ERROR")

    print("\n" + "=" * 70)
    print("ALL 7 PHASE 4 MEDICAL ROUTING & SAFETY SCENARIOS VERIFIED AND PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    run_medical_routing_verification()
