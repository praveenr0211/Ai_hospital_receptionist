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
