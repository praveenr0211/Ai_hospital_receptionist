from datetime import date, time, datetime, timedelta
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import (
    Doctor,
    DoctorSchedule,
    Appointment,
    DoctorStatus,
    AppointmentStatus,
)
from app.services.exceptions import (
    DoctorNotFoundError,
    DoctorInactiveError,
    ScheduleNotFoundError,
    ScheduleOverlapError,
    InvalidSlotError,
)
from app.services.schedule_service import (
    generate_slots,
    validate_slot_alignment,
    check_schedules_overlap,
)

ACTIVE_APPOINTMENT_STATUSES = {
    AppointmentStatus.PENDING,
    AppointmentStatus.CONFIRMED,
}


def _get_doctor_or_raise(doctor_id: int, db: Session) -> Doctor:
    doctor = db.scalars(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor:
        raise DoctorNotFoundError(f"Doctor with ID {doctor_id} not found.")
    if doctor.status != DoctorStatus.ACTIVE:
        raise DoctorInactiveError(f"Doctor {doctor.name} is currently {doctor.status.value}.")
    return doctor


def get_available_slots(
    doctor_id: int,
    appointment_date: date,
    start_time_range: time | None = None,
    end_time_range: time | None = None,
    db: Session | None = None
) -> dict[str, Any]:
    """
    Compute real-time available slots for a doctor on a specific date.
    
    Excludes active booked appointments (pending and confirmed).
    Supports multiple schedule blocks per day (e.g. morning + afternoon).
    Detects and rejects overlapping schedules.
    Optionally filters by a time window (e.g. afternoon range).
    """
    is_local_session = False
    if db is None:
        db = SessionLocal()
        is_local_session = True

    try:
        doctor = _get_doctor_or_raise(doctor_id, db)

        # Retrieve active schedules for the date
        schedules = db.scalars(
            select(DoctorSchedule)
            .where(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.date == appointment_date,
                DoctorSchedule.status == "active"
            )
            .order_by(DoctorSchedule.start_time)
        ).all()

        if not schedules:
            raise ScheduleNotFoundError(
                f"No active schedule found for Dr. {doctor.name} on {appointment_date}."
            )

        # Validate that multiple schedules do not overlap
        intervals = [(s.start_time, s.end_time) for s in schedules]
        if check_schedules_overlap(intervals):
            raise ScheduleOverlapError(
                f"Dr. {doctor.name} has overlapping schedules on {appointment_date}."
            )

        # Retrieve active appointments blocking slots
        active_appointments = db.scalars(
            select(Appointment)
            .where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES)
            )
        ).all()

        booked_start_times = {apt.start_time for apt in active_appointments}

        all_slots: list[dict[str, Any]] = []
        for sched in schedules:
            sched_slots = generate_slots(sched.start_time, sched.end_time, sched.slot_duration_minutes)
            for st, et in sched_slots:
                # Apply time range filters if specified
                if start_time_range and st < start_time_range:
                    continue
                if end_time_range and et > end_time_range:
                    continue

                is_booked = st in booked_start_times
                all_slots.append({
                    "start": st.strftime("%H:%M"),
                    "end": et.strftime("%H:%M"),
                    "start_time": st,
                    "end_time": et,
                    "schedule_id": sched.id,
                    "available": not is_booked
                })

        formatted_slots = [
            {
                "start": s["start"],
                "end": s["end"],
                "schedule_id": s["schedule_id"],
                "available": s["available"]
            }
            for s in all_slots
        ]

        return {
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "specialty": doctor.specialty.name if doctor.specialty else None,
            "date": appointment_date.isoformat(),
            "total_slots": len(formatted_slots),
            "available_count": sum(1 for s in formatted_slots if s["available"]),
            "slots": formatted_slots
        }

    finally:
        if is_local_session:
            db.close()


def check_slot_availability(
    doctor_id: int,
    appointment_date: date,
    start_time: time,
    db: Session | None = None
) -> dict[str, Any]:
    """
    Validate whether a specific slot is available for booking.
    
    Performs full deterministic validation:
    1. Doctor exists and is active
    2. Working schedule exists on requested date
    3. Start time falls within a schedule and matches slot duration boundary
    4. Slot is not already booked in an active appointment
    """
    is_local_session = False
    if db is None:
        db = SessionLocal()
        is_local_session = True

    try:
        doctor = _get_doctor_or_raise(doctor_id, db)

        schedules = db.scalars(
            select(DoctorSchedule)
            .where(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.date == appointment_date,
                DoctorSchedule.status == "active"
            )
            .order_by(DoctorSchedule.start_time)
        ).all()

        if not schedules:
            raise ScheduleNotFoundError(
                f"No active schedule found for Dr. {doctor.name} on {appointment_date}."
            )

        intervals = [(s.start_time, s.end_time) for s in schedules]
        if check_schedules_overlap(intervals):
            raise ScheduleOverlapError(
                f"Dr. {doctor.name} has overlapping schedules on {appointment_date}."
            )

        # Match start_time to one of the schedules
        matching_schedule: DoctorSchedule | None = None
        calculated_end_time: time | None = None

        for sched in schedules:
            is_valid, et = validate_slot_alignment(
                start_time,
                sched.start_time,
                sched.end_time,
                sched.slot_duration_minutes
            )
            if is_valid:
                matching_schedule = sched
                calculated_end_time = et
                break

        if not matching_schedule or calculated_end_time is None:
            raise InvalidSlotError(
                f"Time {start_time.strftime('%H:%M')} does not align with any valid slot on {appointment_date}."
            )

        # Check existing active appointment
        existing_appointment = db.scalars(
            select(Appointment)
            .where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.start_time == start_time,
                Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES)
            )
        ).first()

        if existing_appointment:
            return {
                "available": False,
                "doctor_id": doctor.id,
                "doctor_name": doctor.name,
                "date": appointment_date.isoformat(),
                "start_time": start_time.strftime("%H:%M"),
                "end_time": calculated_end_time.strftime("%H:%M"),
                "schedule_id": matching_schedule.id,
                "reason": "Slot is already booked."
            }

        return {
            "available": True,
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "date": appointment_date.isoformat(),
            "start_time": start_time.strftime("%H:%M"),
            "end_time": calculated_end_time.strftime("%H:%M"),
            "schedule_id": matching_schedule.id,
            "reason": None
        }

    finally:
        if is_local_session:
            db.close()


def find_alternative_slots(
    doctor_id: int,
    appointment_date: date,
    requested_time: time,
    limit: int = 3,
    db: Session | None = None
) -> dict[str, Any]:
    """
    Find nearby available slots on the same date when the requested slot is unavailable.
    
    Sorts available slots outward by absolute time distance from requested_time.
    """
    is_local_session = False
    if db is None:
        db = SessionLocal()
        is_local_session = True

    try:
        avail_data = get_available_slots(doctor_id, appointment_date, db=db)
        requested_str = requested_time.strftime("%H:%M")

        is_requested_available = any(
            s["start"] == requested_str and s["available"]
            for s in avail_data["slots"]
        )

        available_slots = [s for s in avail_data["slots"] if s["available"]]

        dummy_today = date(2000, 1, 1)
        req_dt = datetime.combine(dummy_today, requested_time)

        def distance_from_requested(slot_dict: dict[str, Any]) -> float:
            st = datetime.strptime(slot_dict["start"], "%H:%M").time()
            st_dt = datetime.combine(dummy_today, st)
            return abs((st_dt - req_dt).total_seconds())

        available_slots.sort(key=distance_from_requested)
        top_alternatives = available_slots[:limit]

        return {
            "doctor_id": doctor_id,
            "doctor_name": avail_data["doctor_name"],
            "date": appointment_date.isoformat(),
            "requested_slot": requested_str,
            "available": is_requested_available,
            "alternatives": [s["start"] for s in top_alternatives]
        }

    finally:
        if is_local_session:
            db.close()
