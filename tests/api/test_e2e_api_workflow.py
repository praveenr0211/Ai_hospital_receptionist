import uuid

def test_complete_patient_journey_via_rest_api(client):
    """
    Test complete patient booking journey via REST API:
    1. Caller recognition by phone -> Create if new
    2. Identify cardiology specialty & choose Dr. Ravi Kumar
    3. Check available slots for date
    4. Check specific slot boundary
    5. Book the appointment
    6. Verify appointment shows up in doctor's booked patient roster
    7. Atomically reschedule to another free slot
    8. Soft cancel with reason
    9. Verify cancelled slot is freed up in availability endpoint
    """
    # 1. Caller recognition
    unique_phone = f"97{uuid.uuid4().int % 100000000:08d}"
    lookup_res = client.get(f"/api/v1/patients/by-phone/{unique_phone}")
    assert lookup_res.status_code == 404

    # Create new patient
    create_pat_res = client.post("/api/v1/patients", json={
        "name": "Ananya Sen",
        "phone": unique_phone,
        "email": "ananya@example.com",
        "age": 28,
        "gender": "Female"
    })
    assert create_pat_res.status_code == 201
    patient_id = create_pat_res.json()["id"]

    # 2. Find Cardiology doctors
    specs = client.get("/api/v1/specialties").json()["items"]
    cardio_spec = next(s for s in specs if s["name"] == "Cardiology")
    docs = client.get(f"/api/v1/doctors?specialty_id={cardio_spec['id']}").json()["items"]
    dr_ravi = next(d for d in docs if "Ravi" in d["name"])
    doctor_id = dr_ravi["id"]

    # 3. Check available slots
    target_date = "2026-09-25"
    avail_res = client.get(f"/api/v1/doctors/{doctor_id}/availability?date={target_date}")
    assert avail_res.status_code == 200
    avail_data = avail_res.json()
    assert avail_data["total_slots"] == 8

    # 4. Check specific slot 09:00
    slot_check = client.get(f"/api/v1/doctors/{doctor_id}/availability/check?date={target_date}&start_time=09:00")
    assert slot_check.status_code == 200
    assert slot_check.json()["available"] is True

    # 5. Book appointment at 09:00
    book_res = client.post("/api/v1/appointments", json={
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": target_date,
        "start_time": "09:00",
        "reason": "Cardiology Consultation"
    })
    assert book_res.status_code == 201
    apt = book_res.json()
    appointment_id = apt["appointment_id"]
    assert apt["status"] == "confirmed"

    # 6. Verify appointment appears in doctor's booked patient list
    doc_apts_res = client.get(f"/api/v1/doctors/{doctor_id}/appointments?date={target_date}")
    assert doc_apts_res.status_code == 200
    booked_names = [a["patient_name"] for a in doc_apts_res.json()["appointments"]]
    assert "Ananya Sen" in booked_names

    # 7. Reschedule to 10:30
    resched_res = client.post(f"/api/v1/appointments/{appointment_id}/reschedule", json={
        "new_date": target_date,
        "new_start_time": "10:30"
    })
    assert resched_res.status_code == 200
    assert resched_res.json()["new_start_time"] == "10:30"

    # 8. Cancel appointment
    cancel_res = client.post(f"/api/v1/appointments/{appointment_id}/cancel", json={
        "reason": "Travel conflict"
    })
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"
    assert cancel_res.json()["cancellation_reason"] == "Travel conflict"

    # 9. Verify slot 10:30 is available again
    final_check = client.get(f"/api/v1/doctors/{doctor_id}/availability/check?date={target_date}&start_time=10:30")
    assert final_check.status_code == 200
    assert final_check.json()["available"] is True
