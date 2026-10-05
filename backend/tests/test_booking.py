import pytest
from datetime import date, time
from sqlalchemy import select
from app.models import Appointment
from app.services.booking_service import book_appointment, get_appointment
from app.services.exceptions import (
    SlotNotAvailableError,
    SlotAlreadyBookedError,
    InvalidSlotError,
    PatientNotFoundError,
    DoctorNotFoundError,
)

def test_successful_booking(sample_doctor, sample_patient, db_session):
    """Booking a valid available slot succeeds and creates a confirmed appointment."""
    target_date = date(2026, 9, 25)
    booking_time = time(9, 0)  # 09:00 is available

    res = book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_date=target_date,
        start_time=booking_time,
        reason="Test consultation booking",
        db=db_session
    )

    try:
        assert res["success"] is True
        assert res["patient_name"] == sample_patient.name
        assert res["doctor_name"] == sample_doctor.name
        assert res["start_time"] == "09:00"
        assert res["end_time"] == "09:30"
        assert res["status"] == "confirmed"

        # Verify get_appointment
        apt_details = get_appointment(res["appointment_id"], db=db_session)
        assert apt_details["appointment_id"] == res["appointment_id"]
        assert apt_details["start_time"] == "09:00"
    finally:
        # Clean up test appointment
        db_session.rollback()
        apt = db_session.scalars(select(Appointment).where(Appointment.id == res["appointment_id"])).first()
        if apt:
            db_session.delete(apt)
            db_session.commit()

def test_booking_occupied_slot_rejected(sample_doctor, sample_patient, db_session):
    """Attempting to book an already occupied slot raises SlotAlreadyBookedError."""
    target_date = date(2026, 9, 25)
    # 10:00 is already booked by Praveen Kumar in seed data
    with pytest.raises(SlotAlreadyBookedError, match="already booked"):
        book_appointment(
            patient_id=sample_patient.id,
            doctor_id=sample_doctor.id,
            appointment_date=target_date,
            start_time=time(10, 0),
            db=db_session
        )

def test_booking_invalid_slot_boundary(sample_doctor, sample_patient, db_session):
    """Attempting to book a misaligned time raises InvalidSlotError."""
    target_date = date(2026, 9, 25)
    with pytest.raises(InvalidSlotError, match="does not align"):
        book_appointment(
            patient_id=sample_patient.id,
            doctor_id=sample_doctor.id,
            appointment_date=target_date,
            start_time=time(10, 15),
            db=db_session
        )

def test_booking_nonexistent_patient_or_doctor(sample_doctor, sample_patient, db_session):
    """Booking raises PatientNotFoundError or DoctorNotFoundError appropriately."""
    target_date = date(2026, 9, 25)
    with pytest.raises(PatientNotFoundError):
        book_appointment(
            patient_id=99999,
            doctor_id=sample_doctor.id,
            appointment_date=target_date,
            start_time=time(9, 30),
            db=db_session
        )

    with pytest.raises(DoctorNotFoundError):
        book_appointment(
            patient_id=sample_patient.id,
            doctor_id=99999,
            appointment_date=target_date,
            start_time=time(9, 30),
            db=db_session
        )
