from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.doctor import Doctor, DoctorStatus
from app.models.specialty import Specialty
from app.schemas.tool_results import DoctorSearchResult, DoctorItem

def find_doctors_by_specialty(db: Session, specialty: str) -> DoctorSearchResult:
    """Find all active doctors for a given medical specialty."""
    clean_spec = specialty.strip()
    doctors = db.scalars(
        select(Doctor)
        .join(Doctor.specialty)
        .where(
            Specialty.name.ilike(clean_spec),
            Doctor.status == DoctorStatus.ACTIVE,
        )
        .order_by(Doctor.name.asc())
    ).all()

    doctor_items = [
        DoctorItem(
            id=doc.id,
            name=doc.name,
            specialty=doc.specialty.name if doc.specialty else clean_spec,
            status=doc.status.value,
        )
        for doc in doctors
    ]

    return DoctorSearchResult(
        success=True,
        specialty=clean_spec,
        doctors=doctor_items,
    )
