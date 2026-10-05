"""
Red-flag emergency screening rules for the hospital triage layer.
Evaluates explicit danger signs requiring immediate emergency attention or human escalation.
"""

from typing import TypedDict

class EmergencyRule(TypedDict):
    id: str
    name: str
    description: str
    terms: list[str]
    urgency: str       # "emergency" or "urgent"
    priority: str      # "critical" or "urgent"
    safety_message: str

EMERGENCY_RULES: list[EmergencyRule] = [
    {
        "id": "severe_breathing_difficulty",
        "name": "Severe Respiratory Distress",
        "description": "Patient experiencing severe, acute difficulty breathing or airway obstruction",
        "terms": [
            "can't breathe",
            "cannot breathe",
            "unable to breathe",
            "severe difficulty breathing",
            "severe shortness of breath",
            "gasping for air",
            "choking",
            "turning blue",
            "struggling to breathe"
        ],
        "urgency": "emergency",
        "priority": "critical",
        "safety_message": "Immediate emergency care required. The symptoms indicate acute respiratory distress. Please call emergency services (e.g. 108/911/112) or go to the nearest emergency room immediately."
    },
    {
        "id": "acute_chest_pain_cardiac",
        "name": "Severe / Radiating Chest Pain",
        "description": "Crushing chest pain or chest pain radiating to arm, jaw, or back",
        "terms": [
            "severe chest pain",
            "crushing chest pain",
            "chest pain radiating",
            "chest pressure radiating",
            "chest pain left arm",
            "crushing pressure in chest",
            "elephant on my chest",
            "chest pain and sweating profusely"
        ],
        "urgency": "emergency",
        "priority": "critical",
        "safety_message": "Immediate emergency evaluation required. Severe or radiating chest pain can be a sign of an acute coronary event. Please visit the nearest emergency department immediately."
    },
    {
        "id": "stroke_symptoms",
        "name": "Suspected Stroke (FAST)",
        "description": "Acute neurological deficit: facial drooping, arm weakness, slurred speech",
        "terms": [
            "facial drooping",
            "face drooping",
            "arm weakness sudden",
            "slurred speech sudden",
            "sudden paralysis",
            "sudden loss of vision",
            "can't speak suddenly",
            "one side of body numb"
        ],
        "urgency": "emergency",
        "priority": "critical",
        "safety_message": "Suspected acute stroke event. Immediate emergency transport to a stroke-ready hospital is critical. Do not wait for an outpatient appointment."
    },
    {
        "id": "loss_of_consciousness",
        "name": "Loss of Consciousness / Unresponsiveness",
        "description": "Patient collapsed, unresponsive, or lost consciousness",
        "terms": [
            "loss of consciousness",
            "passed out",
            "unresponsive",
            "unconscious",
            "fainted and not waking",
            "seizure lasting more than 5 minutes"
        ],
        "urgency": "emergency",
        "priority": "critical",
        "safety_message": "Loss of consciousness requires immediate emergency evaluation. Please seek immediate urgent medical care."
    },
    {
        "id": "uncontrolled_bleeding",
        "name": "Severe / Uncontrolled Hemorrhage",
        "description": "Continuous, heavy bleeding that cannot be stopped",
        "terms": [
            "uncontrolled bleeding",
            "bleeding heavily won't stop",
            "bleeding profusely",
            "gushing blood",
            "coughing up large amounts of blood",
            "vomiting blood"
        ],
        "urgency": "emergency",
        "priority": "critical",
        "safety_message": "Uncontrolled bleeding requires immediate emergency intervention to prevent severe hypovolemia."
    },
    {
        "id": "anaphylaxis_allergy",
        "name": "Severe Allergic Reaction / Anaphylaxis",
        "description": "Acute swelling of throat, tongue, or lips with respiratory compromise",
        "terms": [
            "throat swelling",
            "throat is swelling",
            "throat is swelling up",
            "tongue swelling",
            "tongue is swelling",
            "severe allergic reaction",
            "anaphylaxis",
            "swollen lips can't breathe",
            "throat closing up",
            "throat is closing up"
        ],
        "urgency": "emergency",
        "priority": "critical",
        "safety_message": "Suspected acute anaphylaxis. Use an epinephrine auto-injector if prescribed and seek immediate emergency care."
    }
]
