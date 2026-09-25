import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_api_agent_greeting_and_chat(client):
    session_id = "test_api_agent_sess"
    
    # 1. Reset session first
    reset_resp = client.post(f"/api/v1/agent/reset?session_id={session_id}")
    assert reset_resp.status_code == 200

    # 2. First greeting turn
    payload1 = {
        "session_id": session_id,
        "message": "Hello, I need to make an appointment",
        "phone_number": "9876500001",
    }
    resp1 = client.post("/api/v1/agent/chat", json=payload1)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["session_id"] == session_id
    assert "symptoms" in data1["message"].lower() or "help" in data1["message"].lower()
    assert data1["action_required"] == "USER_INPUT"

    # 3. Inspect state endpoint
    state_resp = client.get(f"/api/v1/agent/state/{session_id}")
    assert state_resp.status_code == 200
    state_data = state_resp.json()
    assert state_data["session_id"] == session_id
    assert len(state_data["conversation_history"]) >= 2

def test_api_agent_emergency_handling(client):
    session_id = "test_api_emergency"
    payload = {
        "session_id": session_id,
        "message": "I'm gasping for air and have crushing chest pain",
    }
    resp = client.post("/api/v1/agent/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["escalation_required"] is True
    assert data["action_required"] == "HUMAN_ESCALATION"
    assert "emergency" in data["message"].lower()

def test_api_agent_human_request(client):
    session_id = "test_api_human"
    payload = {
        "session_id": session_id,
        "message": "Can I please speak with a human receptionist?",
    }
    resp = client.post("/api/v1/agent/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["escalation_required"] is True
    assert "transferring" in data["message"].lower() or "staff" in data["message"].lower()
