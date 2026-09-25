from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class PatientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: str | None = None
    age: int | None = Field(default=None, ge=0, le=150)
    gender: str | None = Field(default=None, max_length=20)

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
