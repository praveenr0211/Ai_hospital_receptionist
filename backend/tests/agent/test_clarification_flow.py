import pytest
from app.agent.graph import agent
from app.agent.state import session_store

def test_ambiguous_symptoms_require_clarification(db_session, sample_patient):
    session_id = "test_clarification_sess_1"
    session_store.clear(session_id)

    # Turn 1: Patient provides vague symptoms
    resp1 = agent.process_message(
        session_id=session_id,
        message="I'm not feeling well, my body feels strange",
        phone_number=sample_patient.phone,
        db=db_session,
    )

    assert resp1.state in {"CLARIFICATION", "COLLECT_SYMPTOMS"}
    assert resp1.action_required == "USER_INPUT"

    # Turn 2: Patient clarifies symptoms specifically with Cardiology complaint
    resp2 = agent.process_message(
        session_id=session_id,
        message="I have mild heart palpitations and flutter since yesterday",
        phone_number=sample_patient.phone,
        db=db_session,
    )

    state = session_store.get_or_create(session_id)
    assert state.specialty == "Cardiology"
    assert resp2.state in {"OFFER_SLOTS", "CHECK_AVAILABILITY"}
