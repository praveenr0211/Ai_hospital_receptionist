from pydantic import BaseModel, ConfigDict
from app.schemas.specialty import SpecialtyResponse

class DoctorBase(BaseModel):
    name: str
    qualification: str | None = None
    experience_years: int = 0
    consultation_fee: float = 0.0
    phone: str | None = None
    email: str | None = None
    status: str = "active"

class DoctorResponse(DoctorBase):
    id: int
    specialty_id: int
    specialty: SpecialtyResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class DoctorListResponse(BaseModel):
    items: list[DoctorResponse]
    total: int
    page: int
    page_size: int
