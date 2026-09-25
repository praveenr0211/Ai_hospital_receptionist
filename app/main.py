from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import api_v1_router
from app.services.exceptions import (
    DoctorNotFoundError,
    PatientNotFoundError,
    ScheduleNotFoundError,
    AppointmentNotFoundError,
    InvalidSlotError,
    SlotNotAvailableError,
    SlotAlreadyBookedError,
    AppointmentAlreadyCancelledError,
    DoctorInactiveError,
    ScheduleOverlapError,
    BookingError,
)

app = FastAPI(
    title="Hospital AI Receptionist API",
    version="1.0.0",
    description="REST API layer exposing deterministic scheduling, dynamic availability, and booking workflows for AI agents and hospital dashboards.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# -------------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------------
# Allow local dashboard and developer dev servers
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# Domain Exception Handlers (Standard Error Envelope)
# -------------------------------------------------------------

def build_error_response(status_code: int, code: str, message: str, details=None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details
            }
        }
    )


@app.exception_handler(DoctorNotFoundError)
async def doctor_not_found_handler(request: Request, exc: DoctorNotFoundError):
    return build_error_response(status.HTTP_404_NOT_FOUND, "DOCTOR_NOT_FOUND", str(exc))


@app.exception_handler(PatientNotFoundError)
async def patient_not_found_handler(request: Request, exc: PatientNotFoundError):
    return build_error_response(status.HTTP_404_NOT_FOUND, "PATIENT_NOT_FOUND", str(exc))


@app.exception_handler(ScheduleNotFoundError)
async def schedule_not_found_handler(request: Request, exc: ScheduleNotFoundError):
    return build_error_response(status.HTTP_404_NOT_FOUND, "SCHEDULE_NOT_FOUND", str(exc))


@app.exception_handler(AppointmentNotFoundError)
async def appointment_not_found_handler(request: Request, exc: AppointmentNotFoundError):
    return build_error_response(status.HTTP_404_NOT_FOUND, "APPOINTMENT_NOT_FOUND", str(exc))


@app.exception_handler(InvalidSlotError)
async def invalid_slot_handler(request: Request, exc: InvalidSlotError):
    return build_error_response(status.HTTP_400_BAD_REQUEST, "INVALID_SLOT", str(exc))


@app.exception_handler(SlotAlreadyBookedError)
async def slot_already_booked_handler(request: Request, exc: SlotAlreadyBookedError):
    return build_error_response(status.HTTP_409_CONFLICT, "SLOT_ALREADY_BOOKED", str(exc))


@app.exception_handler(SlotNotAvailableError)
async def slot_not_available_handler(request: Request, exc: SlotNotAvailableError):
    return build_error_response(status.HTTP_409_CONFLICT, "SLOT_NOT_AVAILABLE", str(exc))


@app.exception_handler(AppointmentAlreadyCancelledError)
async def appointment_already_cancelled_handler(request: Request, exc: AppointmentAlreadyCancelledError):
    return build_error_response(status.HTTP_409_CONFLICT, "APPOINTMENT_ALREADY_CANCELLED", str(exc))


@app.exception_handler(DoctorInactiveError)
async def doctor_inactive_handler(request: Request, exc: DoctorInactiveError):
    return build_error_response(status.HTTP_409_CONFLICT, "DOCTOR_INACTIVE", str(exc))


@app.exception_handler(ScheduleOverlapError)
async def schedule_overlap_handler(request: Request, exc: ScheduleOverlapError):
    return build_error_response(status.HTTP_409_CONFLICT, "SCHEDULE_OVERLAP", str(exc))


@app.exception_handler(BookingError)
async def generic_booking_error_handler(request: Request, exc: BookingError):
    return build_error_response(status.HTTP_400_BAD_REQUEST, "BOOKING_ERROR", str(exc))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return build_error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "VALIDATION_ERROR",
        "Request body or parameters failed validation.",
        details=exc.errors()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return build_error_response(
        exc.status_code,
        "HTTP_ERROR",
        exc.detail
    )


# -------------------------------------------------------------
# Router Inclusion
# -------------------------------------------------------------
app.include_router(api_v1_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "Hospital AI Receptionist API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
