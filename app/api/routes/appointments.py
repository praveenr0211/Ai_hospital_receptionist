from datetime import date as dt_date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.api.deps import get_db
from app.models import Appointment
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentCancel,
    AppointmentCancelResponse,
    AppointmentReschedule,
    AppointmentRescheduleResponse,
    AppointmentListResponse,
)
from app.services import (
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
    get_appointment,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED, summary="Create Appointment")
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    result = book_appointment(
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        start_time=payload.start_time,
        reason=payload.reason,
        db=db
    )
    db.commit()
    return result

@router.get("/{appointment_id}", response_model=AppointmentResponse, summary="Get Appointment Details")
def get_appointment_by_id(appointment_id: int, db: Session = Depends(get_db)):
    return get_appointment(appointment_id=appointment_id, db=db)

@router.get("", response_model=AppointmentListResponse, summary="List Appointments")
def list_appointments(
    doctor_id: int | None = Query(None, description="Filter by doctor ID"),
    patient_id: int | None = Query(None, description="Filter by patient ID"),
    date: dt_date | None = Query(None, description="Filter by date"),
    status: str | None = Query(None, description="Filter by appointment status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    query = (
        select(Appointment)
        .options(
            selectinload(Appointment.doctor),
            selectinload(Appointment.patient)
        )
    )
    count_query = select(func.count(Appointment.id))

    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
        count_query = count_query.where(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.where(Appointment.patient_id == patient_id)
        count_query = count_query.where(Appointment.patient_id == patient_id)
    if date:
        query = query.where(Appointment.appointment_date == date)
        count_query = count_query.where(Appointment.appointment_date == date)
    if status:
        query = query.where(Appointment.status == status)
        count_query = count_query.where(Appointment.status == status)

    total = db.scalar(count_query) or 0
    offset = (page - 1) * page_size
    apts = db.scalars(
        query.order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
        .offset(offset)
        .limit(page_size)
    ).all()

    items = [
        AppointmentResponse(
            appointment_id=a.id,
            patient_id=a.patient_id,
            patient_name=a.patient.name,
            doctor_id=a.doctor_id,
            doctor_name=a.doctor.name,
            specialty=a.doctor.specialty.name if a.doctor.specialty else None,
            date=a.appointment_date.isoformat(),
            start_time=a.start_time.strftime("%H:%M"),
            end_time=a.end_time.strftime("%H:%M"),
            status=a.status.value,
            reason=a.reason,
            cancellation_reason=a.cancellation_reason
        )
        for a in apts
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("/{appointment_id}/cancel", response_model=AppointmentCancelResponse, summary="Cancel Appointment")
def cancel_existing_appointment(
    appointment_id: int,
    payload: AppointmentCancel = AppointmentCancel(),
    db: Session = Depends(get_db)
):
    result = cancel_appointment(
        appointment_id=appointment_id,
        cancellation_reason=payload.reason,
        db=db
    )
    db.commit()
    return result

@router.post("/{appointment_id}/reschedule", response_model=AppointmentRescheduleResponse, summary="Reschedule Appointment")
def reschedule_existing_appointment(
    appointment_id: int,
    payload: AppointmentReschedule,
    db: Session = Depends(get_db)
):
    result = reschedule_appointment(
        appointment_id=appointment_id,
        new_date=payload.new_date,
        new_start_time=payload.new_start_time,
        db=db
    )
    db.commit()
    return result
