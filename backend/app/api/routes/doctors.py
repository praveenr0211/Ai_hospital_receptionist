from datetime import date as dt_date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.api.deps import get_db
from app.models import Doctor, DoctorSchedule, Appointment
from app.models.enums import DoctorStatus, AppointmentStatus
from app.schemas.doctor import DoctorResponse, DoctorListResponse
from app.schemas.schedule import DoctorSchedulesResponse, ScheduleItem
from app.schemas.appointment import DoctorBookedAppointmentsResponse, DoctorBookedAppointmentItem
from app.services.exceptions import DoctorNotFoundError

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("", response_model=DoctorListResponse, summary="List Doctors")
def list_doctors(
    specialty_id: int | None = Query(None, description="Filter by specialty ID"),
    status: str | None = Query(None, description="Filter by status (active/inactive)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    query = select(Doctor).options(selectinload(Doctor.specialty))
    count_query = select(func.count(Doctor.id))

    if specialty_id:
        query = query.where(Doctor.specialty_id == specialty_id)
        count_query = count_query.where(Doctor.specialty_id == specialty_id)
    if status:
        query = query.where(Doctor.status == status)
        count_query = count_query.where(Doctor.status == status)

    total = db.scalar(count_query) or 0
    offset = (page - 1) * page_size
    doctors = db.scalars(query.order_by(Doctor.id).offset(offset).limit(page_size)).all()

    return {
        "items": doctors,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{doctor_id}", response_model=DoctorResponse, summary="Get Doctor Details")
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.scalars(
        select(Doctor)
        .options(selectinload(Doctor.specialty))
        .where(Doctor.id == doctor_id)
    ).first()
    if not doctor:
        raise DoctorNotFoundError(f"Doctor with ID {doctor_id} not found.")
    return doctor

@router.get("/{doctor_id}/schedules", response_model=DoctorSchedulesResponse, summary="Get Doctor Shifts")
def get_doctor_schedules(
    doctor_id: int,
    date: dt_date | None = Query(None, description="Specific schedule date"),
    start_date: dt_date | None = Query(None, description="Range start date"),
    end_date: dt_date | None = Query(None, description="Range end date"),
    db: Session = Depends(get_db)
):
    doctor = db.scalars(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor:
        raise DoctorNotFoundError(f"Doctor with ID {doctor_id} not found.")

    query = select(DoctorSchedule).where(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.status == "active"
    )

    if date:
        query = query.where(DoctorSchedule.date == date)
    else:
        if start_date:
            query = query.where(DoctorSchedule.date >= start_date)
        if end_date:
            query = query.where(DoctorSchedule.date <= end_date)

    schedules = db.scalars(query.order_by(DoctorSchedule.date, DoctorSchedule.start_time)).all()

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
        "date": date.isoformat() if date else None,
        "schedules": items
    }

@router.get("/{doctor_id}/appointments", response_model=DoctorBookedAppointmentsResponse, summary="Get Doctor's Booked Patients")
def get_doctor_appointments(
    doctor_id: int,
    date: dt_date | None = Query(None, description="Filter by appointment date"),
    status: str | None = Query(None, description="Filter by appointment status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    doctor = db.scalars(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor:
        raise DoctorNotFoundError(f"Doctor with ID {doctor_id} not found.")

    query = (
        select(Appointment)
        .options(selectinload(Appointment.patient))
        .where(Appointment.doctor_id == doctor_id)
    )
    count_query = select(func.count(Appointment.id)).where(Appointment.doctor_id == doctor_id)

    if date:
        query = query.where(Appointment.appointment_date == date)
        count_query = count_query.where(Appointment.appointment_date == date)
    if status:
        query = query.where(Appointment.status == status)
        count_query = count_query.where(Appointment.status == status)

    total = db.scalar(count_query) or 0
    offset = (page - 1) * page_size
    apts = db.scalars(query.order_by(Appointment.appointment_date, Appointment.start_time).offset(offset).limit(page_size)).all()

    items = [
        DoctorBookedAppointmentItem(
            appointment_id=a.id,
            patient_id=a.patient_id,
            patient_name=a.patient.name,
            patient_phone=a.patient.phone,
            date=a.appointment_date.isoformat(),
            start_time=a.start_time.strftime("%H:%M"),
            end_time=a.end_time.strftime("%H:%M"),
            reason=a.reason,
            status=a.status.value
        )
        for a in apts
    ]

    return {
        "doctor_id": doctor.id,
        "doctor_name": doctor.name,
        "appointments": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
