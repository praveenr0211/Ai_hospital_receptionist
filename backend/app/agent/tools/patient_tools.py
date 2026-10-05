from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.tool_results import (
    PatientLookupResult,
    PatientCreateResult,
    PatientAppointmentsResult,
    AppointmentItem,
)

def find_patient_by_phone(db: Session, phone_number: str) -> PatientLookupResult:
    """Look up a patient by their phone number."""
    clean_phone = phone_number.strip()
    patient = db.scalars(select(Patient).where(Patient.phone == clean_phone)).first()
    if not patient:
        return PatientLookupResult(
            success=True,
            exists=False,
            phone_number=clean_phone,
        )
    return PatientLookupResult(
        success=True,
        exists=True,
        patient_id=patient.id,
        patient_name=patient.name,
        phone_number=patient.phone,
    )

def create_patient(
    db: Session,
    name: str,
    phone_number: str,
    email: str | None = None,
    age: int | None = None,
    gender: str | None = None,
) -> PatientCreateResult:
    """Create a new patient record in the database."""
    clean_phone = phone_number.strip()
    clean_name = name.strip()
    
    # Check if patient already exists with this phone
    existing = db.scalars(select(Patient).where(Patient.phone == clean_phone)).first()
    if existing:
        return PatientCreateResult(
            success=True,
            patient_id=existing.id,
            patient_name=existing.name,
            phone_number=existing.phone,
        )
    
    new_patient = Patient(
        name=clean_name,
        phone=clean_phone,
        email=email.strip() if email else None,
        age=age,
        gender=gender.strip() if gender else None,
    )
    db.add(new_patient)
    db.flush()
    db.refresh(new_patient)
    
    return PatientCreateResult(
        success=True,
        patient_id=new_patient.id,
        patient_name=new_patient.name,
        phone_number=new_patient.phone,
    )

def get_patient_appointments(db: Session, patient_id: int) -> PatientAppointmentsResult:
    """Retrieve active appointments for a patient (for cancellation or rescheduling)."""
    appointments = db.scalars(
        select(Appointment)
        .where(
            Appointment.patient_id == patient_id,
            Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]),
        )
        .order_by(Appointment.appointment_date.asc(), Appointment.start_time.asc())
    ).all()

    items = [
        AppointmentItem(
            appointment_id=apt.id,
            doctor_id=apt.doctor_id,
            doctor_name=apt.doctor.name if apt.doctor else f"Doctor #{apt.doctor_id}",
            appointment_date=apt.appointment_date.isoformat(),
            start_time=apt.start_time.strftime("%H:%M"),
            end_time=apt.end_time.strftime("%H:%M"),
            status=apt.status.value,
        )
        for apt in appointments
    ]
    return PatientAppointmentsResult(
        success=True,
        patient_id=patient_id,
        appointments=items,
    )
