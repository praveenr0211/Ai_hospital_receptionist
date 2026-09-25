import uuid

def test_get_patient_by_phone(client):
    response = client.get("/api/v1/patients/by-phone/9876500001")
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "9876500001"
    assert data["name"] == "Praveen Kumar"

def test_get_patient_by_phone_not_found(client):
    response = client.get("/api/v1/patients/by-phone/0000000000")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "PATIENT_NOT_FOUND"

def test_create_patient_success(client):
    unique_phone = f"99{uuid.uuid4().int % 100000000:08d}"
    payload = {
        "name": "Test Patient",
        "phone": unique_phone,
        "email": "test@example.com",
        "age": 30,
        "gender": "Female"
    }
    response = client.post("/api/v1/patients", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["phone"] == unique_phone
    assert data["name"] == "Test Patient"
    assert "id" in data

def test_create_duplicate_patient_rejected(client):
    payload = {
        "name": "Duplicate Patient",
        "phone": "9876500001",
        "email": "praveen@example.com"
    }
    response = client.post("/api/v1/patients", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "BOOKING_ERROR"

def test_get_patient_appointments(client):
    response = client.get("/api/v1/patients/1/appointments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
