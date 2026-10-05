from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_doctors: int
    active_doctors: int
    total_patients: int
    appointments_today: int
    confirmed_appointments: int
    cancelled_appointments: int
    calls_today: int
    successful_bookings_today: int
    escalated_calls_today: int

class DashboardDoctorItem(BaseModel):
    doctor_id: int
    doctor_name: str
    specialty: str
    appointments_today: int
    completed: int
    upcoming: int

class DashboardDoctorsResponse(BaseModel):
    doctors: list[DashboardDoctorItem]
