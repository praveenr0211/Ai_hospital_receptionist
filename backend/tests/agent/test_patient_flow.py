import pytest
from app.agent.tools.patient_tools import find_patient_by_phone, create_patient, get_patient_appointments

def test_find_existing_patient_by_phone(db_session, sample_patient):
    res = find_patient_by_phone(db_session, sample_patient.phone)
    assert res.success is True
    assert res.exists is True
    assert res.patient_id == sample_patient.id
    assert res.patient_name == sample_patient.name

def test_find_non_existing_patient(db_session):
    res = find_patient_by_phone(db_session, "9999999999")
    assert res.success is True
    assert res.exists is False
    assert res.patient_id is None

def test_create_new_patient(db_session):
    test_phone = "9112233445"
    res = create_patient(db_session, name="David Miller", phone_number=test_phone)
    assert res.success is True
    assert res.patient_id is not None
    assert res.patient_name == "David Miller"

    # Subsequent lookup should find them
    lookup = find_patient_by_phone(db_session, test_phone)
    assert lookup.exists is True
    assert lookup.patient_id == res.patient_id
