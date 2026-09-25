from typing import Any
from app.data.medical.symptom_mapping import SYMPTOM_CONCEPTS
from app.data.medical.specialties import HOSPITAL_SPECIALTIES

def map_symptoms_to_specialties(normalized_terms: list[str], is_vague: bool = False) -> dict[str, Any]:
    """
    Map extracted symptom concepts to candidate medical departments and evaluate routing confidence.
    Produces auditable rule traces and targeted clarification questions.
    """
    if is_vague or not normalized_terms:
        return {
            "possible_specialties": [],
            "selected_specialty": None,
            "confidence": "low",
            "clarification_required": True,
            "clarification_question": "Could you tell me what specific symptoms you are experiencing and where they are located?",
            "matched_rules": ["vague_or_unrecognized_symptoms"]
        }

    specialty_votes: dict[str, int] = {}
    matched_rules: list[str] = []
    clarification_questions: list[str] = []

    for term in normalized_terms:
        definition = SYMPTOM_CONCEPTS.get(term)
        if not definition:
            continue

        specs = definition["specialties"]
        rule_desc = f"{term} -> {', '.join(specs)}"
        matched_rules.append(rule_desc)

        if definition["clarification_question"]:
            clarification_questions.append(definition["clarification_question"])

        for spec in specs:
            specialty_votes[spec] = specialty_votes.get(spec, 0) + 1

    if not specialty_votes:
        return {
            "possible_specialties": [],
            "selected_specialty": None,
            "confidence": "low",
            "clarification_required": True,
            "clarification_question": "Could you describe your symptoms in more detail so I can direct you to the right department?",
            "matched_rules": matched_rules or ["no_specialty_mapped"]
        }

    # Sort specialties by frequency of matching terms
    sorted_specialties = sorted(specialty_votes.keys(), key=lambda s: specialty_votes[s], reverse=True)

    # Single unambiguous match
    if len(sorted_specialties) == 1:
        return {
            "possible_specialties": sorted_specialties,
            "selected_specialty": sorted_specialties[0],
            "confidence": "high",
            "clarification_required": False,
            "clarification_question": None,
            "matched_rules": matched_rules
        }

    # Check if top specialty has a clear majority
    top_spec = sorted_specialties[0]
    second_spec = sorted_specialties[1]

    if specialty_votes[top_spec] > specialty_votes[second_spec]:
        # Clear majority among multiple symptoms
        return {
            "possible_specialties": sorted_specialties,
            "selected_specialty": top_spec,
            "confidence": "high",
            "clarification_required": False,
            "clarification_question": None,
            "matched_rules": matched_rules
        }
    else:
        # Tied or multi-specialty concept (e.g. headache -> Neurology / General Medicine)
        clarification_q = clarification_questions[0] if clarification_questions else (
            f"Your symptoms could be seen by {sorted_specialties[0]} or {sorted_specialties[1]}. Could you clarify if this is a specialized or general concern?"
        )
        return {
            "possible_specialties": sorted_specialties,
            "selected_specialty": None,
            "confidence": "medium",
            "clarification_required": True,
            "clarification_question": clarification_q,
            "matched_rules": matched_rules
        }
