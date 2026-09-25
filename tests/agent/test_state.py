import pytest
from app.agent.state import ReceptionistState, SessionStore

def test_receptionist_state_defaults():
    state = ReceptionistState(session_id="test_sess_1")
    assert state.session_id == "test_sess_1"
    assert state.current_state == "GREETING"
    assert state.patient_id is None
    assert state.awaiting_confirmation is False
    assert state.emergency_detected is False
    assert state.conversation_history == []

def test_session_store_isolation():
    store = SessionStore()
    s1 = store.get_or_create("session_a", phone_number="9876500001")
    s2 = store.get_or_create("session_b", phone_number="9876500002")

    s1.current_state = "COLLECT_SYMPTOMS"
    s1.patient_id = 10
    store.save(s1)

    # Verify session b remains untouched
    assert store.get_or_create("session_b").current_state == "GREETING"
    assert store.get_or_create("session_b").patient_id is None
    assert store.get_or_create("session_a").patient_id == 10
    assert store.get_or_create("session_a").current_state == "COLLECT_SYMPTOMS"

def test_session_store_clear():
    store = SessionStore()
    s1 = store.get_or_create("session_temp")
    s1.patient_name = "Alice"
    store.save(s1)

    assert store.get_or_create("session_temp").patient_name == "Alice"
    store.clear("session_temp")
    # Next retrieval gives a fresh state
    fresh = store.get_or_create("session_temp")
    assert fresh.patient_name is None
