def test_list_doctors(client):
    response = client.get("/api/v1/doctors")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    assert data["page"] == 1

def test_list_doctors_filter_status(client):
    response = client.get("/api/v1/doctors?status=active")
    assert response.status_code == 200
    data = response.json()
    for doc in data["items"]:
        assert doc["status"] == "active"

def test_get_doctor_detail(client):
    list_res = client.get("/api/v1/doctors")
    doc_id = list_res.json()["items"][0]["id"]

    response = client.get(f"/api/v1/doctors/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert "specialty" in data

def test_get_doctor_not_found(client):
    response = client.get("/api/v1/doctors/999999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "DOCTOR_NOT_FOUND"

def test_get_doctor_schedules(client):
    list_res = client.get("/api/v1/doctors")
    doc_id = list_res.json()["items"][0]["id"]

    response = client.get(f"/api/v1/doctors/{doc_id}/schedules?date=2026-09-25")
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == doc_id
    assert "schedules" in data
    assert len(data["schedules"]) >= 1

def test_get_doctor_booked_appointments(client):
    list_res = client.get("/api/v1/doctors")
    doc_id = list_res.json()["items"][0]["id"]

    response = client.get(f"/api/v1/doctors/{doc_id}/appointments?date=2026-09-25")
    assert response.status_code == 200
    data = response.json()
    assert "appointments" in data
    assert "total" in data
