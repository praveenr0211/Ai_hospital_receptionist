from datetime import date, datetime
from typing import Any, Tuple
from sqlalchemy.orm import Session

from app.agent.state import ReceptionistState
from app.agent.prompts import (
    EMERGENCY_TEMPLATE,
    CLARIFICATION_TEMPLATE,
    format_slots_message,
    format_confirmation_request,
    format_cancellation_confirmation,
    format_reschedule_confirmation,
)
from app.agent.policies import parse_user_confirmation, is_tool_allowed
from app.agent.llm import (
    classify_intent,
    extract_phone_number,
    extract_time_str,
    extract_date_str,
)
from app.agent.tools import (
    find_patient_by_phone,
    create_patient,
    get_patient_appointments,
    route_medical_symptoms,
    find_doctors_by_specialty,
    check_doctor_availability,
    check_specific_slot,
    find_alternative_slots,
    book_appointment_tool,
    cancel_appointment_tool,
    reschedule_appointment_tool,
    request_human_escalation,
)
from app.schemas.agent import ActionRequired, AgentResponse

def node_greeting(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    clean = user_message.strip().lower()
    simple_greetings = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"}
    words = clean.split()
    if clean in simple_greetings or (len(words) <= 3 and any(w in simple_greetings for w in words) and not any(w in {"appointment", "doctor", "cancel", "reschedule", "human", "pain", "breathe", "emergency", "sick", "see"} for w in words)):
        state.current_state = "UNDERSTAND_INTENT"
        return (
            "Hello, thank you for calling City General Hospital. I am your AI hospital receptionist. How can I help you today?",
            "USER_INPUT",
        )
    state.current_state = "UNDERSTAND_INTENT"
    return node_understand_intent(state, user_message, db)

def node_identify_patient(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    phone = extract_phone_number(user_message) or state.patient_phone
    if phone:
        lookup = find_patient_by_phone(db, phone)
        if lookup.exists:
            state.patient_id = lookup.patient_id
            state.patient_name = lookup.patient_name
            state.patient_phone = lookup.phone_number
        else:
            # Create a patient record with the available phone
            c_res = create_patient(db, name="Patient", phone_number=phone)
            state.patient_id = c_res.patient_id
            state.patient_name = c_res.patient_name
            state.patient_phone = c_res.phone_number
        
        # Patient is identified; proceed to understand intent or collect symptoms
        if state.symptom_text:
            state.current_state = "MEDICAL_ROUTING"
            return node_medical_routing(state, user_message, db)
        state.current_state = "UNDERSTAND_INTENT"
        return ("Thank you. What symptoms are you experiencing or how can I assist you with your appointment?", "USER_INPUT")
    
    return ("Could you please provide your phone number so I can locate or create your patient file?", "USER_INPUT")

def node_understand_intent(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    intent_res = classify_intent(user_message, state.current_state)
    state.intent = intent_res.intent
    state.intent_confidence = intent_res.confidence

    if intent_res.intent == "EMERGENCY":
        state.current_state = "EMERGENCY_HANDLING"
        return node_emergency_handling(state, user_message, db)

    if intent_res.intent == "HUMAN_AGENT":
        state.current_state = "HUMAN_ESCALATION"
        return node_human_escalation(state, user_message, db)

    if intent_res.intent == "CANCEL_APPOINTMENT":
        state.current_state = "CANCEL_APPOINTMENT"
        return node_cancel_appointment(state, user_message, db)

    if intent_res.intent == "RESCHEDULE_APPOINTMENT":
        state.current_state = "RESCHEDULE_APPOINTMENT"
        return node_reschedule_appointment(state, user_message, db)

    if intent_res.intent in {"BOOK_APPOINTMENT", "CHECK_AVAILABILITY"}:
        # If user provided symptoms in this message
        if intent_res.extracted_entities.get("symptom_cue") or len(user_message.split()) > 3:
            state.symptom_text = user_message
            state.current_state = "MEDICAL_ROUTING"
            return node_medical_routing(state, user_message, db)
        else:
            state.current_state = "COLLECT_SYMPTOMS"
            return ("Sure, I can help you with that. Could you tell me what symptoms you are experiencing?", "USER_INPUT")

    if intent_res.intent == "DOCTOR_INFORMATION":
        return ("Our hospital has specialists in Cardiology, Dentistry, Dermatology, Orthopedics, Neurology, Pediatrics, ENT, and General Medicine. Which specialty or doctor would you like to know more about?", "USER_INPUT")

    if intent_res.intent == "GENERAL_HOSPITAL_QUERY":
        return ("City General Hospital is located at 123 Healthcare Blvd, open 24/7 for emergency care and 8:00 AM to 8:00 PM for OPD consultations. Would you like to schedule an appointment?", "USER_INPUT")

    return ("I'd be glad to assist you. Are you looking to book an appointment, reschedule, cancel, or speak with hospital staff?", "USER_INPUT")

def node_collect_symptoms(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    state.symptom_text = user_message
    state.current_state = "MEDICAL_ROUTING"
    return node_medical_routing(state, user_message, db)

def node_medical_routing(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    symptom_text = state.symptom_text or user_message
    res = route_medical_symptoms(symptom_text)
    
    state.specialty = res.specialty
    state.routing_confidence = res.confidence
    state.emergency_detected = res.emergency_detected
    state.escalation_required = res.escalation_required
    state.normalized_symptoms = res.normalized_symptoms
    state.clarification_cue = res.clarification_cue

    if res.emergency_detected:
        state.current_state = "EMERGENCY_HANDLING"
        return node_emergency_handling(state, user_message, db)

    if res.clarification_cue or res.confidence == "low" or not res.specialty:
        state.current_state = "CLARIFICATION"
        cue = res.clarification_cue or CLARIFICATION_TEMPLATE
        return (cue, "USER_INPUT")

    if not res.booking_allowed:
        state.current_state = "HUMAN_ESCALATION"
        return (res.reasoning or "We cannot proceed with automated booking for this request. Connecting to staff.", "HUMAN_ESCALATION")

    # Routing successful -> find doctors
    state.current_state = "FIND_DOCTOR"
    return node_find_doctor(state, user_message, db)

def node_clarification(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    # Concrete clarification supersedes vague previous symptom
    state.symptom_text = user_message.strip()
    state.current_state = "MEDICAL_ROUTING"
    return node_medical_routing(state, user_message, db)

def node_emergency_handling(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    state.emergency_detected = True
    state.escalation_required = True
    state.escalation_reason = "Emergency clinical red-flag detected"
    request_human_escalation(
        reason=state.escalation_reason,
        escalation_type="EMERGENCY",
    )
    state.current_state = "HUMAN_ESCALATION"
    return (EMERGENCY_TEMPLATE, "HUMAN_ESCALATION")

def node_find_doctor(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    if not state.specialty:
        state.current_state = "COLLECT_SYMPTOMS"
        return ("Could you tell me what symptoms you have so I can find the right specialist?", "USER_INPUT")

    docs = find_doctors_by_specialty(db, state.specialty)
    if not docs.doctors:
        state.current_state = "HUMAN_ESCALATION"
        return (
            f"We do not currently have an active doctor for {state.specialty}. Let me connect you with our hospital staff.",
            "HUMAN_ESCALATION",
        )

    # Pick the primary active doctor or matching doctor
    doctor = docs.doctors[0]
    state.doctor_id = doctor.id
    state.doctor_name = doctor.name
    state.candidate_doctors = [d.model_dump() for d in docs.doctors]

    state.current_state = "CHECK_AVAILABILITY"
    return node_check_availability(state, user_message, db)

def node_check_availability(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    # Extract requested date or default to a near date
    extracted_date = extract_date_str(user_message)
    target_date = extracted_date or state.appointment_date or date.today().isoformat()
    state.appointment_date = target_date

    res = check_doctor_availability(db, state.doctor_id, target_date)
    state.available_slots = [s.model_dump() for s in res.available_slots]

    if not state.available_slots:
        # Check if next day has slots or let user choose
        state.current_state = "OFFER_SLOTS"
        return (
            f"Dr. {state.doctor_name} does not have open slots on {target_date}. Would you like to check tomorrow or another date?",
            "USER_INPUT",
        )

    state.current_state = "OFFER_SLOTS"
    # If the user already specified a time in their message, try to evaluate it immediately
    requested_time = extract_time_str(user_message)
    if requested_time:
        return node_offer_slots(state, requested_time, db)

    msg = format_slots_message(state.doctor_name, target_date, state.available_slots)
    return (
        f"{state.specialty} is the appropriate department. {msg}",
        "USER_INPUT",
    )

def node_offer_slots(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    req_time = extract_time_str(user_message) or state.requested_time
    if not req_time:
        # User didn't give a time, re-prompt with slots
        msg = format_slots_message(state.doctor_name, state.appointment_date, state.available_slots)
        return (msg, "USER_INPUT")

    state.requested_time = req_time

    # Validate slot availability with tool
    check = check_specific_slot(db, state.doctor_id, state.appointment_date, req_time)
    if check.available:
        state.selected_slot = {
            "start_time": check.start_time,
            "end_time": check.end_time or "",
        }
        state.awaiting_confirmation = True
        state.confirmation_intent = "BOOKING"
        state.current_state = "WAIT_CONFIRMATION"
        msg = format_confirmation_request(state.doctor_name, state.appointment_date, check.start_time)
        return (msg, "CONFIRMATION_REQUIRED")
    else:
        # Find alternative slots
        alts = find_alternative_slots(db, state.doctor_id, state.appointment_date, req_time)
        if alts.alternatives:
            alt_list = ", ".join([a.start_time for a in alts.alternatives])
            return (
                f"{req_time} is not available. I can offer the following nearby times: {alt_list}. Which would you prefer?",
                "USER_INPUT",
            )
        return (
            f"{req_time} is not available with Dr. {state.doctor_name} on {state.appointment_date}. Would you like to check another date?",
            "USER_INPUT",
        )

def node_wait_confirmation(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    confirmed = parse_user_confirmation(user_message, state.confirmation_intent)

    if confirmed is True:
        state.awaiting_confirmation = False
        if state.confirmation_intent == "CANCELLATION":
            state.current_state = "END"
            c_res = cancel_appointment_tool(db, state.existing_appointment_id)
            if c_res.success:
                return (
                    f"Your appointment #{state.existing_appointment_id} with Dr. {state.doctor_name or ''} has been successfully cancelled.",
                    "COMPLETED",
                )
            return (f"Failed to cancel appointment: {c_res.error_message}. Connecting to staff.", "HUMAN_ESCALATION")

        elif state.confirmation_intent == "RESCHEDULE":
            state.current_state = "END"
            r_res = reschedule_appointment_tool(db, state.existing_appointment_id, state.appointment_date, state.requested_time)
            if r_res.success:
                return (
                    f"Your appointment has been successfully rescheduled to {state.appointment_date} at {state.requested_time} with Dr. {state.doctor_name or ''}.",
                    "COMPLETED",
                )
            return (f"Failed to reschedule: {r_res.error_message}. Connecting to staff.", "HUMAN_ESCALATION")

        else:
            state.current_state = "BOOK_APPOINTMENT"
            return node_book_appointment(state, user_message, db)

    elif confirmed is False:
        state.awaiting_confirmation = False
        state.selected_slot = None
        state.current_state = "OFFER_SLOTS"
        return ("No problem, I have not confirmed that appointment. What time or date would you prefer instead?", "USER_INPUT")

    # Ambiguous or non-committal answer
    return (
        f"Would you like me to book the appointment with Dr. {state.doctor_name} at {state.requested_time}? Please reply with yes or no.",
        "CONFIRMATION_REQUIRED",
    )

def node_book_appointment(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    # Tool permission boundary check
    if not is_tool_allowed("BOOK_APPOINTMENT", "book_appointment_tool"):
        return ("Error: Booking tool is not permitted in this state.", "USER_INPUT")

    # Ensure patient ID exists
    if not state.patient_id:
        phone = state.patient_phone or "9876543210"
        name = state.patient_name or "Patient"
        p_res = create_patient(db, name=name, phone_number=phone)
        state.patient_id = p_res.patient_id

    slot_time = state.selected_slot["start_time"] if state.selected_slot else state.requested_time

    res = book_appointment_tool(
        db=db,
        patient_id=state.patient_id,
        doctor_id=state.doctor_id,
        appointment_date=state.appointment_date,
        start_time=slot_time,
        reason=state.symptom_text,
    )

    if res.success:
        state.appointment_id = res.appointment_id
        state.current_state = "BOOKING_COMPLETE"
        return (
            f"Your appointment with Dr. {state.doctor_name} has been confirmed for {state.appointment_date} at {slot_time}. "
            f"Your appointment confirmation number is #{res.appointment_id}. Is there anything else I can help you with?",
            "COMPLETED",
        )
    elif res.error_code == "SLOT_ALREADY_BOOKED":
        # Handle race condition gracefully
        state.current_state = "OFFER_SLOTS"
        alts = find_alternative_slots(db, state.doctor_id, state.appointment_date, slot_time)
        alt_times = ", ".join([a.start_time for a in alts.alternatives]) if alts.alternatives else "none"
        return (
            f"I apologize, but that slot was just booked by another patient. Here are the closest available times: {alt_times}. Which would you prefer?",
            "USER_INPUT",
        )
    else:
        return (
            f"I encountered an issue confirming your booking: {res.error_message}. Let me connect you with our hospital staff.",
            "HUMAN_ESCALATION",
        )

def node_cancel_appointment(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    # Ensure patient identified
    if not state.patient_id:
        phone = extract_phone_number(user_message) or state.patient_phone
        if phone:
            lookup = find_patient_by_phone(db, phone)
            if lookup.exists:
                state.patient_id = lookup.patient_id
                state.patient_phone = lookup.phone_number
        if not state.patient_id:
            return ("To help cancel your appointment, could you please provide your phone number?", "USER_INPUT")

    # Fetch active appointments
    apts_res = get_patient_appointments(db, state.patient_id)
    if not apts_res.appointments:
        state.current_state = "END"
        return ("I checked our records, but there are no upcoming scheduled appointments under your phone number.", "COMPLETED")

    target_apt = apts_res.appointments[0]
    state.existing_appointment_id = target_apt.appointment_id

    # If not yet awaiting confirmation, request confirmation
    if not state.awaiting_confirmation:
        state.awaiting_confirmation = True
        state.confirmation_intent = "CANCELLATION"
        state.current_state = "WAIT_CONFIRMATION"
        msg = format_cancellation_confirmation(target_apt.doctor_name, target_apt.appointment_date, target_apt.start_time)
        return (msg, "CONFIRMATION_REQUIRED")

    # Execute cancellation tool
    c_res = cancel_appointment_tool(db, target_apt.appointment_id)
    state.awaiting_confirmation = False
    if c_res.success:
        state.current_state = "END"
        return (f"Your appointment #{target_apt.appointment_id} with Dr. {target_apt.doctor_name} has been successfully cancelled.", "COMPLETED")
    return (f"Failed to cancel appointment: {c_res.error_message}. Connecting you with support.", "HUMAN_ESCALATION")

def node_reschedule_appointment(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    # Ensure patient identified
    if not state.patient_id:
        phone = extract_phone_number(user_message) or state.patient_phone
        if phone:
            lookup = find_patient_by_phone(db, phone)
            if lookup.exists:
                state.patient_id = lookup.patient_id
                state.patient_phone = lookup.phone_number
        if not state.patient_id:
            return ("To reschedule your appointment, could you please provide your phone number?", "USER_INPUT")

    apts_res = get_patient_appointments(db, state.patient_id)
    if not apts_res.appointments:
        state.current_state = "END"
        return ("I did not find any active appointments to reschedule under your record.", "COMPLETED")

    target_apt = apts_res.appointments[0]
    state.existing_appointment_id = target_apt.appointment_id
    state.doctor_id = target_apt.doctor_id
    state.doctor_name = target_apt.doctor_name

    # Check for requested new date and time
    req_date = extract_date_str(user_message) or state.appointment_date or target_apt.appointment_date
    req_time = extract_time_str(user_message)

    if not req_time:
        state.appointment_date = req_date
        res = check_doctor_availability(db, target_apt.doctor_id, req_date)
        state.available_slots = [s.model_dump() for s in res.available_slots]
        times = ", ".join([s.start_time for s in res.available_slots[:5]])
        return (f"What time would you prefer on {req_date}? Dr. {target_apt.doctor_name} has slots at: {times}.", "USER_INPUT")

    state.appointment_date = req_date
    state.requested_time = req_time

    if not state.awaiting_confirmation:
        # Check slot availability first
        check = check_specific_slot(db, target_apt.doctor_id, req_date, req_time)
        if not check.available:
            alts = find_alternative_slots(db, target_apt.doctor_id, req_date, req_time)
            alt_times = ", ".join([a.start_time for a in alts.alternatives]) if alts.alternatives else "none"
            return (f"{req_time} is not available on {req_date}. Alternatives: {alt_times}. Which time would you prefer?", "USER_INPUT")

        state.awaiting_confirmation = True
        state.confirmation_intent = "RESCHEDULE"
        state.current_state = "WAIT_CONFIRMATION"
        msg = format_reschedule_confirmation(target_apt.doctor_name, req_date, req_time)
        return (msg, "CONFIRMATION_REQUIRED")

    # User confirmed reschedule
    r_res = reschedule_appointment_tool(db, target_apt.appointment_id, req_date, req_time)
    state.awaiting_confirmation = False
    if r_res.success:
        state.current_state = "END"
        return (f"Your appointment has been successfully rescheduled to {req_date} at {req_time} with Dr. {target_apt.doctor_name}.", "COMPLETED")
    return (f"Failed to reschedule: {r_res.error_message}. Connecting to staff.", "HUMAN_ESCALATION")

def node_human_escalation(state: ReceptionistState, user_message: str, db: Session) -> Tuple[str, ActionRequired]:
    state.escalation_required = True
    request_human_escalation(reason="Patient requested human agent or transfer required", escalation_type="HUMAN_REQUEST")
    state.current_state = "END"
    return ("I am transferring you to a member of our hospital patient care team. Please hold on.", "HUMAN_ESCALATION")
