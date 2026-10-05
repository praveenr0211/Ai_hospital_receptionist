from fastapi import APIRouter, status
from app.schemas.medical_routing import MedicalRoutingRequest, MedicalRoutingResponse
from app.services.medical.routing_service import route_symptoms

router = APIRouter(prefix="/medical-routing", tags=["Medical Routing & Safety"])

@router.post(
    "",
    response_model=MedicalRoutingResponse,
    status_code=status.HTTP_200_OK,
    summary="Route Symptoms to Medical Specialty with Safety Triage",
    description="Evaluates patient symptom descriptions, normalizes concepts, detects emergency red flags, and determines clinical specialty routing without diagnosing the patient or mutating database state."
)
def route_patient_symptoms(payload: MedicalRoutingRequest) -> MedicalRoutingResponse:
    return route_symptoms(
        symptom_text=payload.symptom_text,
        patient_id=payload.patient_id,
        call_id=payload.call_id
    )
