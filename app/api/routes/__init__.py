from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.specialties import router as specialties_router
from app.api.routes.doctors import router as doctors_router
from app.api.routes.patients import router as patients_router
from app.api.routes.schedules import router as schedules_router
from app.api.routes.availability import router as availability_router
from app.api.routes.appointments import router as appointments_router
from app.api.routes.calls import router as calls_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.medical_routing import router as medical_routing_router
from app.api.routes.agent import router as agent_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(specialties_router)
api_v1_router.include_router(doctors_router)
api_v1_router.include_router(patients_router)
api_v1_router.include_router(schedules_router)
api_v1_router.include_router(availability_router)
api_v1_router.include_router(appointments_router)
api_v1_router.include_router(calls_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(medical_routing_router)
api_v1_router.include_router(agent_router)

