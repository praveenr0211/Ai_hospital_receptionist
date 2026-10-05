"""Prompts and natural language phrasing templates for the AI Hospital Receptionist."""

SYSTEM_PROMPT = """You are an intelligent, professional, and empathetic AI Hospital Receptionist.
Your core responsibilities:
1. Understand the patient's intent and symptoms with empathy.
2. Rely entirely on deterministic medical and hospital scheduling tools.
3. NEVER diagnose medical conditions or recommend medications.
4. If emergency symptoms are flagged, immediately prioritize patient safety, advise emergency care, and escalate.
5. NEVER invent doctors, dates, times, or available slots. Only offer slots confirmed by availability tools.
6. NEVER book an appointment without explicit, confirmed patient agreement.
7. Be polite, clear, concise, and reassuring.
"""

INTENT_SYSTEM_PROMPT = """Analyze the user's message in a hospital receptionist context.
Classify the intent into one of:
- BOOK_APPOINTMENT: Patient wants to book or see a doctor or mentions medical symptoms.
- CHECK_AVAILABILITY: Patient asks about doctor timings, schedule, or availability.
- CANCEL_APPOINTMENT: Patient requests to cancel an appointment.
- RESCHEDULE_APPOINTMENT: Patient requests to move or reschedule an appointment.
- DOCTOR_INFORMATION: Patient asks about doctor qualifications, fees, or specialties.
- GENERAL_HOSPITAL_QUERY: Patient asks about hospital location, hours, or general non-appointment queries.
- HUMAN_AGENT: Patient explicitly asks to speak to a person, receptionist, or operator.
- EMERGENCY: Patient expresses severe, life-threatening symptoms (chest pain, severe breathing difficulty, stroke).
- UNKNOWN: Ambiguous, unrelated, or unrecognizable input.
"""

EMERGENCY_TEMPLATE = (
    "The symptoms you are describing may indicate a medical emergency requiring urgent attention. "
    "For your safety, I cannot schedule a routine appointment for these symptoms. "
    "Please seek immediate emergency medical care or call emergency services (such as 911 or 112) right away. "
    "I am also connecting you with our hospital emergency triage staff."
)

CLARIFICATION_TEMPLATE = (
    "Could you provide a little more detail about your symptoms, such as how long you have experienced them "
    "and whether you have any accompanying symptoms?"
)

def _clean_doc_name(name: str) -> str:
    n = (name or "").strip()
    return n if n.startswith("Dr.") else f"Dr. {n}"

def format_slots_message(doctor_name: str, date_str: str, slots: list[dict[str, str]]) -> str:
    doc = _clean_doc_name(doctor_name)
    if not slots:
        return f"{doc} has no available appointments on {date_str}."
    times_list = ", ".join([s["start_time"] for s in slots[:5]])
    return (
        f"{doc} has the following available slots on {date_str}: {times_list}. "
        "Which time would work best for you?"
    )

def format_confirmation_request(doctor_name: str, date_str: str, time_str: str) -> str:
    doc = _clean_doc_name(doctor_name)
    return (
        f"I can book an appointment for you with {doc} on {date_str} at {time_str}. "
        "Would you like me to confirm this booking?"
    )

def format_cancellation_confirmation(doctor_name: str, date_str: str, time_str: str) -> str:
    doc = _clean_doc_name(doctor_name)
    return (
        f"I found your appointment with {doc} on {date_str} at {time_str}. "
        "Are you sure you would like to cancel this appointment?"
    )

def format_reschedule_confirmation(doctor_name: str, new_date: str, new_time: str) -> str:
    doc = _clean_doc_name(doctor_name)
    return (
        f"I can reschedule your appointment with {doc} to {new_date} at {new_time}. "
        "Would you like me to confirm this change?"
    )
