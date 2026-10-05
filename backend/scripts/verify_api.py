import sys
import uuid
from fastapi.testclient import TestClient
from app.main import app

# Ensure clean UTF-8 console output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_api_verification():
    print("=" * 65)
    print("PHASE 3 — REST API LAYER VERIFICATION")
    print("=" * 65)

    client = TestClient(app)

    # -------------------------------------------------------------
    # [1] Health & Connectivity Check
    # -------------------------------------------------------------
    print("\n[1] Health Check Endpoints")
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_db = client.get("/api/v1/health/db")
    assert res_db.status_code == 200
    assert res_db.json()["database"] == "hospital_receptionist"
    print("    [PASS] /api/v1/health and /api/v1/health/db operational")

    # -------------------------------------------------------------
    # [2] Specialties API
    # -------------------------------------------------------------
    print("\n[2] Specialties Endpoints")
    res_specs = client.get("/api/v1/specialties")
    assert res_specs.status_code == 200
    specs_data = res_specs.json()
    assert specs_data["total"] >= 5
    cardio = next(s for s in specs_data["items"] if s["name"] == "Cardiology")
    print(f"    [PASS] /api/v1/specialties returned {specs_data['total']} specialties (Cardiology ID: {cardio['id']})")

    res_spec_detail = client.get(f"/api/v1/specialties/{cardio['id']}")
    assert res_spec_detail.status_code == 200
    assert res_spec_detail.json()["name"] == "Cardiology"
    print(f"    [PASS] /api/v1/specialties/{cardio['id']} returned '{cardio['name']}'")

    # -------------------------------------------------------------
    # [3] Doctors API
    # -------------------------------------------------------------
    print("\n[3] Doctors Endpoints")
    res_docs = client.get(f"/api/v1/doctors?specialty_id={cardio['id']}&status=active")
    assert res_docs.status_code == 200
    docs_data = res_docs.json()
    dr_ravi = next(d for d in docs_data["items"] if "Ravi" in d["name"])
    print(f"    [PASS] /api/v1/doctors filtered by specialty: found {dr_ravi['name']} (#{dr_ravi['id']})")

    res_doc_detail = client.get(f"/api/v1/doctors/{dr_ravi['id']}")
    assert res_doc_detail.status_code == 200
    assert res_doc_detail.json()["specialty"]["name"] == "Cardiology"
    print(f"    [PASS] /api/v1/doctors/{dr_ravi['id']} returned doctor profile with specialty")

    res_doc_sched = client.get(f"/api/v1/doctors/{dr_ravi['id']}/schedules?date=2026-09-25")
    assert res_doc_sched.status_code == 200
    assert len(res_doc_sched.json()["schedules"]) >= 1
    print(f"    [PASS] /api/v1/doctors/{dr_ravi['id']}/schedules returned shift intervals")

    # -------------------------------------------------------------
    # [4] Patients API
    # -------------------------------------------------------------
    print("\n[4] Patients Endpoints")
    res_patient_lookup = client.get("/api/v1/patients/by-phone/9876500001")
    assert res_patient_lookup.status_code == 200
    assert res_patient_lookup.json()["name"] == "Praveen Kumar"
    print("    [PASS] /api/v1/patients/by-phone/9876500001 recognized patient 'Praveen Kumar'")

    test_phone = f"95{uuid.uuid4().int % 100000000:08d}"
    res_create_pat = client.post("/api/v1/patients", json={
        "name": "Phase 3 Test Patient",
        "phone": test_phone,
        "email": "phase3@test.com",
        "age": 34,
        "gender": "Male"
    })
    assert res_create_pat.status_code == 201
    new_patient_id = res_create_pat.json()["id"]
    print(f"    [PASS] /api/v1/patients created new patient #{new_patient_id} with phone {test_phone}")

    # -------------------------------------------------------------
    # [5] Availability API
    # -------------------------------------------------------------
    print("\n[5] Availability Endpoints")
    target_date = "2026-09-25"
    res_avail = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability?date={target_date}")
    assert res_avail.status_code == 200
    avail_data = res_avail.json()
    assert avail_data["total_slots"] == 8
    print(f"    [PASS] /api/v1/doctors/{dr_ravi['id']}/availability: {avail_data['available_count']}/{avail_data['total_slots']} slots available")

    res_slot_free = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability/check?date={target_date}&start_time=09:30")
    assert res_slot_free.status_code == 200
    assert res_slot_free.json()["available"] is True
    print("    [PASS] /api/v1/doctors/{id}/availability/check verified free slot at 09:30")

    res_slot_occ = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability/check?date={target_date}&start_time=10:00")
    assert res_slot_occ.status_code == 200
    assert res_slot_occ.json()["available"] is False
    print("    [PASS] /api/v1/doctors/{id}/availability/check rejected occupied slot at 10:00")

    res_alts = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability/alternatives?date={target_date}&requested_time=10:00&limit=3")
    assert res_alts.status_code == 200
    alts_data = res_alts.json()
    assert len(alts_data["alternatives"]) >= 1
    print(f"    [PASS] /api/v1/doctors/{dr_ravi['id']}/availability/alternatives returned nearest: {alts_data['alternatives']}")

    # -------------------------------------------------------------
    # [6] Appointments Lifecycle API
    # -------------------------------------------------------------
    print("\n[6] Appointments API Lifecycle")
    # 6.1 Book
    book_payload = {
        "patient_id": new_patient_id,
        "doctor_id": dr_ravi["id"],
        "appointment_date": target_date,
        "start_time": "09:00",
        "reason": "Phase 3 API E2E Booking"
    }
    res_book = client.post("/api/v1/appointments", json=book_payload)
    assert res_book.status_code == 201
    apt_id = res_book.json()["appointment_id"]
    print(f"    [PASS] POST /api/v1/appointments booked appointment #{apt_id} (09:00)")

    # 6.2 Double booking rejection
    res_dup = client.post("/api/v1/appointments", json=book_payload)
    assert res_dup.status_code == 409
    assert res_dup.json()["error"]["code"] == "SLOT_ALREADY_BOOKED"
    print(f"    [PASS] POST /api/v1/appointments rejected duplicate booking with 409 {res_dup.json()['error']['code']}")

    # 6.3 Reschedule
    res_resched = client.post(f"/api/v1/appointments/{apt_id}/reschedule", json={
        "new_date": target_date,
        "new_start_time": "10:30"
    })
    assert res_resched.status_code == 200
    assert res_resched.json()["new_start_time"] == "10:30"
    print(f"    [PASS] POST /api/v1/appointments/{apt_id}/reschedule rescheduled to 10:30")

    # 6.4 Cancel with reason
    res_cancel = client.post(f"/api/v1/appointments/{apt_id}/cancel", json={
        "reason": "Patient requested cancellation via API verification"
    })
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "cancelled"
    assert res_cancel.json()["cancellation_reason"] == "Patient requested cancellation via API verification"
    print(f"    [PASS] POST /api/v1/appointments/{apt_id}/cancel cancelled appointment and stored reason")

    # -------------------------------------------------------------
    # [7] Calls API
    # -------------------------------------------------------------
    print("\n[7] Calls Endpoints")
    res_call_create = client.post("/api/v1/calls", json={
        "patient_id": new_patient_id,
        "phone_number": test_phone,
        "intent": "appointment_booking",
        "specialty_detected": "Cardiology",
        "duration_seconds": 150,
        "outcome": "appointment_booked",
        "escalated": False
    })
    assert res_call_create.status_code == 201
    call_id = res_call_create.json()["id"]
    print(f"    [PASS] POST /api/v1/calls logged call record #{call_id}")

    res_call_list = client.get("/api/v1/calls")
    assert res_call_list.status_code == 200
    assert res_call_list.json()["total"] >= 1
    print(f"    [PASS] GET /api/v1/calls retrieved {res_call_list.json()['total']} call records")

    # -------------------------------------------------------------
    # [8] Dashboard Endpoints
    # -------------------------------------------------------------
    print("\n[8] Dashboard Endpoints")
    res_dash_sum = client.get("/api/v1/dashboard/summary")
    assert res_dash_sum.status_code == 200
    sum_data = res_dash_sum.json()
    assert sum_data["total_doctors"] >= 1
    assert sum_data["total_patients"] >= 1
    print(f"    [PASS] GET /api/v1/dashboard/summary: {sum_data['total_doctors']} doctors, {sum_data['total_patients']} patients, {sum_data['calls_today']} calls")

    res_dash_docs = client.get("/api/v1/dashboard/doctors")
    assert res_dash_docs.status_code == 200
    docs_perf = res_dash_docs.json()["doctors"]
    assert len(docs_perf) >= 1
    print(f"    [PASS] GET /api/v1/dashboard/doctors: performance tracking available for {len(docs_perf)} doctors")

    # -------------------------------------------------------------
    # [9] Standardized Error Response Validation
    # -------------------------------------------------------------
    print("\n[9] Standard Error Envelope Validation")
    # 9.1 404 DOCTOR_NOT_FOUND
    err_404 = client.get("/api/v1/doctors/999999")
    assert err_404.status_code == 404
    assert err_404.json()["error"]["code"] == "DOCTOR_NOT_FOUND"

    # 9.2 400 INVALID_SLOT
    err_400 = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability/check?date={target_date}&start_time=10:15")
    assert err_400.status_code == 400
    assert err_400.json()["error"]["code"] == "INVALID_SLOT"

    # 9.3 422 VALIDATION_ERROR
    err_422 = client.post("/api/v1/patients", json={"name": ""})
    assert err_422.status_code == 422
    assert err_422.json()["error"]["code"] == "VALIDATION_ERROR"
    print("    [PASS] Uniform error envelope verified across 400, 404, 409, and 422 status codes")

    print("\n" + "=" * 65)
    print("ALL 9 PHASE 3 REST API MODULES VERIFIED AND FULLY OPERATIONAL!")
    print("=" * 65)


if __name__ == "__main__":
    run_api_verification()
