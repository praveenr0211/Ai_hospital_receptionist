from datetime import date, time, datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import (
    Patient,
    Doctor,
    DoctorSchedule,
    Appointment,
    AppointmentStatus,
)
from app.services.exceptions import (
    PatientNotFoundError,
    DoctorNotFoundError,
    DoctorInactiveError,
    SlotNotAvailableError,
    SlotAlreadyBookedError,
    AppointmentNotFoundError,
    AppointmentAlreadyCancelledError,
    BookingError,
)
from app.services.availability_service import check_slot_availability


def get_appointment(appointment_id: int, db: Session | None = None) -> dict[str, Any]:
    """Retrieve details for a single appointment."""
    is_local_session = False
    if db is None:
        db = SessionLocal()
        is_local_session = True

    try:
        apt = db.scalars(select(Appointment).where(Appointment.id == appointment_id)).first()
        if not apt:
            raise AppointmentNotFoundError(f"Appointment with ID {appointment_id} not found.")

        return {
            "appointment_id": apt.id,
            "patient_id": apt.patient_id,
            "patient_name": apt.patient.name,
            "doctor_id": apt.doctor_id,
            "doctor_name": apt.doctor.name,
            "specialty": apt.doctor.specialty.name if apt.doctor.specialty else None,
            "date": apt.appointment_date.isoformat(),
            "start_time": apt.start_time.strftime("%H:%M"),
            "end_time": apt.end_time.strftime("%H:%M"),
            "status": apt.status.value,
            "reason": apt.reason,
            "cancellation_reason": apt.cancellation_reason
        }
    finally:
        if is_local_session:
            db.close()


def book_appointment(
    patient_id: int,
    doctor_id: int,
    appointment_date: date,
    start_time: time,
    reason: str | None = None,
    status: AppointmentStatus = AppointmentStatus.CONFIRMED,
    db: Session | None = None
) -> dict[str, Any]:
    """
    Safely book an appointment with transactional availability verification,
    schedule row locking, and database-level double-booking protection.
    
    Session ownership:
    - If `db` is None, this service creates, commits, and closes the session.
    - If `db` is supplied by the caller, changes are flushed and the caller
      retains ownership of the transaction commit/rollback.
    """
    is_local_session = False
    if db is None:
        db = SessionLocal()
        is_local_session = True

    try:
        # Validate patient exists
        patient = db.scalars(select(Patient).where(Patient.id == patient_id)).first()
        if not patient:
            raise PatientNotFoundError(f"Patient with ID {patient_id} does not exist.")

        # Validate doctor exists and is active
        doctor = db.scalars(select(Doctor).where(Doctor.id == doctor_id)).first()
        if not doctor:
            raise DoctorNotFoundError(f"Doctor with ID {doctor_id} does not exist.")
        if doctor.status != "active":
            raise DoctorInactiveError(f"Doctor {doctor.name} is inactive.")

        # 1. Lock the target schedule row first to serialize concurrent bookings
        locked_sched = db.scalars(
            select(DoctorSchedule)
            .where(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.date == appointment_date,
                DoctorSchedule.status == "active",
                DoctorSchedule.start_time <= start_time,
                DoctorSchedule.end_time > start_time
            )
            .with_for_update()
        ).first()

        if not locked_sched:
            from app.services.exceptions import ScheduleNotFoundError
            raise ScheduleNotFoundError(
                f"No active schedule found for doctor #{doctor_id} on {appointment_date} covering {start_time.strftime('%H:%M')}."
            )

        # 2. Availability re-check under the schedule lock
        slot_info = check_slot_availability(doctor_id, appointment_date, start_time, db=db)
        if not slot_info["available"]:
            if slot_info.get("reason") == "Slot is already booked.":
                raise SlotAlreadyBookedError(
                    f"Slot {start_time.strftime('%H:%M')} on {appointment_date} is already booked."
                )
            raise SlotNotAvailableError(
                f"Slot {start_time.strftime('%H:%M')} on {appointment_date} is not available: {slot_info['reason']}"
            )

        end_time = datetime.strptime(slot_info["end_time"], "%H:%M").time()

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            schedule_id=locked_sched.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            status=status
        )

        db.add(appointment)
        try:
            if is_local_session:
                db.commit()
                db.refresh(appointment)
            else:
                db.flush()
        except IntegrityError as e:
            if is_local_session:
                db.rollback()
            if "uq_doctor_active_slot" in str(e):
                raise SlotAlreadyBookedError(
                    f"Slot {start_time.strftime('%H:%M')} on {appointment_date} was just booked by another caller."
                ) from e
            raise BookingError(f"Database constraint violation during booking: {e}") from e

        return {
            "success": True,
            "appointment_id": appointment.id,
            "patient_id": patient.id,
            "patient_name": patient.name,
            "doctor_id": slot_info["doctor_id"],
            "doctor_name": slot_info["doctor_name"],
            "date": appointment_date.isoformat(),
            "start_time": start_time.strftime("%H:%M"),
            "end_time": slot_info["end_time"],
            "status": appointment.status.value,
            "reason": reason
        }

    except Exception:
        if is_local_session:
            db.rollback()
        raise
    finally:
        if is_local_session:
            db.close()


def cancel_appointment(
    appointment_id: int,
    cancellation_reason: str | None = None,
    db: Session | None = None
) -> dict[str, Any]:
    """
    Cancel an existing appointment.
    
    Preserves historical appointment record (status = cancelled, stores cancellation_reason)
    and releases the slot for future bookings.
    """
    is_local_session = False
    if db is None:
        db = SessionLocal()
        is_local_session = True

    try:
        # Lock appointment row
        apt = db.scalars(
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .with_for_update()
        ).first()

        if not apt:
            raise AppointmentNotFoundError(f"Appointment with ID {appointment_id} not found.")

        if apt.status == AppointmentStatus.CANCELLED:
            raise AppointmentAlreadyCancelledError(
                f"Appointment #{appointment_id} is already cancelled."
            )

        apt.status = AppointmentStatus.CANCELLED
        if cancellation_reason:
            apt.cancellation_reason = cancellation_reason

        if is_local_session:
            db.commit()
            db.refresh(apt)
        else:
            db.flush()

        return {
            "success": True,
            "appointment_id": apt.id,
            "status": apt.status.value,
            "doctor_id": apt.doctor_id,
            "date": apt.appointment_date.isoformat(),
            "slot": f"{apt.start_time.strftime('%H:%M')} - {apt.end_time.strftime('%H:%M')}",
            "cancellation_reason": apt.cancellation_reason,
            "message": "Appointment successfully cancelled and slot released."
        }

    except Exception:
        if is_local_session:
            db.rollback()
        raise
    finally:
        if is_local_session:
            db.close()


def reschedule_appointment(
    appointment_id: int,
    new_date: date,
    new_start_time: time,
    db: Session | None = None
) -> dict[str, Any]:
    """
    Atomically reschedule an appointment to a new date and time.
    
    Locks the existing appointment and target schedule row.
    If the new slot is unavailable or conflicts, the transaction rolls back
    and the original appointment remains completely untouched.
    """
    is_local_session = False
    if db is None:
        db = SessionLocal()
        is_local_session = True

    try:
        # 1. Lock existing appointment
        apt = db.scalars(
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .with_for_update()
        ).first()

        if not apt:
            raise AppointmentNotFoundError(f"Appointment with ID {appointment_id} not found.")

        if apt.status == AppointmentStatus.CANCELLED:
            raise BookingError(f"Cannot reschedule cancelled appointment #{appointment_id}.")

        # 2. Lock target new schedule row to serialize concurrent bookings on target shift
        locked_new_sched = db.scalars(
            select(DoctorSchedule)
            .where(
                DoctorSchedule.doctor_id == apt.doctor_id,
                DoctorSchedule.date == new_date,
                DoctorSchedule.status == "active",
                DoctorSchedule.start_time <= new_start_time,
                DoctorSchedule.end_time > new_start_time
            )
            .with_for_update()
        ).first()

        if not locked_new_sched:
            from app.services.exceptions import ScheduleNotFoundError
            raise ScheduleNotFoundError(
                f"No active schedule found for doctor #{apt.doctor_id} on {new_date} covering {new_start_time.strftime('%H:%M')}."
            )

        # 3. Check availability of new slot for this doctor under the lock
        new_slot_info = check_slot_availability(apt.doctor_id, new_date, new_start_time, db=db)
        if not new_slot_info["available"]:
            if new_slot_info.get("reason") == "Slot is already booked.":
                raise SlotAlreadyBookedError(
                    f"Cannot reschedule: Slot {new_start_time.strftime('%H:%M')} on {new_date} is already booked."
                )
            raise SlotNotAvailableError(
                f"Cannot reschedule: Slot {new_start_time.strftime('%H:%M')} on {new_date} is not available: {new_slot_info.get('reason')}"
            )

        new_end_time = datetime.strptime(new_slot_info["end_time"], "%H:%M").time()

        orig_date = apt.appointment_date.isoformat()
        orig_time = apt.start_time.strftime("%H:%M")

        # Mutate appointment in-place (preserves appointment identity)
        apt.appointment_date = new_date
        apt.start_time = new_start_time
        apt.end_time = new_end_time
        apt.schedule_id = locked_new_sched.id

        try:
            if is_local_session:
                db.commit()
                db.refresh(apt)
            else:
                db.flush()
        except IntegrityError as e:
            if is_local_session:
                db.rollback()
            if "uq_doctor_active_slot" in str(e):
                raise SlotAlreadyBookedError(
                    f"Slot {new_start_time.strftime('%H:%M')} on {new_date} was just taken by another caller."
                ) from e
            raise BookingError(f"Database conflict during reschedule: {e}") from e

        return {
            "success": True,
            "appointment_id": apt.id,
            "patient_id": apt.patient_id,
            "doctor_id": apt.doctor_id,
            "previous_date": orig_date,
            "previous_time": orig_time,
            "new_date": new_date.isoformat(),
            "new_start_time": new_start_time.strftime("%H:%M"),
            "new_end_time": new_slot_info["end_time"],
            "status": apt.status.value,
            "message": "Appointment successfully rescheduled."
        }

    except Exception:
        if is_local_session:
            db.rollback()
        raise
    finally:
        if is_local_session:
            db.close()
