def test_get_doctor_availability(client):
    list_res = client.get("/api/v1/doctors")
    doc_id = list_res.json()["items"][0]["id"]

    response = client.get(f"/api/v1/doctors/{doc_id}/availability?date=2026-09-25")
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == doc_id
    assert "slots" in data
    assert "total_slots" in data
    assert "available_count" in data
    assert len(data["slots"]) == data["total_slots"]

def test_check_slot_availability_free_and_occupied(client):
    # Dr. Ravi Kumar has 10:00 booked in seed data, 09:30 free
    docs = client.get("/api/v1/doctors").json()["items"]
    dr_ravi = next(d for d in docs if "Ravi" in d["name"])

    # Check free slot
    free_res = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability/check?date=2026-09-25&start_time=09:30")
    assert free_res.status_code == 200
    assert free_res.json()["available"] is True

    # Check occupied slot
    occ_res = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability/check?date=2026-09-25&start_time=10:00")
    assert occ_res.status_code == 200
    assert occ_res.json()["available"] is False

def test_check_misaligned_slot_rejected(client):
    docs = client.get("/api/v1/doctors").json()["items"]
    dr_ravi = next(d for d in docs if "Ravi" in d["name"])

    response = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability/check?date=2026-09-25&start_time=10:15")
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_SLOT"

def test_find_alternative_slots(client):
    docs = client.get("/api/v1/doctors").json()["items"]
    dr_ravi = next(d for d in docs if "Ravi" in d["name"])

    response = client.get(f"/api/v1/doctors/{dr_ravi['id']}/availability/alternatives?date=2026-09-25&requested_time=10:00&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["requested_time"] == "10:00"
    assert data["available"] is False
    assert len(data["alternatives"]) >= 1
