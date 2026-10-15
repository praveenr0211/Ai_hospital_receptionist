"""Rolling Schedule Service.

Maintains an automatic, rolling 14-day schedule horizon for all active hospital doctors.
Provides both proactive batch population and on-demand just-in-time (JIT) provisioning.
"""

import logging
import asyncio
from datetime import date, time, timedelta, datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.doctor import Doctor, DoctorStatus
from app.models.schedule import DoctorSchedule

logger = logging.getLogger("services.rolling_schedule")

ROLLING_WINDOW_DAYS = 14

# Default Shift Patterns
DEFAULT_MORNING_SHIFT = (time(9, 0), time(13, 0), 30)
DEFAULT_AFTERNOON_SHIFT = (time(14, 0), time(18, 0), 30)


def get_default_shifts_for_doctor(doctor: Doctor, target_date: date) -> List[tuple[time, time, int]]:
    """
    Determine default daily shifts for a doctor based on day of week and doctor ID.
    - Sunday: Morning shift only (light staffing)
    - Monday - Saturday:
      - Doctors with even ID: Morning + Afternoon (8h availability)
      - Doctors with odd ID: Morning (4h availability)
    """
    is_sunday = target_date.weekday() == 6
    if is_sunday:
        return [DEFAULT_MORNING_SHIFT]

    if doctor.id % 2 == 0:
        return [DEFAULT_MORNING_SHIFT, DEFAULT_AFTERNOON_SHIFT]
    return [DEFAULT_MORNING_SHIFT, DEFAULT_AFTERNOON_SHIFT]


def ensure_doctor_schedule_for_date(
    doctor_id: int,
    target_date: date,
    db: Session
) -> List[DoctorSchedule]:
    """
    Idempotently ensure schedule blocks exist for a specific doctor on a given date.
    Returns existing or newly created schedule blocks.
    """
    # 1. Check existing schedules
    existing = db.scalars(
        select(DoctorSchedule)
        .where(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.date == target_date,
            DoctorSchedule.status == "active"
        )
        .order_by(DoctorSchedule.start_time)
    ).all()

    if existing:
        return list(existing)

    # 2. Check if doctor is active
    doctor = db.scalars(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor or doctor.status != DoctorStatus.ACTIVE:
        return []

    # 3. Create default shift blocks
    shifts = get_default_shifts_for_doctor(doctor, target_date)
    new_schedules = []
    for start_t, end_t, dur in shifts:
        sched = DoctorSchedule(
            doctor_id=doctor_id,
            date=target_date,
            start_time=start_t,
            end_time=end_t,
            slot_duration_minutes=dur,
            status="active"
        )
        db.add(sched)
        new_schedules.append(sched)

    db.flush()
    return new_schedules


def ensure_rolling_schedules(
    start_date: Optional[date] = None,
    window_days: int = ROLLING_WINDOW_DAYS,
    db: Optional[Session] = None
) -> int:
    """
    Ensures that every active doctor has schedules from start_date through start_date + window_days.
    Returns the total count of new schedule blocks created.
    """
    is_local_db = False
    if db is None:
        db = SessionLocal()
        is_local_db = True

    try:
        active_doctors = db.scalars(
            select(Doctor).where(Doctor.status == DoctorStatus.ACTIVE)
        ).all()

        if not active_doctors:
            logger.info("No active doctors found for rolling schedule generation.")
            return 0

        effective_start = start_date or date.today()
        dates_to_check = [effective_start + timedelta(days=i) for i in range(window_days + 1)]

        created_count = 0
        for doc in active_doctors:
            for day in dates_to_check:
                shifts = get_default_shifts_for_doctor(doc, day)
                for start_t, end_t, dur in shifts:
                    existing = db.scalars(
                        select(DoctorSchedule).where(
                            DoctorSchedule.doctor_id == doc.id,
                            DoctorSchedule.date == day,
                            DoctorSchedule.start_time == start_t,
                            DoctorSchedule.status == "active"
                        )
                    ).first()

                    if not existing:
                        sched = DoctorSchedule(
                            doctor_id=doc.id,
                            date=day,
                            start_time=start_t,
                            end_time=end_t,
                            slot_duration_minutes=dur,
                            status="active"
                        )
                        db.add(sched)
                        created_count += 1

        db.commit()
        if created_count > 0:
            logger.info(
                "Rolling schedule window extended: created %d blocks across %d doctors for %d days.",
                created_count,
                len(active_doctors),
                len(dates_to_check)
            )
        return created_count
    except Exception as e:
        db.rollback()
        logger.error("Failed to maintain rolling schedule window: %s", e)
        raise
    finally:
        if is_local_db:
            db.close()


async def schedule_maintenance_background_worker() -> None:
    """
    Continuous background task running during application lifespan.
    Runs once immediately on startup, then runs periodically every 12 hours.
    """
    logger.info("Starting rolling schedule background maintenance worker.")
    while True:
        try:
            # Run in a thread to keep async event loop completely unblocked
            created = await asyncio.to_thread(ensure_rolling_schedules)
            logger.info("Periodic schedule check complete. New blocks created: %d", created)
        except asyncio.CancelledError:
            logger.info("Rolling schedule maintenance worker cancelled.")
            break
        except Exception as err:
            logger.warning("Error in schedule background worker: %s", err)

        # Sleep for 12 hours before next check
        try:
            await asyncio.sleep(12 * 3600)
        except asyncio.CancelledError:
            break
