"""Tests for Voice REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.voice.session import voice_session_store, CallStatus

client = TestClient(app)


def test_incoming_call_form_json_response():
    resp = client.post(
        "/api/v1/voice/incoming",
        data={"CallSid": "call_test_1", "From": "+919876543210"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["call_sid"] == "call_test_1"
    assert "stream/call_test_1" in data["stream_url"]

    # Verify session registered in store
    session = voice_session_store.get("call_test_1")
    assert session is not None
    assert session.phone_number == "+919876543210"


def test_incoming_call_xml_response():
    resp = client.post(
        "/api/v1/voice/incoming",
        data={"CallSid": "call_test_xml", "From": "+919876543210"},
        headers={"Accept": "application/xml"}
    )
    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    assert "<Response>" in resp.text
    assert "<Stream" in resp.text


def test_get_call_session():
    # Setup call
    client.post("/api/v1/voice/incoming", data={"CallSid": "call_get_test", "From": "+919876543210"})
    
    resp = client.get("/api/v1/voice/call_get_test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["call_id"] == "call_get_test"
    assert data["status"] == "incoming"


def test_call_status_callback():
    client.post("/api/v1/voice/incoming", data={"CallSid": "call_status_test", "From": "+919876543210"})

    resp = client.post(
        "/api/v1/voice/status",
        json={"CallSid": "call_status_test", "Status": "completed", "Duration": 45}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["updated_status"] == "completed"

    session = voice_session_store.get("call_status_test")
    assert session.status == CallStatus.COMPLETED


def test_transfer_call_endpoint():
    client.post("/api/v1/voice/incoming", data={"CallSid": "call_transfer_test", "From": "+919876543210"})

    resp = client.post(
        "/api/v1/voice/call_transfer_test/transfer",
        json={"reason": "Emergency escalated by AI"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "transferred"
    assert data["reason"] == "Emergency escalated by AI"

    session = voice_session_store.get("call_transfer_test")
    assert session.transferred is True


def test_end_call_endpoint():
    client.post("/api/v1/voice/incoming", data={"CallSid": "call_end_test", "From": "+919876543210"})

    resp = client.post("/api/v1/voice/call_end_test/end")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "terminated"

    session = voice_session_store.get("call_end_test")
    assert session.status == CallStatus.COMPLETED
