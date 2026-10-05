import re
from typing import Any
from app.data.medical.emergency_rules import EMERGENCY_RULES
from app.services.medical.normalization_service import clean_text

NEGATION_PATTERNS = [
    r"\bno\b",
    r"\bnot\b",
    r"\bwithout\b",
    r"\bdon't have\b",
    r"\bdo not have\b",
    r"\bdenies\b",
    r"\brule out\b",
    r"\bnever\b"
]

def is_negated(text: str, match_start: int) -> bool:
    """Check if the matched term is preceded by a negation word within a short prefix window."""
    # Look at the 35 characters immediately preceding the match
    prefix = text[max(0, match_start - 35):match_start]
    for neg in NEGATION_PATTERNS:
        if re.search(neg, prefix):
            return True
    return False


def detect_emergencies(raw_text: str) -> dict[str, Any]:
    """
    Screen input text against life-safety red flags.
    Returns matched rules, emergency flag, clinical urgency, and patient safety advisory.
    """
    cleaned = clean_text(raw_text)
    matched_rule_ids: list[str] = []
    safety_messages: list[str] = []
    highest_urgency = "routine"
    highest_priority = "normal"

    for rule in EMERGENCY_RULES:
        rule_matched = False
        for term in rule["terms"]:
            pattern = r"\b" + re.escape(term) + r"\b"
            for match in re.finditer(pattern, cleaned):
                if not is_negated(cleaned, match.start()):
                    rule_matched = True
                    break
            if rule_matched:
                break

        if rule_matched:
            matched_rule_ids.append(rule["id"])
            safety_messages.append(rule["safety_message"])
            if rule["urgency"] == "emergency":
                highest_urgency = "emergency"
                highest_priority = "critical"
            elif highest_urgency != "emergency" and rule["urgency"] == "urgent":
                highest_urgency = "urgent"
                highest_priority = "urgent"

    emergency_detected = highest_urgency == "emergency"

    return {
        "emergency_detected": emergency_detected,
        "urgency": highest_urgency,
        "priority": highest_priority,
        "matched_rules": matched_rule_ids,
        "safety_message": safety_messages[0] if safety_messages else None
    }
