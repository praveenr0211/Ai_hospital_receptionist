def test_api_route_routine_symptoms(client):
    payload = {
        "symptom_text": "I have had a bad tooth ache since yesterday",
        "patient_id": 1
    }
    response = client.post("/api/v1/medical-routing", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["selected_specialty"] == "Dentistry"
    assert data["confidence"] == "high"
    assert data["urgency"] == "routine"
    assert data["emergency_detected"] is False
    assert data["booking_allowed"] is True
    assert data["escalation_required"] is False
    assert "tooth_pain" in data["normalized_symptoms"]
    assert len(data["matched_rules"]) >= 1

def test_api_route_emergency_symptoms(client):
    payload = {
        "symptom_text": "Patient has severe chest pain radiating to left arm and cannot breathe"
    }
    response = client.post("/api/v1/medical-routing", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["emergency_detected"] is True
    assert data["urgency"] == "emergency"
    assert data["booking_allowed"] is False
    assert data["escalation_required"] is True
    assert data["safety_message"] is not None
    assert "acute_chest_pain_cardiac" in data["matched_rules"] or "severe_breathing_difficulty" in data["matched_rules"]

def test_api_route_ambiguous_symptoms(client):
    payload = {
        "symptom_text": "I do not feel well at all"
    }
    response = client.post("/api/v1/medical-routing", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] == "low"
    assert data["booking_allowed"] is False
    assert data["clarification_required"] is True
    assert data["clarification_question"] is not None

def test_api_route_empty_input_rejected_with_422(client):
    response = client.post("/api/v1/medical-routing", json={"symptom_text": ""})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
