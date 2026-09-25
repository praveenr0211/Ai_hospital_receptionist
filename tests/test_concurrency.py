import pytest
from datetime import date, time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Appointment
from app.services.booking_service import book_appointment
from app.services.exceptions import SlotAlreadyBookedError, SlotNotAvailableError

def test_concurrent_booking_collision(sample_doctor, sample_patient, second_patient):
    """
    When two concurrent requests attempt to book the exact same slot simultaneously,
    exactly one must succeed and the other must be rejected with SlotAlreadyBookedError or SlotNotAvailableError.
    """
    target_date = date(2026, 9, 25)
    collision_time = time(12, 30)  # 12:30 is available

    results = []
    errors = []

    def attempt_booking(pat_id: int, note: str):
        thread_db = SessionLocal()
        try:
            with thread_db.begin():
                res = book_appointment(
                    patient_id=pat_id,
                    doctor_id=sample_doctor.id,
                    appointment_date=target_date,
                    start_time=collision_time,
                    reason=f"Concurrent booking test: {note}",
                    db=thread_db
                )
            results.append(res)
        except (SlotAlreadyBookedError, SlotNotAvailableError) as e:
            errors.append(e)
        finally:
            thread_db.close()

    # Launch both booking attempts simultaneously across 2 threads
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(attempt_booking, sample_patient.id, "Caller 1")
        f2 = executor.submit(attempt_booking, second_patient.id, "Caller 2")
        f1.result()
        f2.result()

    clean_db = SessionLocal()
    try:
        # Exactly one succeeded
        assert len(results) == 1, f"Expected 1 success, got {len(results)}"
        # Exactly one was rejected
        assert len(errors) == 1, f"Expected 1 error, got {len(errors)}"

        # Verify database has exactly 1 active appointment for that slot
        from app.models.enums import AppointmentStatus
        apts = clean_db.scalars(
            select(Appointment)
            .where(
                Appointment.doctor_id == sample_doctor.id,
                Appointment.appointment_date == target_date,
                Appointment.start_time == collision_time,
                Appointment.status != AppointmentStatus.CANCELLED
            )
        ).all()
        assert len(apts) == 1, f"Expected 1 active appointment in DB, found {len(apts)}"

    finally:
        # Cleanup
        for r in results:
            apt = clean_db.scalars(select(Appointment).where(Appointment.id == r["appointment_id"])).first()
            if apt:
                clean_db.delete(apt)
        clean_db.commit()
        clean_db.close()
