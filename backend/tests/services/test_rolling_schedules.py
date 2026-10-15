"""Unit and Integration tests for Rolling Schedule Service and JIT provisioning."""

from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.doctor import Doctor, DoctorStatus
from app.models.schedule import DoctorSchedule
from app.services.rolling_schedule_service import (
    ensure_rolling_schedules,
    ensure_doctor_schedule_for_date,
    ROLLING_WINDOW_DAYS,
)
from app.services.availability_service import get_available_slots

client = TestClient(app)


def test_ensure_rolling_schedules_coverage(db_session, sample_doctor):
    """Test that schedules are generated across the rolling window."""
    today = date.today()
    ensure_rolling_schedules(start_date=today, window_days=7, db=db_session)

    # Verify every day has at least 1 active schedule for sample_doctor
    for i in range(8):
        check_date = today + timedelta(days=i)
        schedules = db_session.scalars(
            select(DoctorSchedule).where(
                DoctorSchedule.doctor_id == sample_doctor.id,
                DoctorSchedule.date == check_date,
                DoctorSchedule.status == "active"
            )
        ).all()
        assert len(schedules) > 0


def test_ensure_rolling_schedules_idempotency(db_session, sample_doctor):
    """Running ensure_rolling_schedules repeatedly should not create duplicate blocks."""
    today = date.today()
    ensure_rolling_schedules(start_date=today, window_days=5, db=db_session)
    
    # Second run should find everything already exists
    second_created = ensure_rolling_schedules(start_date=today, window_days=5, db=db_session)
    assert second_created == 0


def test_jit_schedule_provisioning_on_availability_check(db_session, sample_doctor):
    """Querying availability for an in-window date without pre-existing schedules should JIT generate them."""
    target_date = date.today() + timedelta(days=9)
    
    # Delete any existing schedules for this specific day to ensure clean slate
    db_session.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == sample_doctor.id,
        DoctorSchedule.date == target_date
    ).delete()
    db_session.commit()

    # Call availability service - JIT will provision schedules on the fly
    result = get_available_slots(sample_doctor.id, target_date, db=db_session)
    
    assert result["doctor_id"] == sample_doctor.id
    assert result["date"] == target_date.isoformat()
    assert result["available_count"] > 0
    assert len(result["slots"]) > 0


def test_maintain_window_api_endpoint(sample_doctor):
    """Test POST /api/v1/schedules/maintain-window endpoint."""
    response = client.post("/api/v1/schedules/maintain-window?days=7")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["window_days"] == 7
    assert "new_schedule_blocks_created" in data
