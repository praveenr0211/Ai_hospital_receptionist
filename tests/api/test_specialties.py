def test_list_specialties(client):
    response = client.get("/api/v1/specialties")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 5
    names = [s["name"] for s in data["items"]]
    assert "Cardiology" in names

def test_get_specialty_by_id(client):
    # Fetch list first to get valid id
    list_res = client.get("/api/v1/specialties")
    first_item = list_res.json()["items"][0]

    response = client.get(f"/api/v1/specialties/{first_item['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == first_item["id"]
    assert data["name"] == first_item["name"]

def test_get_specialty_not_found(client):
    response = client.get("/api/v1/specialties/999999")
    assert response.status_code == 404
