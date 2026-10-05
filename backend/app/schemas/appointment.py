from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    start_time: time
    reason: str | None = None

class AppointmentCancel(BaseModel):
    reason: str | None = Field(default=None, description="Reason for cancellation")

class AppointmentReschedule(BaseModel):
    new_date: date
    new_start_time: time

class AppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    specialty: str | None = None
    date: str
    start_time: str
    end_time: str
    status: str
    reason: str | None = None
    cancellation_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)

class AppointmentCancelResponse(BaseModel):
    appointment_id: int
    status: str
    cancellation_reason: str | None = None
    message: str

class AppointmentRescheduleResponse(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    previous_date: str
    previous_time: str
    new_date: str
    new_start_time: str
    new_end_time: str
    status: str
    message: str

class DoctorBookedAppointmentItem(BaseModel):
    appointment_id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    date: str
    start_time: str
    end_time: str
    reason: str | None = None
    status: str

class DoctorBookedAppointmentsResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    appointments: list[DoctorBookedAppointmentItem]
    total: int
    page: int
    page_size: int

class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
    total: int
    page: int
    page_size: int
