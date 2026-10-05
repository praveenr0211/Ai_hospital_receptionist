from app.schemas.medical_routing import SafetyDecision, UrgencyLevel, RoutingConfidence

def evaluate_safety(
    emergency_detected: bool,
    urgency_str: str,
    confidence: RoutingConfidence,
    clarification_required: bool,
    matched_emergency_rules: list[str]
) -> SafetyDecision:
    """
    Synthesize emergency indicators, routing confidence, and input clarity
    into an auditable safety decision determining booking eligibility.
    """
    urgency = UrgencyLevel(urgency_str)

    # 1. Emergency condition: Immediate stop on automated booking
    if emergency_detected or urgency == UrgencyLevel.EMERGENCY:
        rules_text = ", ".join(matched_emergency_rules) if matched_emergency_rules else "red-flag emergency rules"
        return SafetyDecision(
            booking_allowed=False,
            escalation_required=True,
            urgency=UrgencyLevel.EMERGENCY,
            reason=f"Emergency red-flag indicators detected ({rules_text}). Normal outpatient booking is clinically unsafe."
        )

    # 2. Urgent non-emergency condition
    if urgency == UrgencyLevel.URGENT:
        return SafetyDecision(
            booking_allowed=False,
            escalation_required=True,
            urgency=UrgencyLevel.URGENT,
            reason="Urgent symptoms require prompt clinical staff review before scheduling."
        )

    # 3. Ambiguous / Insufficient information
    if clarification_required or confidence == RoutingConfidence.LOW:
        return SafetyDecision(
            booking_allowed=False,
            escalation_required=False,
            urgency=UrgencyLevel.ROUTINE,
            reason="Additional symptom information is required before a specialty can be assigned."
        )

    # 4. Multi-specialty uncertainty (medium confidence)
    if confidence == RoutingConfidence.MEDIUM:
        return SafetyDecision(
            booking_allowed=False,
            escalation_required=False,
            urgency=UrgencyLevel.ROUTINE,
            reason="Symptoms map to multiple plausible clinical departments; patient clarification required."
        )

    # 5. Routine high-confidence scenario
    return SafetyDecision(
        booking_allowed=True,
        escalation_required=False,
        urgency=UrgencyLevel.ROUTINE,
        reason="No emergency indicators detected. Clinical specialty resolved with high confidence."
    )
