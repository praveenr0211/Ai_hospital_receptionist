def test_dashboard_summary(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_doctors" in data
    assert "active_doctors" in data
    assert "total_patients" in data
    assert "appointments_today" in data
    assert "confirmed_appointments" in data
    assert "cancelled_appointments" in data
    assert "calls_today" in data

def test_dashboard_doctors(client):
    response = client.get("/api/v1/dashboard/doctors")
    assert response.status_code == 200
    data = response.json()
    assert "doctors" in data
    assert len(data["doctors"]) >= 1
    first_doc = data["doctors"][0]
    assert "doctor_name" in first_doc
    assert "appointments_today" in first_doc
    assert "upcoming" in first_doc
