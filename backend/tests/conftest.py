import pytest
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Doctor, Patient

@pytest.fixture(scope="function")
def db_session():
    """Provide a database session for test execution."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def sample_doctor(db_session):
    """Retrieve Dr. Ravi Kumar."""
    doc = db_session.scalars(select(Doctor).where(Doctor.name == "Dr. Ravi Kumar")).first()
    assert doc is not None, "Dr. Ravi Kumar should exist in seeded database."
    return doc

@pytest.fixture(scope="function")
def sample_patient(db_session):
    """Retrieve Praveen Kumar."""
    pat = db_session.scalars(select(Patient).where(Patient.phone == "9876500001")).first()
    assert pat is not None, "Patient Praveen Kumar should exist in seeded database."
    return pat

@pytest.fixture(scope="function")
def second_patient(db_session):
    """Retrieve Rohan Sharma."""
    pat = db_session.scalars(select(Patient).where(Patient.phone == "9876500002")).first()
    assert pat is not None, "Patient Rohan Sharma should exist in seeded database."
    return pat
