def test_create_and_list_calls(client):
    payload = {
        "patient_id": 1,
        "phone_number": "9876500001",
        "intent": "appointment_booking",
        "specialty_detected": "Cardiology",
        "duration_seconds": 180,
        "outcome": "appointment_booked",
        "escalated": False
    }
    create_res = client.post("/api/v1/calls", json=payload)
    assert create_res.status_code == 201
    call_data = create_res.json()
    assert call_data["intent"] == "appointment_booking"
    assert call_data["outcome"] == "appointment_booked"
    assert "id" in call_data

    list_res = client.get("/api/v1/calls")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert "items" in list_data
    assert list_data["total"] >= 1
