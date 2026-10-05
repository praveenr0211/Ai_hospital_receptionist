class BookingError(Exception):
    """Base exception for all appointment scheduling and booking errors."""
    pass


class DoctorNotFoundError(BookingError):
    """Raised when the requested doctor does not exist."""
    pass


class DoctorInactiveError(BookingError):
    """Raised when the doctor is inactive or on leave."""
    pass


class PatientNotFoundError(BookingError):
    """Raised when the requested patient does not exist."""
    pass


class ScheduleNotFoundError(BookingError):
    """Raised when no working schedule is found for the doctor on the requested date."""
    pass


class ScheduleOverlapError(BookingError):
    """Raised when multiple schedules for the same doctor overlap in time."""
    pass


class InvalidSlotError(BookingError):
    """Raised when the requested time does not align with the schedule's slot boundary or shift hours."""
    pass


class SlotNotAvailableError(BookingError):
    """Raised when the requested slot is already booked or blocked."""
    pass


class SlotAlreadyBookedError(SlotNotAvailableError):
    """Raised when a concurrency conflict occurs and another caller booked the slot first."""
    pass


class AppointmentNotFoundError(BookingError):
    """Raised when the appointment cannot be found."""
    pass


class AppointmentAlreadyCancelledError(BookingError):
    """Raised when trying to cancel an appointment that is already cancelled."""
    pass
