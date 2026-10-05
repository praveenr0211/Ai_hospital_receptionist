import pytest
from app.agent.graph import agent
from app.agent.state import session_store

def test_emergency_symptoms_block_booking(db_session, sample_patient):
    session_id = "test_emergency_sess_1"
    session_store.clear(session_id)

    # Turn 1: Patient reports emergency symptoms
    resp = agent.process_message(
        session_id=session_id,
        message="I'm having severe crushing chest pain and I can't breathe",
        phone_number=sample_patient.phone,
        db=db_session,
    )

    assert resp.escalation_required is True
    assert resp.appointment_id is None
    assert resp.action_required == "HUMAN_ESCALATION"
    assert "emergency" in resp.message.lower()

    # State check: emergency_detected must be True
    state = session_store.get_or_create(session_id)
    assert state.emergency_detected is True
    assert state.escalation_required is True
    assert state.doctor_id is None
    assert state.selected_slot is None
