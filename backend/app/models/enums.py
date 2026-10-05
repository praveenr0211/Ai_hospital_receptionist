import enum

class DoctorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"

class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

class NotificationChannel(str, enum.Enum):
    SMS = "SMS"
    WHATSAPP = "WhatsApp"
    EMAIL = "Email"

class CallOutcome(str, enum.Enum):
    APPOINTMENT_BOOKED = "appointment_booked"
    INFORMATION_PROVIDED = "information_provided"
    HUMAN_TRANSFER = "human_transfer"
    CANCELLED = "cancelled"
    FAILED = "failed"
    ABANDONED = "abandoned"
