from datetime import date
from pydantic import BaseModel, Field

class AvailableSlotItem(BaseModel):
    start_time: str
    end_time: str
    available: bool

class DoctorAvailabilityResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    date: str
    total_slots: int
    available_count: int
    slots: list[AvailableSlotItem]

class SlotCheckResponse(BaseModel):
    available: bool
    doctor_id: int
    doctor_name: str
    date: str
    start_time: str
    end_time: str | None = None
    schedule_id: int | None = None
    reason: str | None = None

class AlternativeSlotItem(BaseModel):
    start_time: str
    end_time: str

class AlternativeSlotsResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    date: str
    requested_time: str
    available: bool
    alternatives: list[str] = Field(default_factory=list, description="List of start times for nearest available slots")
