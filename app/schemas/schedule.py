from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field

class ScheduleItem(BaseModel):
    id: int
    start_time: str
    end_time: str
    slot_duration_minutes: int
    status: str = "active"

    model_config = ConfigDict(from_attributes=True)

class DoctorSchedulesResponse(BaseModel):
    doctor_id: int
    doctor_name: str | None = None
    date: str | None = None
    schedules: list[ScheduleItem] = Field(default_factory=list)
