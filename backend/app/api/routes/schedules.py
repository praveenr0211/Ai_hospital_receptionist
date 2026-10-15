from datetime import date as dt_date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models import DoctorSchedule, Doctor
from app.schemas.schedule import DoctorSchedulesResponse, ScheduleItem
from app.services.exceptions import DoctorNotFoundError

router = APIRouter(prefix="/schedules", tags=["Schedules"])

@router.get("", response_model=DoctorSchedulesResponse, summary="Get Doctor Schedules")
def get_schedules(
    doctor_id: int = Query(..., description="Doctor ID"),
    date: dt_date = Query(..., description="Schedule Date"),
    db: Session = Depends(get_db)
):
    doctor = db.scalars(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor:
        raise DoctorNotFoundError(f"Doctor with ID {doctor_id} not found.")

    schedules = db.scalars(
        select(DoctorSchedule)
        .where(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.date == date,
            DoctorSchedule.status == "active"
        )
        .order_by(DoctorSchedule.start_time)
    ).all()

    items = [
        ScheduleItem(
            id=s.id,
            start_time=s.start_time.strftime("%H:%M"),
            end_time=s.end_time.strftime("%H:%M"),
            slot_duration_minutes=s.slot_duration_minutes,
            status=s.status
        )
        for s in schedules
    ]

    return {
        "doctor_id": doctor.id,
        "doctor_name": doctor.name,
        "date": date.isoformat(),
        "schedules": items
    }


@router.post("/maintain-window", summary="Maintain rolling schedule window")
def maintain_schedule_window(
    days: int = Query(14, ge=1, le=30, description="Rolling window days ahead"),
    db: Session = Depends(get_db)
):
    """Admin/System endpoint to verify and extend doctor schedules across the rolling window."""
    from app.services.rolling_schedule_service import ensure_rolling_schedules
    created_count = ensure_rolling_schedules(window_days=days, db=db)
    return {
        "status": "success",
        "window_days": days,
        "new_schedule_blocks_created": created_count,
        "message": f"Rolling schedule window maintained for {days} days ahead."
    }

