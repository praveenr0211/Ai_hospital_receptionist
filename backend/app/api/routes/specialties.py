from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models import Specialty
from app.schemas.specialty import SpecialtyResponse, SpecialtyListResponse

router = APIRouter(prefix="/specialties", tags=["Specialties"])

@router.get("", response_model=SpecialtyListResponse, summary="List Medical Specialties")
def list_specialties(db: Session = Depends(get_db)):
    specialties = db.scalars(select(Specialty).order_by(Specialty.name)).all()
    total = db.scalar(select(func.count(Specialty.id))) or 0
    return {
        "items": specialties,
        "total": total
    }

@router.get("/{specialty_id}", response_model=SpecialtyResponse, summary="Get Specialty Details")
def get_specialty(specialty_id: int, db: Session = Depends(get_db)):
    specialty = db.scalars(select(Specialty).where(Specialty.id == specialty_id)).first()
    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specialty with ID {specialty_id} not found."
        )
    return specialty
