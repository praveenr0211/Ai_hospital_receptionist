import pytest
from datetime import date, time
from sqlalchemy import select
from app.models import Appointment
from app.services.booking_service import (
    book_appointment,
    reschedule_appointment,
    cancel_appointment,
)
from app.services.availability_service import check_slot_availability
from app.services.exceptions import (
    SlotNotAvailableError,
    BookingError,
    AppointmentNotFoundError,
)

def test_atomic_rescheduling_success(sample_doctor, sample_patient, db_session):
    """Rescheduling to a free slot moves the appointment and releases the old slot."""
    target_date = date(2026, 9, 25)
    initial_time = time(9, 30)
    new_time = time(10, 30)

    # 1. Book initial slot
    booked = book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_date=target_date,
        start_time=initial_time,
        reason="Initial booking for reschedule test",
        db=db_session
    )
    apt_id = booked["appointment_id"]

    try:
        # 2. Reschedule to free slot (10:30)
        resched_res = reschedule_appointment(apt_id, target_date, new_time, db=db_session)
        assert resched_res["success"] is True
        assert resched_res["previous_time"] == "09:30"
        assert resched_res["new_start_time"] == "10:30"

        # 3. Old slot 09:30 is now AVAILABLE
        check_old = check_slot_availability(sample_doctor.id, target_date, initial_time, db=db_session)
        assert check_old["available"] is True

        # 4. New slot 10:30 is now BOOKED
        check_new = check_slot_availability(sample_doctor.id, target_date, new_time, db=db_session)
        assert check_new["available"] is False

    finally:
        db_session.rollback()
        apt = db_session.scalars(select(Appointment).where(Appointment.id == apt_id)).first()
        if apt:
            db_session.delete(apt)
            db_session.commit()

def test_atomic_rescheduling_failure_preserves_original(sample_doctor, sample_patient, db_session):
    """If target slot is occupied, reschedule fails and original booking remains intact."""
    target_date = date(2026, 9, 25)
    initial_time = time(9, 30)
    occupied_time = time(11, 30)  # Rohan Sharma booked 11:30 in seed data

    # 1. Book initial slot
    booked = book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_date=target_date,
        start_time=initial_time,
        reason="Reschedule failure safety test",
        db=db_session
    )
    apt_id = booked["appointment_id"]

    try:
        # 2. Attempt reschedule to occupied slot
        with pytest.raises(SlotNotAvailableError):
            reschedule_appointment(apt_id, target_date, occupied_time, db=db_session)

        # 3. Original appointment must still exist at 09:30
        apt = db_session.scalars(select(Appointment).where(Appointment.id == apt_id)).first()
        assert apt is not None
        assert apt.start_time == initial_time
        assert apt.appointment_date == target_date

        # 4. Initial slot 09:30 remains BOOKED
        check_orig = check_slot_availability(sample_doctor.id, target_date, initial_time, db=db_session)
        assert check_orig["available"] is False

    finally:
        db_session.rollback()
        apt = db_session.scalars(select(Appointment).where(Appointment.id == apt_id)).first()
        if apt:
            db_session.delete(apt)
            db_session.commit()

def test_reschedule_cancelled_appointment(sample_doctor, sample_patient, db_session):
    """Cannot reschedule a cancelled appointment."""
    target_date = date(2026, 9, 25)
    booked = book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_date=target_date,
        start_time=time(9, 30),
        db=db_session
    )
    apt_id = booked["appointment_id"]
    cancel_appointment(apt_id, db=db_session)

    try:
        with pytest.raises(BookingError, match="Cannot reschedule cancelled"):
            reschedule_appointment(apt_id, target_date, time(10, 30), db=db_session)
    finally:
        db_session.rollback()
        apt = db_session.scalars(select(Appointment).where(Appointment.id == apt_id)).first()
        if apt:
            db_session.delete(apt)
            db_session.commit()
