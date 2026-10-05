from datetime import date as dt_date, time as dt_time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.availability import (
    DoctorAvailabilityResponse,
    SlotCheckResponse,
    AlternativeSlotsResponse,
    AvailableSlotItem,
)
from app.services import (
    get_available_slots,
    check_slot_availability,
    find_alternative_slots,
)

router = APIRouter(prefix="/doctors", tags=["Availability"])

@router.get("/{doctor_id}/availability", response_model=DoctorAvailabilityResponse, summary="Get Available Slots")
def get_doctor_availability(
    doctor_id: int,
    date: dt_date = Query(..., description="Target appointment date"),
    start_time: dt_time | None = Query(None, description="Optional start time range filter"),
    end_time: dt_time | None = Query(None, description="Optional end time range filter"),
    db: Session = Depends(get_db)
):
    result = get_available_slots(
        doctor_id=doctor_id,
        appointment_date=date,
        start_time_range=start_time,
        end_time_range=end_time,
        db=db
    )

    slot_items = [
        AvailableSlotItem(
            start_time=s["start"],
            end_time=s["end"],
            available=s["available"]
        )
        for s in result["slots"]
    ]

    return {
        "doctor_id": result["doctor_id"],
        "doctor_name": result["doctor_name"],
        "date": result["date"],
        "total_slots": result["total_slots"],
        "available_count": result["available_count"],
        "slots": slot_items
    }

@router.get("/{doctor_id}/availability/check", response_model=SlotCheckResponse, summary="Check Specific Slot Availability")
def check_single_slot(
    doctor_id: int,
    date: dt_date = Query(..., description="Target appointment date"),
    start_time: dt_time = Query(..., description="Requested start time (e.g. 10:30)"),
    db: Session = Depends(get_db)
):
    result = check_slot_availability(
        doctor_id=doctor_id,
        appointment_date=date,
        start_time=start_time,
        db=db
    )
    return result

@router.get("/{doctor_id}/availability/alternatives", response_model=AlternativeSlotsResponse, summary="Find Nearest Alternative Slots")
def get_alternative_slots(
    doctor_id: int,
    date: dt_date = Query(..., description="Target appointment date"),
    requested_time: dt_time = Query(..., description="Originally requested start time"),
    limit: int = Query(3, ge=1, le=10, description="Max number of alternatives"),
    db: Session = Depends(get_db)
):
    result = find_alternative_slots(
        doctor_id=doctor_id,
        appointment_date=date,
        requested_time=requested_time,
        limit=limit,
        db=db
    )
    return {
        "doctor_id": result["doctor_id"],
        "doctor_name": result["doctor_name"],
        "date": result["date"],
        "requested_time": result.get("requested_slot", result.get("requested_time", requested_time.strftime("%H:%M"))),
        "available": result["available"],
        "alternatives": result["alternatives"]
    }
