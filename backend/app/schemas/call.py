from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import CallOutcome

class CallCreate(BaseModel):
    patient_id: int | None = None
    phone_number: str = Field(..., min_length=10, max_length=20)
    intent: str = Field(..., max_length=100)
    specialty_detected: str | None = None
    duration_seconds: int = 0
    outcome: CallOutcome = CallOutcome.APPOINTMENT_BOOKED
    escalated: bool = False
    started_at: datetime | None = None
    ended_at: datetime | None = None

class CallResponse(BaseModel):
    id: int
    patient_id: int | None = None
    phone_number: str
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int
    intent: str
    specialty_detected: str | None = None
    outcome: str
    escalated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CallListResponse(BaseModel):
    items: list[CallResponse]
    total: int
    page: int
    page_size: int
