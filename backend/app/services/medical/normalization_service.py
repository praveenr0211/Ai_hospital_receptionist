import re
from app.schemas.medical_routing import NormalizedSymptom
from app.data.medical.symptom_mapping import SYMPTOM_CONCEPTS, VAGUE_SYMPTOM_PHRASES

# Duration extraction regex
DURATION_PATTERN = re.compile(
    r"\b(for|since|past|last)?\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten|a few|several)?\s*(hours?|days?|weeks?|months?|years?|yesterday|morning|today)\b",
    re.IGNORECASE
)

# Severity cues regex
SEVERITY_PATTERN = re.compile(
    r"\b(severe|intense|acute|unbearable|excruciating|terrible|bad|moderate|mild|slight|minor)\b",
    re.IGNORECASE
)

def clean_text(text: str) -> str:
    """Normalize input text by lowering case and stripping excessive punctuation."""
    lowered = text.lower().strip()
    # Replace punctuation except hyphens and apostrophes with spaces
    cleaned = re.sub(r"[^a-z0-9\s'-]", " ", lowered)
    return " ".join(cleaned.split())


def extract_duration(text: str) -> str | None:
    match = DURATION_PATTERN.search(text)
    if match:
        return match.group(0).strip()
    return None


def extract_severity(text: str) -> str | None:
    match = SEVERITY_PATTERN.search(text)
    if match:
        return match.group(0).lower().strip()
    return None


def is_vague_complaint(text: str) -> bool:
    cleaned = clean_text(text)
    for phrase in VAGUE_SYMPTOM_PHRASES:
        if phrase in cleaned:
            return True
    # If the text is very short (under 4 words) and contains only generic words like "pain", "doctor", "hurts"
    words = cleaned.split()
    generic_words = {"i", "have", "am", "having", "got", "pain", "hurts", "doctor", "need", "please", "help", "sick"}
    if len(words) <= 3 and all(w in generic_words for w in words):
        return True
    return False


def normalize_symptoms(symptom_text: str) -> NormalizedSymptom:
    """
    Deterministically normalize raw patient text into standardized symptom concepts.
    Maps variations, typos, and phrasing to canonical concept IDs.
    """
    cleaned = clean_text(symptom_text)
    duration = extract_duration(symptom_text)
    severity = extract_severity(symptom_text)

    matched_concepts: list[str] = []
    body_areas: list[str] = []

    # Match against canonical concepts & synonyms
    for concept_id, concept_def in SYMPTOM_CONCEPTS.items():
        for synonym in concept_def["synonyms"]:
            pattern = r"\b" + re.escape(synonym) + r"\b"
            if re.search(pattern, cleaned):
                if concept_id not in matched_concepts:
                    matched_concepts.append(concept_id)
                    if concept_def["body_area"] not in body_areas:
                        body_areas.append(concept_def["body_area"])
                break

    primary_body_area = body_areas[0] if body_areas else None

    return NormalizedSymptom(
        original_text=symptom_text,
        normalized_terms=matched_concepts,
        body_area=primary_body_area,
        duration=duration,
        severity=severity
    )
