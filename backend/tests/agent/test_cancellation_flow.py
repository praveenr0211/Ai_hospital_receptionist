import pytest
from datetime import date, time
from app.services.booking_service import book_appointment
from app.agent.graph import agent
from app.agent.state import session_store

from sqlalchemy import delete
from app.models.appointment import Appointment
from app.agent.tools.availability_tools import check_doctor_availability

def test_cancellation_flow(db_session, sample_patient, sample_doctor):
    # Setup: Create an appointment for patient at an available slot
    avail = check_doctor_availability(db_session, sample_doctor.id, "2026-09-25")
    assert avail.available_slots, "Doctor must have open slots"
    slot_str = avail.available_slots[0].start_time
    h, m = map(int, slot_str.split(":"))

    apt = book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_date=date(2026, 9, 25),
        start_time=time(h, m),
        reason="Follow up",
        db=db_session,
    )
    db_session.commit()

    try:
        session_id = "test_cancel_sess_1"
        session_store.clear(session_id)

        # Turn 1: Patient asks to cancel
        resp1 = agent.process_message(
            session_id=session_id,
            message="I want to cancel my appointment",
            phone_number=sample_patient.phone,
            db=db_session,
        )

        assert resp1.state == "WAIT_CONFIRMATION"
        assert resp1.action_required == "CONFIRMATION_REQUIRED"
        assert "cancel" in resp1.message.lower()

        # Turn 2: Patient confirms cancellation
        resp2 = agent.process_message(
            session_id=session_id,
            message="Yes, please cancel it",
            phone_number=sample_patient.phone,
            db=db_session,
        )

        assert resp2.state == "END"
        assert resp2.action_required == "COMPLETED"
        assert "cancelled" in resp2.message.lower()
    finally:
        db_session.rollback()
        db_session.execute(delete(Appointment).where(Appointment.id == apt["appointment_id"]))
        db_session.commit()
