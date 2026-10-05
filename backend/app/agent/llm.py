import re
from datetime import date, timedelta
from typing import Any
from app.schemas.agent import IntentResult, IntentType, IntentConfidence

# Pre-compiled regex patterns for intent classification
HUMAN_PATTERNS = [
    r"\b(?:speak|talk)\s+(?:to|with)\s+(?:a\s+)?(?:human|person|agent|receptionist|operator|staff)\b",
    r"\b(?:human|person|agent|operator)\s+please\b",
    r"\btransfer\s+me\b",
    r"\bconnect\s+me\s+to\s+(?:a\s+)?(?:human|person|staff|receptionist)\b",
    r"\bhuman\s+(?:receptionist|agent|operator|staff)\b",
    r"\b(?:speak|talk)\s+to\s+someone\b",
]

CANCEL_PATTERNS = [
    r"\bcancel\b",
    r"\bdrop\s+(?:my\s+)?appointment\b",
    r"\bdelete\s+(?:my\s+)?booking\b",
]

RESCHEDULE_PATTERNS = [
    r"\breschedule\b",
    r"\bchange\s+(?:my\s+)?(?:appointment|date|time|slot)\b",
    r"\bmove\s+(?:my\s+)?appointment\b",
    r"\bpostpone\b",
    r"\bshift\s+(?:my\s+)?appointment\b",
]

AVAILABILITY_PATTERNS = [
    r"\b(?:check|see|what)\s+(?:are\s+the\s+)?available\s+slots\b",
    r"\bwhen\s+is\s+dr\.?\s+\w+\s+(?:available|free)\b",
    r"\bis\s+there\s+any\s+slot\b",
    r"\bwhat\s+times?\s+are\s+available\b",
]

DOCTOR_INFO_PATTERNS = [
    r"\bwho\s+is\s+the\s+(?:cardiologist|dentist|neurologist|doctor)\b",
    r"\bdoctor\s+(?:info|details|qualification|profile|fee)\b",
    r"\btell\s+me\s+about\s+dr\b",
]

GENERAL_QUERY_PATTERNS = [
    r"\bwhere\s+is\s+the\s+hospital\b",
    r"\bhospital\s+(?:location|address|timing|visiting\s+hours)\b",
    r"\bparking\s+available\b",
]

EMERGENCY_INDICATORS = [
    r"\b(?:can't|cannot)\s+breathe\b",
    r"\bsevere\s+difficulty\s+breathing\b",
    r"\bgasping\b",
    r"\bcrushing\s+chest\s+pain\b",
    r"\bheart\s+attack\b",
    r"\bunconscious\b",
    r"\bstroke\b",
    r"\bcoughing\s+up\s+blood\b",
    r"\banaphylaxis\b",
]

BOOKING_PATTERNS = [
    r"\b(?:book|schedule|make|want|need)\s+(?:an?\s+)?appointment\b",
    r"\bsee\s+a\s+doctor\b",
    r"\bconsult\s+a\s+doctor\b",
    r"\bwant\s+to\s+see\b",
    r"\bdoctor\s+consultation\b",
    r"\bvisit\s+(?:the\s+)?hospital\b",
]

def classify_intent(message: str, current_state: str = "GREETING") -> IntentResult:
    """
    Classify user message into a structured intent with confidence and extracted entities.
    Designed for clinical robustness and deterministic safety.
    """
    text = message.strip().lower()
    entities: dict[str, Any] = {}

    # Check for emergency symptoms first
    for pat in EMERGENCY_INDICATORS:
        if re.search(pat, text):
            return IntentResult(
                intent="EMERGENCY",
                confidence="high",
                extracted_entities={"emergency_cue": pat},
            )

    # Human agent request
    for pat in HUMAN_PATTERNS:
        if re.search(pat, text):
            return IntentResult(intent="HUMAN_AGENT", confidence="high")

    # Reschedule intent
    for pat in RESCHEDULE_PATTERNS:
        if re.search(pat, text):
            return IntentResult(intent="RESCHEDULE_APPOINTMENT", confidence="high")

    # Cancel intent
    for pat in CANCEL_PATTERNS:
        if re.search(pat, text):
            return IntentResult(intent="CANCEL_APPOINTMENT", confidence="high")

    # Doctor availability intent
    for pat in AVAILABILITY_PATTERNS:
        if re.search(pat, text):
            return IntentResult(intent="CHECK_AVAILABILITY", confidence="high")

    # Doctor information intent
    for pat in DOCTOR_INFO_PATTERNS:
        if re.search(pat, text):
            return IntentResult(intent="DOCTOR_INFORMATION", confidence="high")

    # General hospital queries
    for pat in GENERAL_QUERY_PATTERNS:
        if re.search(pat, text):
            return IntentResult(intent="GENERAL_HOSPITAL_QUERY", confidence="medium")

    # Booking intent
    for pat in BOOKING_PATTERNS:
        if re.search(pat, text):
            return IntentResult(intent="BOOK_APPOINTMENT", confidence="high")

    # If the user directly describes symptoms during GREETING, UNDERSTAND_INTENT or COLLECT_SYMPTOMS,
    # treat as BOOK_APPOINTMENT with medium-to-high confidence
    symptom_cues = [
        "pain", "ache", "fever", "cough", "swelling", "bleeding", "rash", "hurt",
        "teeth", "tooth", "headache", "dizzy", "vision", "ear", "vomit", "nausea",
        "sick", "unwell", "ill", "not feeling well", "flutter", "heart", "chest",
        "throat", "stomach", "body", "trouble", "problem", "strange"
    ]
    if any(cue in text for cue in symptom_cues):
        return IntentResult(
            intent="BOOK_APPOINTMENT",
            confidence="high",
            extracted_entities={"symptom_cue": True},
        )

    # In states expecting slot or confirmation, treat as state-continuation
    if current_state in {"OFFER_SLOTS", "WAIT_CONFIRMATION", "CHECK_AVAILABILITY"}:
        return IntentResult(intent="BOOK_APPOINTMENT", confidence="medium")

    return IntentResult(intent="UNKNOWN", confidence="low")

def extract_phone_number(text: str) -> str | None:
    """Extract standard 10-15 digit phone number (e.g. +919876543210 or 9876543210)."""
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    if match:
        cleaned = re.sub(r"[^\d+]", "", match.group(0))
        if len(cleaned) >= 10:
            return cleaned
    return None

def extract_time_str(text: str) -> str | None:
    """Extract requested time such as '10:30', '10:30 AM', '11:00', '2:30 PM', '10 AM'."""
    # Pattern for 10:30 or 10:30 AM
    match = re.search(r"\b(\d{1,2}):(\d{2})(?:\s*(am|pm))?\b", text, re.IGNORECASE)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3)
        if period:
            period = period.lower()
            if period == "pm" and hour < 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
        return f"{hour:02d}:{minute:02d}"

    # Pattern for 10 AM or 2 PM
    match2 = re.search(r"\b(\d{1,2})\s*(am|pm)\b", text, re.IGNORECASE)
    if match2:
        hour = int(match2.group(1))
        period = match2.group(2).lower()
        if period == "pm" and hour < 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:00"

    return None

def extract_date_str(text: str, reference_date: date | None = None) -> str | None:
    """Extract date string YYYY-MM-DD or relative terms like 'today' or 'tomorrow'."""
    ref = reference_date or date.today()
    lower = text.lower()

    if "today" in lower:
        return ref.isoformat()
    if "tomorrow" in lower:
        return (ref + timedelta(days=1)).isoformat()

    # Match YYYY-MM-DD
    iso_match = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if iso_match:
        return iso_match.group(0)

    return None
