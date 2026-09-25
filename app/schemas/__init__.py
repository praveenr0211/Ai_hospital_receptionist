from app.schemas.common import ErrorDetail, ErrorResponse, PaginatedResponse
from app.schemas.specialty import SpecialtyBase, SpecialtyResponse, SpecialtyListResponse
from app.schemas.doctor import DoctorBase, DoctorResponse, DoctorListResponse
from app.schemas.patient import PatientBase, PatientCreate, PatientResponse
from app.schemas.schedule import ScheduleItem, DoctorSchedulesResponse
from app.schemas.availability import (
    AvailableSlotItem,
    DoctorAvailabilityResponse,
    SlotCheckResponse,
    AlternativeSlotItem,
    AlternativeSlotsResponse,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentCancel,
    AppointmentReschedule,
    AppointmentResponse,
    AppointmentCancelResponse,
    AppointmentRescheduleResponse,
    DoctorBookedAppointmentItem,
    DoctorBookedAppointmentsResponse,
    AppointmentListResponse,
)
from app.schemas.call import CallCreate, CallResponse, CallListResponse
from app.schemas.dashboard import DashboardSummaryResponse, DashboardDoctorItem, DashboardDoctorsResponse
from app.schemas.agent import ChatRequest, AgentResponse, IntentResult

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    "SpecialtyBase",
    "SpecialtyResponse",
    "SpecialtyListResponse",
    "DoctorBase",
    "DoctorResponse",
    "DoctorListResponse",
    "PatientBase",
    "PatientCreate",
    "PatientResponse",
    "ScheduleItem",
    "DoctorSchedulesResponse",
    "AvailableSlotItem",
    "DoctorAvailabilityResponse",
    "SlotCheckResponse",
    "AlternativeSlotItem",
    "AlternativeSlotsResponse",
    "AppointmentCreate",
    "AppointmentCancel",
    "AppointmentReschedule",
    "AppointmentResponse",
    "AppointmentCancelResponse",
    "AppointmentRescheduleResponse",
    "DoctorBookedAppointmentItem",
    "DoctorBookedAppointmentsResponse",
    "AppointmentListResponse",
    "CallCreate",
    "CallResponse",
    "CallListResponse",
    "DashboardSummaryResponse",
    "DashboardDoctorItem",
    "DashboardDoctorsResponse",
    "ChatRequest",
    "AgentResponse",
    "IntentResult",
]
