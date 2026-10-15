from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.api.deps import get_db
from app.models import Patient, Appointment
from app.schemas.patient import PatientCreate, PatientResponse, PatientListResponse
from app.schemas.appointment import AppointmentResponse
from app.services.exceptions import PatientNotFoundError, BookingError

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=PatientListResponse, summary="List Patients")
def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    count_query = select(func.count(Patient.id))
    total = db.scalar(count_query) or 0
    offset = (page - 1) * page_size
    patients = db.scalars(select(Patient).order_by(Patient.id.desc()).offset(offset).limit(page_size)).all()
    return {
        "items": patients,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/by-phone/{phone}", response_model=PatientResponse, summary="Find Patient by Phone")
def get_patient_by_phone(phone: str, db: Session = Depends(get_db)):
    clean_phone = phone.strip()
    patient = db.scalars(select(Patient).where(Patient.phone == clean_phone)).first()
    if not patient:
        raise PatientNotFoundError(f"Patient with phone '{clean_phone}' not found.")
    return patient

@router.get("/{patient_id}", response_model=PatientResponse, summary="Get Patient Details")
def get_patient_by_id(patient_id: int, db: Session = Depends(get_db)):
    patient = db.scalars(select(Patient).where(Patient.id == patient_id)).first()
    if not patient:
        raise PatientNotFoundError(f"Patient with ID {patient_id} not found.")
    return patient

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED, summary="Create Patient")
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    clean_phone = payload.phone.strip()
    existing = db.scalars(select(Patient).where(Patient.phone == clean_phone)).first()
    if existing:
        raise BookingError(f"Patient with phone '{clean_phone}' already exists with ID #{existing.id}.")

    new_patient = Patient(
        name=payload.name.strip(),
        phone=clean_phone,
        email=payload.email.strip() if payload.email else None,
        age=payload.age,
        gender=payload.gender
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/{patient_id}/appointments", response_model=list[AppointmentResponse], summary="Get Patient's Appointments")
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    patient = db.scalars(select(Patient).where(Patient.id == patient_id)).first()
    if not patient:
        raise PatientNotFoundError(f"Patient with ID {patient_id} not found.")

    apts = db.scalars(
        select(Appointment)
        .options(
            selectinload(Appointment.doctor),
            selectinload(Appointment.patient)
        )
        .where(Appointment.patient_id == patient_id)
        .order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
    ).all()

    return [
        AppointmentResponse(
            appointment_id=a.id,
            patient_id=a.patient_id,
            patient_name=patient.name,
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
