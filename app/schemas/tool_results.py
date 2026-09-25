from typing import Any
from pydantic import BaseModel, Field

class PatientLookupResult(BaseModel):
    success: bool = True
    exists: bool = False
    patient_id: int | None = None
    patient_name: str | None = None
    phone_number: str | None = None
    error: str | None = None

class PatientCreateResult(BaseModel):
    success: bool = True
    patient_id: int | None = None
    patient_name: str | None = None
    phone_number: str | None = None
    error: str | None = None

class MedicalRoutingToolResult(BaseModel):
    success: bool = True
    specialty: str | None = None
    confidence: str = "high"
    emergency_detected: bool = False
    booking_allowed: bool = True
    escalation_required: bool = False
    normalized_symptoms: list[str] = Field(default_factory=list)
    clarification_cue: str | None = None
    reasoning: str | None = None
    error: str | None = None

class DoctorItem(BaseModel):
    id: int
    name: str
    specialty: str
    status: str = "active"

class DoctorSearchResult(BaseModel):
    success: bool = True
    specialty: str
    doctors: list[DoctorItem] = Field(default_factory=list)
    error: str | None = None

class SlotInfo(BaseModel):
    start_time: str
    end_time: str

class AvailabilityToolResult(BaseModel):
    success: bool = True
    doctor_id: int
    doctor_name: str | None = None
    date: str
    available_slots: list[SlotInfo] = Field(default_factory=list)
    total_available: int = 0
    error: str | None = None

class SlotCheckResult(BaseModel):
    success: bool = True
    available: bool = False
    doctor_id: int
    date: str
    start_time: str
    end_time: str | None = None
    error: str | None = None

class AlternativeSlotsResult(BaseModel):
    success: bool = True
    doctor_id: int
    date: str
    alternatives: list[SlotInfo] = Field(default_factory=list)
    error: str | None = None

class AppointmentItem(BaseModel):
    appointment_id: int
    doctor_id: int
    doctor_name: str | None = None
    appointment_date: str
    start_time: str
    end_time: str
    status: str

class PatientAppointmentsResult(BaseModel):
    success: bool = True
    patient_id: int
    appointments: list[AppointmentItem] = Field(default_factory=list)
    error: str | None = None

class BookingToolResult(BaseModel):
    success: bool = True
    appointment_id: int | None = None
    doctor_id: int | None = None
    doctor_name: str | None = None
    patient_id: int | None = None
    appointment_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    status: str | None = None
    error_code: str | None = None
    error_message: str | None = None

class CancellationToolResult(BaseModel):
    success: bool = True
    appointment_id: int | None = None
    status: str | None = None
    error_code: str | None = None
    error_message: str | None = None

class RescheduleToolResult(BaseModel):
    success: bool = True
    appointment_id: int | None = None
    new_date: str | None = None
    new_start_time: str | None = None
    new_end_time: str | None = None
    status: str | None = None
    error_code: str | None = None
    error_message: str | None = None

class EscalationToolResult(BaseModel):
    success: bool = True
    escalation_type: str
    reason: str
    assigned_team: str
    error: str | None = None
