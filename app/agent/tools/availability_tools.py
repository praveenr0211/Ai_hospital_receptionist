from datetime import date, time, datetime
from typing import Any
from sqlalchemy.orm import Session
from app.services.availability_service import (
    get_available_slots,
    check_slot_availability,
    find_alternative_slots as service_find_alternatives,
)
from app.services.exceptions import (
    DoctorNotFoundError,
    DoctorInactiveError,
    ScheduleNotFoundError,
    InvalidSlotError,
)
from app.schemas.tool_results import (
    AvailabilityToolResult,
    SlotCheckResult,
    AlternativeSlotsResult,
    SlotInfo,
)

def _parse_date(d: date | str) -> date:
    if isinstance(d, date):
        return d
    return datetime.strptime(d.strip(), "%Y-%m-%d").date()

def _parse_time(t: time | str) -> time:
    if isinstance(t, time):
        return t
    clean = t.strip()
    # Handle both HH:MM and HH:MM:SS
    if len(clean.split(":")) == 3:
        return datetime.strptime(clean, "%H:%M:%S").time()
    return datetime.strptime(clean, "%H:%M").time()

def check_doctor_availability(
    db: Session,
    doctor_id: int,
    date_val: date | str,
) -> AvailabilityToolResult:
    """Retrieve all available appointment slots for a doctor on a specific date."""
    try:
        parsed_date = _parse_date(date_val)
        res = get_available_slots(doctor_id=doctor_id, appointment_date=parsed_date, db=db)
        raw_slots = res.get("slots", [])
        slots = [
            SlotInfo(start_time=s["start"], end_time=s["end"])
            for s in raw_slots
            if s.get("available")
        ]
        return AvailabilityToolResult(
            success=True,
            doctor_id=doctor_id,
            doctor_name=res.get("doctor_name"),
            date=parsed_date.isoformat(),
            available_slots=slots,
            total_available=res.get("available_count", len(slots)),
        )
    except (DoctorNotFoundError, DoctorInactiveError, ScheduleNotFoundError) as e:
        return AvailabilityToolResult(
            success=False,
            doctor_id=doctor_id,
            date=str(date_val),
            available_slots=[],
            total_available=0,
            error=str(e),
        )
    except Exception as e:
        return AvailabilityToolResult(
            success=False,
            doctor_id=doctor_id,
            date=str(date_val),
            available_slots=[],
            total_available=0,
            error=f"Unexpected error checking availability: {str(e)}",
        )

def check_specific_slot(
    db: Session,
    doctor_id: int,
    date_val: date | str,
    start_time_val: time | str,
) -> SlotCheckResult:
    """Check if a specific slot is available for booking."""
    try:
        parsed_date = _parse_date(date_val)
        parsed_time = _parse_time(start_time_val)
        res = check_slot_availability(
            doctor_id=doctor_id,
            appointment_date=parsed_date,
            start_time=parsed_time,
            db=db,
        )
        return SlotCheckResult(
            success=True,
            available=res["available"],
            doctor_id=doctor_id,
            date=parsed_date.isoformat(),
            start_time=parsed_time.strftime("%H:%M"),
            end_time=res.get("end_time"),
            error=res.get("reason") if not res["available"] else None,
        )
    except Exception as e:
        return SlotCheckResult(
            success=False,
            available=False,
            doctor_id=doctor_id,
            date=str(date_val),
            start_time=str(start_time_val),
            error=str(e),
        )

def find_alternative_slots(
    db: Session,
    doctor_id: int,
    target_date: date | str,
    target_time: time | str,
    limit: int = 4,
) -> AlternativeSlotsResult:
    """Find the closest alternative available slots when a requested slot is unavailable."""
    try:
        parsed_date = _parse_date(target_date)
        parsed_time = _parse_time(target_time)
        res = service_find_alternatives(
            doctor_id=doctor_id,
            appointment_date=parsed_date,
            preferred_time=parsed_time,
            limit=limit,
            db=db,
        )
        raw_alts = res.get("alternatives", [])
        slots = []
        for a in raw_alts:
            if isinstance(a, str):
                slots.append(SlotInfo(start_time=a, end_time=""))
            elif isinstance(a, dict):
                slots.append(SlotInfo(
                    start_time=a.get("start", a.get("start_time", "")),
                    end_time=a.get("end", a.get("end_time", ""))
                ))
        return AlternativeSlotsResult(
            success=True,
            doctor_id=doctor_id,
            date=parsed_date.isoformat(),
            alternatives=slots,
        )
    except Exception as e:
        return AlternativeSlotsResult(
            success=False,
            doctor_id=doctor_id,
            date=str(target_date),
            alternatives=[],
            error=str(e),
        )
