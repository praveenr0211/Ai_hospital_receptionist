import logging
from app.schemas.medical_routing import (
    MedicalRoutingResponse,
    RoutingConfidence,
    UrgencyLevel,
)
from app.services.medical.normalization_service import normalize_symptoms, is_vague_complaint
from app.services.medical.emergency_service import detect_emergencies
from app.services.medical.specialty_mapper import map_symptoms_to_specialties
from app.services.medical.safety_service import evaluate_safety
from app.services.medical.escalation_service import determine_escalation

logger = logging.getLogger("medical_routing")

def route_symptoms(
    symptom_text: str,
    patient_id: int | None = None,
    call_id: int | None = None
) -> MedicalRoutingResponse:
    """
    Main entry point for Phase 4 Medical Routing and Safety Engine.
    
    Orchestrates:
    1. Deterministic symptom normalization
    2. Emergency and red-flag screening
    3. Specialty mapping and confidence calculation
    4. Clinical safety decision
    5. Human escalation determination
    
    Does NOT diagnose the patient. Does NOT book appointments or mutate DB.
    """
    logger.info(f"ROUTING_REQUEST: patient_id={patient_id}, call_id={call_id}")

    # 1. Normalization
    normalized = normalize_symptoms(symptom_text)
    is_vague = is_vague_complaint(symptom_text)
    logger.info(f"SYMPTOM_NORMALIZED: terms={normalized.normalized_terms}, body_area={normalized.body_area}")

    # 2. Emergency Screening
    emergency_info = detect_emergencies(symptom_text)

    # 3. Emergency fast-path: If critical red flags matched, halt routine booking immediately
    if emergency_info["emergency_detected"]:
        logger.warning(f"EMERGENCY_RULE_MATCHED: rules={emergency_info['matched_rules']}")
        safety = evaluate_safety(
            emergency_detected=True,
            urgency_str="emergency",
            confidence=RoutingConfidence.HIGH,
            clarification_required=False,
            matched_emergency_rules=emergency_info["matched_rules"]
        )
        escalation = determine_escalation(
            raw_text=symptom_text,
            safety_decision=safety,
            emergency_priority=emergency_info["priority"]
        )

        return MedicalRoutingResponse(
            normalized_symptoms=normalized.normalized_terms,
            possible_specialties=[],
            selected_specialty=None,
            confidence=RoutingConfidence.HIGH,
            urgency=UrgencyLevel.EMERGENCY,
            emergency_detected=True,
            booking_allowed=False,
            escalation_required=True,
            clarification_required=False,
            clarification_question=None,
            safety_message=emergency_info["safety_message"],
            matched_rules=emergency_info["matched_rules"]
        )

    # 4. Specialty Mapping
    mapping_info = map_symptoms_to_specialties(normalized.normalized_terms, is_vague=is_vague)
    confidence = RoutingConfidence(mapping_info["confidence"])
    if confidence == RoutingConfidence.HIGH and mapping_info["selected_specialty"]:
        logger.info(f"SPECIALTY_SELECTED: specialty={mapping_info['selected_specialty']}")
    elif confidence == RoutingConfidence.LOW:
        logger.info("ROUTING_LOW_CONFIDENCE: clarification requested")

    # 5. Safety Evaluation
    safety = evaluate_safety(
        emergency_detected=False,
        urgency_str=emergency_info["urgency"],
        confidence=confidence,
        clarification_required=mapping_info["clarification_required"],
        matched_emergency_rules=emergency_info["matched_rules"]
    )

    # 6. Escalation Determination
    escalation = determine_escalation(
        raw_text=symptom_text,
        safety_decision=safety,
        emergency_priority=emergency_info["priority"]
    )
    if escalation.required:
        logger.info(f"ESCALATION_TRIGGERED: reason={escalation.reason}")

    all_matched_rules = emergency_info["matched_rules"] + mapping_info["matched_rules"]

    return MedicalRoutingResponse(
        normalized_symptoms=normalized.normalized_terms,
        possible_specialties=mapping_info["possible_specialties"],
        selected_specialty=mapping_info["selected_specialty"],
        confidence=confidence,
        urgency=safety.urgency,
        emergency_detected=False,
        booking_allowed=safety.booking_allowed,
        escalation_required=escalation.required,
        clarification_required=mapping_info["clarification_required"],
        clarification_question=mapping_info["clarification_question"],
        safety_message=safety.reason if not safety.booking_allowed else None,
        matched_rules=all_matched_rules
    )
