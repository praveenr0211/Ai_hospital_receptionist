import pytest
from sqlalchemy import delete
from app.models.appointment import Appointment
from app.agent.graph import agent
from app.agent.state import session_store

def test_complete_booking_conversation_flow(db_session, sample_patient):
    session_id = "test_booking_flow_full"
    session_store.clear(session_id)
    created_apt_id = None

    try:
        # Turn 1: Patient expresses cardiology symptoms on 2026-09-25
        resp1 = agent.process_message(
            session_id=session_id,
            message="I have mild heart palpitations and flutter since yesterday, can I see a doctor on 2026-09-25?",
            phone_number=sample_patient.phone,
            db=db_session,
        )

        assert resp1.state in {"OFFER_SLOTS", "CHECK_AVAILABILITY"}
        assert "Cardiology" in resp1.message or "Dr." in resp1.message
        assert resp1.action_required == "USER_INPUT"

        state = session_store.get_or_create(session_id)
        assert len(state.available_slots) > 0
        chosen_slot = state.available_slots[0]["start_time"]

        # Turn 2: Patient selects the first available slot
        resp2 = agent.process_message(
            session_id=session_id,
            message=f"{chosen_slot} please",
            phone_number=sample_patient.phone,
            db=db_session,
        )

        assert resp2.state == "WAIT_CONFIRMATION"
        assert resp2.action_required == "CONFIRMATION_REQUIRED"
        assert "confirm" in resp2.message.lower()

        # Turn 3: Patient explicitly confirms booking
        resp3 = agent.process_message(
            session_id=session_id,
            message="Yes, please book it",
            phone_number=sample_patient.phone,
            db=db_session,
        )

        assert resp3.state == "BOOKING_COMPLETE"
        assert resp3.action_required == "COMPLETED"
        assert resp3.appointment_id is not None
        assert "confirmed" in resp3.message.lower()
        created_apt_id = resp3.appointment_id

        # Final state assertions
        final_state = session_store.get_or_create(session_id)
        assert final_state.appointment_id == resp3.appointment_id
        assert final_state.awaiting_confirmation is False
    finally:
        db_session.rollback()
        if created_apt_id:
            db_session.execute(delete(Appointment).where(Appointment.id == created_apt_id))
            db_session.commit()
