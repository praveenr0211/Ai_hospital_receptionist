import pytest
from datetime import date, time
from app.services.booking_service import book_appointment
from app.agent.graph import agent
from app.agent.state import session_store

from sqlalchemy import delete
from app.models.appointment import Appointment
from app.agent.tools.availability_tools import check_doctor_availability

def test_race_condition_slot_already_booked(db_session, sample_patient, second_patient, sample_doctor):
    session_id = "test_race_condition_sess"
    session_store.clear(session_id)

    # Find an open slot for sample_doctor
    avail = check_doctor_availability(db_session, sample_doctor.id, "2026-09-25")
    assert avail.available_slots, "Doctor must have open slots"
    slot_str = avail.available_slots[0].start_time
    h, m = map(int, slot_str.split(":"))

    # Initialize state as if patient selected that slot
    state = session_store.get_or_create(session_id)
    state.current_state = "WAIT_CONFIRMATION"
    state.patient_id = sample_patient.id
    state.patient_phone = sample_patient.phone
    state.doctor_id = sample_doctor.id
    state.doctor_name = sample_doctor.name
    state.appointment_date = "2026-09-25"
    state.requested_time = slot_str
    state.selected_slot = {"start_time": slot_str, "end_time": f"{h:02d}:{m+30:02d}"}
    state.awaiting_confirmation = True
    session_store.save(state)

    # Simulate another patient booking that exact slot right before confirmation!
    other_apt = book_appointment(
        patient_id=second_patient.id,
        doctor_id=sample_doctor.id,
        appointment_date=date(2026, 9, 25),
        start_time=time(h, m),
        reason="Other patient booked first",
        db=db_session,
    )
    db_session.commit()

    try:
        # Patient sends confirmation
        resp = agent.process_message(
            session_id=session_id,
            message="Yes, please book it now",
            db=db_session,
        )

        # Agent should NOT claim booking succeeded
        assert resp.appointment_id is None
        assert resp.state == "OFFER_SLOTS"
        assert "booked by another patient" in resp.message.lower() or "available" in resp.message.lower()
    finally:
        db_session.rollback()
        db_session.execute(delete(Appointment).where(Appointment.id == other_apt["appointment_id"]))
        db_session.commit()

def test_requesting_unavailable_slot_presents_alternatives(db_session, sample_patient):
    session_id = "test_unavail_slot_sess"
    session_store.clear(session_id)

    # Turn 1: Patient starts booking Cardiology with an unavailable time (e.g. 08:00 AM before doctor shift starts at 09:00)
    resp1 = agent.process_message(
        session_id=session_id,
        message="I have mild heart flutter, can I see a cardiologist on 2026-09-25 at 08:00 AM?",
        phone_number=sample_patient.phone,
        db=db_session,
    )

    # Agent should recognize 08:00 is not available and offer alternatives
    assert resp1.appointment_id is None
    assert "not available" in resp1.message.lower()
