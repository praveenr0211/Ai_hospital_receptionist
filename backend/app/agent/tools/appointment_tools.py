from datetime import date, time, datetime
from typing import Any
from sqlalchemy.orm import Session
from app.services.booking_service import (
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)
from app.services.exceptions import (
    PatientNotFoundError,
    DoctorNotFoundError,
    DoctorInactiveError,
    SlotNotAvailableError,
    SlotAlreadyBookedError,
    AppointmentNotFoundError,
    AppointmentAlreadyCancelledError,
    ScheduleNotFoundError,
    BookingError,
)
from app.schemas.tool_results import (
    BookingToolResult,
    CancellationToolResult,
    RescheduleToolResult,
)

def _parse_date(d: date | str) -> date:
    if isinstance(d, date):
        return d
    return datetime.strptime(d.strip(), "%Y-%m-%d").date()

def _parse_time(t: time | str) -> time:
    if isinstance(t, time):
        return t
    clean = t.strip()
    if len(clean.split(":")) == 3:
        return datetime.strptime(clean, "%H:%M:%S").time()
    return datetime.strptime(clean, "%H:%M").time()

def book_appointment_tool(
    db: Session,
    patient_id: int,
    doctor_id: int,
    appointment_date: date | str,
    start_time: time | str,
    reason: str | None = None,
) -> BookingToolResult:
    """Book a new appointment through the Phase 2 transactional booking engine."""
    try:
        parsed_date = _parse_date(appointment_date)
        parsed_time = _parse_time(start_time)

        res = book_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=parsed_date,
            start_time=parsed_time,
            reason=reason,
            db=db,
        )

        return BookingToolResult(
            success=True,
            appointment_id=res["appointment_id"],
            doctor_id=res["doctor_id"],
            doctor_name=res.get("doctor_name"),
            patient_id=res["patient_id"],
            appointment_date=res.get("date", res.get("appointment_date")),
            start_time=res["start_time"],
            end_time=res.get("end_time"),
            status=res["status"],
        )
    except SlotAlreadyBookedError as e:
        return BookingToolResult(
            success=False,
            error_code="SLOT_ALREADY_BOOKED",
            error_message=str(e),
        )
    except SlotNotAvailableError as e:
        return BookingToolResult(
            success=False,
            error_code="SLOT_NOT_AVAILABLE",
            error_message=str(e),
        )
    except (PatientNotFoundError, DoctorNotFoundError, DoctorInactiveError, ScheduleNotFoundError) as e:
        return BookingToolResult(
            success=False,
            error_code="INVALID_BOOKING_PARAMETERS",
            error_message=str(e),
        )
    except Exception as e:
        return BookingToolResult(
            success=False,
            error_code="BOOKING_FAILED",
            error_message=f"Internal booking error: {str(e)}",
        )

def cancel_appointment_tool(
    db: Session,
    appointment_id: int,
    reason: str | None = "Cancelled by patient via AI receptionist",
) -> CancellationToolResult:
    """Cancel an existing appointment via the Phase 2 cancellation service."""
    try:
        res = cancel_appointment(
            appointment_id=appointment_id,
            cancellation_reason=reason,
            db=db,
        )
        return CancellationToolResult(
            success=True,
            appointment_id=res["appointment_id"],
            status=res["status"],
        )
    except AppointmentAlreadyCancelledError as e:
        return CancellationToolResult(
            success=False,
            error_code="APPOINTMENT_ALREADY_CANCELLED",
            error_message=str(e),
        )
    except AppointmentNotFoundError as e:
        return CancellationToolResult(
            success=False,
            error_code="APPOINTMENT_NOT_FOUND",
            error_message=str(e),
        )
    except Exception as e:
        return CancellationToolResult(
            success=False,
            error_code="CANCELLATION_FAILED",
            error_message=str(e),
        )

def reschedule_appointment_tool(
    db: Session,
    appointment_id: int,
    new_date: date | str,
    new_start_time: time | str,
) -> RescheduleToolResult:
    """Reschedule an existing appointment atomically via the Phase 2 booking engine."""
    try:
        parsed_date = _parse_date(new_date)
        parsed_time = _parse_time(new_start_time)

        res = reschedule_appointment(
            appointment_id=appointment_id,
            new_date=parsed_date,
            new_start_time=parsed_time,
            db=db,
        )
        return RescheduleToolResult(
            success=True,
            appointment_id=res["appointment_id"],
            new_date=res["new_date"],
            new_start_time=res.get("new_start_time", res.get("new_slot", "").split(" - ")[0]),
            new_end_time=res.get("new_end_time", res.get("new_slot", "").split(" - ")[-1]),
            status=res["status"],
        )
    except SlotAlreadyBookedError as e:
        return RescheduleToolResult(
            success=False,
            error_code="SLOT_ALREADY_BOOKED",
            error_message=str(e),
        )
    except SlotNotAvailableError as e:
        return RescheduleToolResult(
            success=False,
            error_code="SLOT_NOT_AVAILABLE",
            error_message=str(e),
        )
    except (AppointmentNotFoundError, ScheduleNotFoundError, BookingError) as e:
        return RescheduleToolResult(
            success=False,
            error_code="RESCHEDULE_REJECTED",
            error_message=str(e),
        )
    except Exception as e:
        return RescheduleToolResult(
            success=False,
            error_code="RESCHEDULE_FAILED",
            error_message=str(e),
        )
