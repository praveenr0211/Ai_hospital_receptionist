"""
Controlled medical vocabulary, symptom concepts, synonyms, and specialty routing map.
Used for deterministic normalization and specialty mapping without diagnosis.
"""

from typing import TypedDict

class SymptomDefinition(TypedDict):
    id: str
    label: str
    body_area: str
    synonyms: list[str]
    specialties: list[str]
    clarification_question: str | None

SYMPTOM_CONCEPTS: dict[str, SymptomDefinition] = {
    "tooth_pain": {
        "id": "tooth_pain",
        "label": "Tooth / Dental Pain",
        "body_area": "mouth",
        "synonyms": [
            "tooth pain", "tooth ache", "toothache", "teeth hurt", "teeth hurting",
            "pain in tooth", "pain in my tooth", "pain in teeth", "pain in my teeth",
            "wisdom tooth pain", "gum pain", "bleeding gums",
            "broken tooth", "cavity pain", "dental pain", "jaw pain from tooth"
        ],
        "specialties": ["Dentistry"],
        "clarification_question": None
    },
    "chest_pain": {
        "id": "chest_pain",
        "label": "Chest Discomfort / Pain",
        "body_area": "chest",
        "synonyms": [
            "chest pain", "pain in chest", "pain in my chest", "chest discomfort", "chest pressure",
            "pressure in chest", "pressure in my chest", "tightness in chest", "tightness in my chest",
            "chest hurting", "heart pain", "pain near heart", "angina", "discomfort in chest"
        ],
        "specialties": ["Cardiology"],
        "clarification_question": None
    },
    "palpitations": {
        "id": "palpitations",
        "label": "Palpitations / Rapid Heartbeat",
        "body_area": "chest",
        "synonyms": [
            "palpitations", "racing heart", "heart beating fast", "heart flutter",
            "irregular heartbeat", "skipped beats", "heart racing"
        ],
        "specialties": ["Cardiology"],
        "clarification_question": None
    },
    "skin_rash": {
        "id": "skin_rash",
        "label": "Skin Rash / Itching",
        "body_area": "skin",
        "synonyms": [
            "skin rash", "rash on skin", "itchy skin", "itching on skin", "skin redness",
            "red patches on skin", "eczema", "psoriasis", "hives on skin", "skin allergy"
        ],
        "specialties": ["Dermatology"],
        "clarification_question": None
    },
    "acne": {
        "id": "acne",
        "label": "Acne / Pimples",
        "body_area": "skin",
        "synonyms": [
            "acne", "pimples", "breakouts", "blackheads", "cystic acne", "facial pimples"
        ],
        "specialties": ["Dermatology"],
        "clarification_question": None
    },
    "hair_loss": {
        "id": "hair_loss",
        "label": "Hair Loss / Alopecia",
        "body_area": "scalp",
        "synonyms": [
            "hair loss", "hair fall", "losing hair", "bald patches", "thinning hair"
        ],
        "specialties": ["Dermatology"],
        "clarification_question": None
    },
    "eye_pain": {
        "id": "eye_pain",
        "label": "Eye Pain / Redness",
        "body_area": "eyes",
        "synonyms": [
            "eye pain", "pain in eye", "pain in my eye", "eyes hurting", "eye hurting",
            "eye hurts", "my eye hurts", "eyes hurt", "red eye", "pink eye",
            "burning eyes", "itchy eyes", "eye irritation", "stye"
        ],
        "specialties": ["Ophthalmology"],
        "clarification_question": None
    },
    "vision_problem": {
        "id": "vision_problem",
        "label": "Blurry Vision / Sight Issues",
        "body_area": "eyes",
        "synonyms": [
            "blurry vision", "blurred vision", "can't see clearly", "double vision",
            "loss of vision", "seeing spots", "vision problems", "cloudy vision"
        ],
        "specialties": ["Ophthalmology"],
        "clarification_question": None
    },
    "ear_pain": {
        "id": "ear_pain",
        "label": "Ear Pain / Infection",
        "body_area": "ears",
        "synonyms": [
            "ear pain", "ear ache", "earache", "pain in ear", "ear hurting",
            "ear discharge", "swimmer's ear", "ear fullness"
        ],
        "specialties": ["ENT"],
        "clarification_question": None
    },
    "hearing_problem": {
        "id": "hearing_problem",
        "label": "Hearing Loss / Tinnitus",
        "body_area": "ears",
        "synonyms": [
            "hearing loss", "can't hear well", "hard of hearing", "ringing in ears",
            "tinnitus", "buzzing in ears"
        ],
        "specialties": ["ENT"],
        "clarification_question": None
    },
    "sore_throat": {
        "id": "sore_throat",
        "label": "Sore Throat / Tonsillitis",
        "body_area": "throat",
        "synonyms": [
            "sore throat", "throat pain", "pain swallowing", "throat hurts",
            "tonsil pain", "swollen tonsils", "scratchy throat"
        ],
        "specialties": ["ENT", "General Medicine"],
        "clarification_question": "Are you experiencing primarily throat discomfort (ENT), or do you also have systemic symptoms like fever and body chills (General Medicine)?"
    },
    "joint_pain": {
        "id": "joint_pain",
        "label": "Joint Pain / Arthritis",
        "body_area": "joints",
        "synonyms": [
            "joint pain", "knee pain", "pain in knee", "shoulder pain", "hip pain",
            "swollen joint", "stiff joints", "arthritis pain", "ankle pain", "wrist pain"
        ],
        "specialties": ["Orthopedics"],
        "clarification_question": None
    },
    "back_pain": {
        "id": "back_pain",
        "label": "Back / Spine Pain",
        "body_area": "back",
        "synonyms": [
            "back pain", "lower back pain", "spine pain", "pain in back", "backache",
            "lumbago", "sciatica", "neck pain", "stiff neck"
        ],
        "specialties": ["Orthopedics"],
        "clarification_question": None
    },
    "abdominal_pain": {
        "id": "abdominal_pain",
        "label": "Stomach / Abdominal Pain",
        "body_area": "abdomen",
        "synonyms": [
            "abdominal pain", "stomach pain", "stomach ache", "stomachache", "belly pain",
            "tummy pain", "cramps in stomach", "pain in stomach", "gastric pain",
            "acid reflux", "heartburn", "indigestion", "bloating", "nausea and vomiting"
        ],
        "specialties": ["Gastroenterology"],
        "clarification_question": None
    },
    "urinary_problem": {
        "id": "urinary_problem",
        "label": "Urinary Pain / Frequency",
        "body_area": "urinary",
        "synonyms": [
            "urinary problem", "burning urination", "pain when peeing", "frequent urination",
            "blood in urine", "difficulty urinating", "bladder pain", "kidney stone pain"
        ],
        "specialties": ["Urology"],
        "clarification_question": None
    },
    "menstrual_problem": {
        "id": "menstrual_problem",
        "label": "Menstrual / Gynecological Issues",
        "body_area": "pelvis",
        "synonyms": [
            "menstrual problem", "period pain", "irregular periods", "heavy bleeding period",
            "cramps menstrual", "pregnancy checkup", "pelvic pain female", "vaginal discharge"
        ],
        "specialties": ["Gynecology"],
        "clarification_question": None
    },
    "difficulty_breathing": {
        "id": "difficulty_breathing",
        "label": "Shortness of Breath / Breathing Problem",
        "body_area": "chest",
        "synonyms": [
            "difficulty breathing", "shortness of breath", "breathlessness",
            "breathing problem", "trouble breathing", "wheezing", "asthma attack"
        ],
        "specialties": ["Pulmonology", "Cardiology"],
        "clarification_question": "Is the shortness of breath associated with wheezing and chronic cough (Pulmonology), or chest tightness and heart flutter (Cardiology)?"
    },
    "cough": {
        "id": "cough",
        "label": "Persistent Cough",
        "body_area": "respiratory",
        "synonyms": [
            "cough", "dry cough", "wet cough", "coughing a lot", "persistent cough",
            "chronic cough", "cough with phlegm"
        ],
        "specialties": ["Pulmonology", "General Medicine"],
        "clarification_question": "Has the cough persisted for more than two weeks (Pulmonology), or is it an acute seasonal illness with mild fever (General Medicine)?"
    },
    "headache": {
        "id": "headache",
        "label": "Headache / Migraine",
        "body_area": "head",
        "synonyms": [
            "headache", "head ache", "migraine", "pain in head", "throbbing head pain",
            "head pounding", "tension headache"
        ],
        "specialties": ["Neurology", "General Medicine"],
        "clarification_question": "Is this a recurrent or severe neurological migraine (Neurology), or general fatigue and fever-related headache (General Medicine)?"
    },
    "dizziness": {
        "id": "dizziness",
        "label": "Dizziness / Vertigo",
        "body_area": "head",
        "synonyms": [
            "dizziness", "feeling dizzy", "lightheaded", "room spinning", "vertigo",
            "loss of balance"
        ],
        "specialties": ["Neurology", "ENT", "General Medicine"],
        "clarification_question": "Does the dizziness feel like the room is spinning when moving your head (ENT Vertigo), or is it unsteady balance and weakness (Neurology)?"
    },
    "fever": {
        "id": "fever",
        "label": "Fever / Chills",
        "body_area": "general",
        "synonyms": [
            "fever", "high temperature", "chills", "feeling feverish", "shivering and fever",
            "viral fever", "mild fever"
        ],
        "specialties": ["General Medicine"],
        "clarification_question": None
    },
    "anxiety_depression": {
        "id": "anxiety_depression",
        "label": "Anxiety / Mood Concerns",
        "body_area": "mind",
        "synonyms": [
            "anxiety", "depression", "panic attacks", "feeling depressed", "nervous breakdown",
            "sleep issues insomnia", "mental distress", "mood swings"
        ],
        "specialties": ["Psychiatry"],
        "clarification_question": None
    }
}

# Ambiguous phrases that contain no discernible organ system or specialty clue
VAGUE_SYMPTOM_PHRASES = [
    "i don't feel well",
    "i do not feel well",
    "not feeling well",
    "feeling sick",
    "i feel sick",
    "i feel bad",
    "feeling strange",
    "i feel strange",
    "i feel weird",
    "i have pain",
    "body pain",
    "hurts everywhere",
    "something is wrong with me",
    "i need a doctor",
    "general checkup"
]
