import pytest
from app.agent.graph import agent
from app.agent.state import session_store
from app.agent.policies import parse_user_confirmation, is_tool_allowed

def test_confirmation_parsing():
    assert parse_user_confirmation("Yes please") is True
    assert parse_user_confirmation("Confirm it") is True
    assert parse_user_confirmation("Go ahead") is True
    assert parse_user_confirmation("No, I don't want that") is False
    assert parse_user_confirmation("Cancel that") is False
    assert parse_user_confirmation("Maybe tomorrow") is None

def test_tool_permission_boundaries():
    # Booking tool is ONLY allowed in BOOK_APPOINTMENT state
    assert is_tool_allowed("BOOK_APPOINTMENT", "book_appointment_tool") is True
    assert is_tool_allowed("WAIT_CONFIRMATION", "book_appointment_tool") is False
    assert is_tool_allowed("OFFER_SLOTS", "book_appointment_tool") is False
    assert is_tool_allowed("GREETING", "book_appointment_tool") is False
    assert is_tool_allowed("EMERGENCY_HANDLING", "book_appointment_tool") is False

def test_booking_never_executed_without_confirmation(db_session, sample_patient, sample_doctor):
    session_id = "test_no_confirm_sess"
    session_store.clear(session_id)

    state = session_store.get_or_create(session_id)
    state.current_state = "WAIT_CONFIRMATION"
    state.doctor_id = sample_doctor.id
    state.doctor_name = sample_doctor.name
    state.appointment_date = "2026-09-25"
    state.requested_time = "10:00"
    state.awaiting_confirmation = True
    session_store.save(state)

    # User says something ambiguous or questions the time
    resp = agent.process_message(
        session_id=session_id,
        message="10:00 sounds okay I guess, is that the only time?",
        db=db_session,
    )

    # Booking must NOT have occurred
    assert resp.appointment_id is None
    assert resp.action_required == "CONFIRMATION_REQUIRED"

def test_user_rejection_resets_selected_slot(db_session, sample_doctor):
    session_id = "test_reject_sess"
    session_store.clear(session_id)

    state = session_store.get_or_create(session_id)
    state.current_state = "WAIT_CONFIRMATION"
    state.doctor_id = sample_doctor.id
    state.doctor_name = sample_doctor.name
    state.requested_time = "10:00"
    state.awaiting_confirmation = True
    session_store.save(state)

    resp = agent.process_message(
        session_id=session_id,
        message="No, don't book that time.",
        db=db_session,
    )

    assert resp.appointment_id is None
    updated = session_store.get_or_create(session_id)
    assert updated.awaiting_confirmation is False
    assert updated.selected_slot is None
