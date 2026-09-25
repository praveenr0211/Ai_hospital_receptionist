import pytest
from datetime import date, time
from sqlalchemy import select
from app.models import Appointment, AppointmentStatus
from app.services.booking_service import book_appointment, cancel_appointment
from app.services.availability_service import check_slot_availability
from app.services.exceptions import (
    AppointmentNotFoundError,
    AppointmentAlreadyCancelledError,
)

def test_cancellation_and_slot_release(sample_doctor, sample_patient, db_session):
    """Cancelling an appointment soft-cancels the record and releases the slot."""
    target_date = date(2026, 9, 25)
    booking_time = time(12, 0)

    # 1. Book slot
    booked = book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_date=target_date,
        start_time=booking_time,
        reason="Checkup to be cancelled",
        db=db_session
    )
    apt_id = booked["appointment_id"]

    try:
        # Verify slot is not available
        check_before = check_slot_availability(sample_doctor.id, target_date, booking_time, db=db_session)
        assert check_before["available"] is False

        # 2. Cancel appointment
        cancel_res = cancel_appointment(apt_id, cancellation_reason="Schedule conflict", db=db_session)
        assert cancel_res["success"] is True
        assert cancel_res["status"] == "cancelled"

        # 3. Verify record still exists in DB with cancelled status (audit preserved)
        apt = db_session.scalars(select(Appointment).where(Appointment.id == apt_id)).first()
        assert apt is not None
        assert apt.status == AppointmentStatus.CANCELLED
        assert apt.cancellation_reason == "Schedule conflict"

        # 4. Verify slot is released and now AVAILABLE
        check_after = check_slot_availability(sample_doctor.id, target_date, booking_time, db=db_session)
        assert check_after["available"] is True

        # 5. Attempting to cancel again raises AppointmentAlreadyCancelledError
        with pytest.raises(AppointmentAlreadyCancelledError):
            cancel_appointment(apt_id, db=db_session)

    finally:
        # Cleanup
        db_session.rollback()
        apt = db_session.scalars(select(Appointment).where(Appointment.id == apt_id)).first()
        if apt:
            db_session.delete(apt)
            db_session.commit()

def test_cancel_nonexistent_appointment(db_session):
    """Cancelling a nonexistent appointment raises AppointmentNotFoundError."""
    with pytest.raises(AppointmentNotFoundError):
        cancel_appointment(99999, db=db_session)
