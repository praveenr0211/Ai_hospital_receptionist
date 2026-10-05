import uuid

def test_appointment_lifecycle_via_api(client):
    """Test full booking, retrieval, rescheduling, and cancellation via REST API."""
    docs = client.get("/api/v1/doctors").json()["items"]
    dr_ravi = next(d for d in docs if "Ravi" in d["name"])
    patient = client.get("/api/v1/patients/by-phone/9876500001").json()

    # 1. Book appointment at 12:00
    book_payload = {
        "patient_id": patient["id"],
        "doctor_id": dr_ravi["id"],
        "appointment_date": "2026-09-25",
        "start_time": "12:00",
        "reason": "API Lifecycle Test"
    }
    create_res = client.post("/api/v1/appointments", json=book_payload)
    assert create_res.status_code == 201
    apt = create_res.json()
    apt_id = apt["appointment_id"]
    assert apt["start_time"] == "12:00"
    assert apt["status"] == "confirmed"

    # 2. Prevent duplicate booking of same slot
    dup_res = client.post("/api/v1/appointments", json=book_payload)
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "SLOT_ALREADY_BOOKED"

    # 3. Retrieve appointment details
    get_res = client.get(f"/api/v1/appointments/{apt_id}")
    assert get_res.status_code == 200
    assert get_res.json()["appointment_id"] == apt_id

    # 4. Reschedule appointment to 12:30
    resched_payload = {
        "new_date": "2026-09-25",
        "new_start_time": "12:30"
    }
    resched_res = client.post(f"/api/v1/appointments/{apt_id}/reschedule", json=resched_payload)
    assert resched_res.status_code == 200
    assert resched_res.json()["new_start_time"] == "12:30"

    # 5. Cancel appointment
    cancel_payload = {
        "reason": "Patient requested cancellation via API"
    }
    cancel_res = client.post(f"/api/v1/appointments/{apt_id}/cancel", json=cancel_payload)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"
    assert cancel_res.json()["cancellation_reason"] == "Patient requested cancellation via API"

    # 6. Cannot cancel already cancelled appointment
    cancel_again = client.post(f"/api/v1/appointments/{apt_id}/cancel", json=cancel_payload)
    assert cancel_again.status_code == 409
    assert cancel_again.json()["error"]["code"] == "APPOINTMENT_ALREADY_CANCELLED"
