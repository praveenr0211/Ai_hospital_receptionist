import pytest
from datetime import date, time
from app.services.availability_service import (
    get_available_slots,
    check_slot_availability,
    find_alternative_slots,
)
from app.services.exceptions import (
    DoctorNotFoundError,
    ScheduleNotFoundError,
    InvalidSlotError,
)

def test_get_available_slots_excludes_booked(sample_doctor, db_session):
    """Available slots query accurately identifies booked vs free slots."""
    target_date = date(2026, 9, 25)
    res = get_available_slots(sample_doctor.id, target_date, db=db_session)

    assert res["doctor_id"] == sample_doctor.id
    assert res["date"] == "2026-09-25"
    assert res["total_slots"] == 8
    assert res["available_count"] == 6

    # 10:00 and 11:30 are booked
    slot_map = {s["start"]: s["available"] for s in res["slots"]}
    assert slot_map["09:00"] is True
    assert slot_map["09:30"] is True
    assert slot_map["10:00"] is False  # Booked
    assert slot_map["10:30"] is True
    assert slot_map["11:00"] is True
    assert slot_map["11:30"] is False  # Booked
    assert slot_map["12:00"] is True
    assert slot_map["12:30"] is True

def test_get_available_slots_with_time_range(sample_doctor, db_session):
    """Time range filters restrict returned slot intervals."""
    target_date = date(2026, 9, 25)
    res = get_available_slots(
        sample_doctor.id,
        target_date,
        start_time_range=time(10, 0),
        end_time_range=time(12, 0),
        db=db_session
    )
    assert len(res["slots"]) == 4
    starts = [s["start"] for s in res["slots"]]
    assert starts == ["10:00", "10:30", "11:00", "11:30"]

def test_check_slot_availability(sample_doctor, db_session):
    """Specific slot checking verifies free, booked, and misaligned slots."""
    target_date = date(2026, 9, 25)

    # Available slot
    res_free = check_slot_availability(sample_doctor.id, target_date, time(9, 30), db=db_session)
    assert res_free["available"] is True
    assert res_free["end_time"] == "10:00"

    # Booked slot
    res_booked = check_slot_availability(sample_doctor.id, target_date, time(10, 0), db=db_session)
    assert res_booked["available"] is False
    assert "already booked" in res_booked["reason"]

    # Misaligned slot (not on 30m boundary)
    with pytest.raises(InvalidSlotError, match="does not align"):
        check_slot_availability(sample_doctor.id, target_date, time(10, 15), db=db_session)

    # Outside schedule hours
    with pytest.raises(InvalidSlotError, match="does not align"):
        check_slot_availability(sample_doctor.id, target_date, time(15, 0), db=db_session)

def test_find_alternative_slots(sample_doctor, db_session):
    """Alternative search returns closest available slots sorted by distance."""
    target_date = date(2026, 9, 25)
    # 10:00 is booked, closest free slots are 09:30 and 10:30
    res = find_alternative_slots(sample_doctor.id, target_date, time(10, 0), limit=3, db=db_session)

    assert res["requested_slot"] == "10:00"
    assert res["available"] is False
    assert len(res["alternatives"]) == 3
    # 09:30 and 10:30 are both 30 mins away from 10:00
    assert "09:30" in res["alternatives"]
    assert "10:30" in res["alternatives"]

def test_availability_errors(sample_doctor, db_session):
    """DoctorNotFoundError and ScheduleNotFoundError are raised appropriately."""
    with pytest.raises(DoctorNotFoundError):
        get_available_slots(99999, date(2026, 9, 25), db=db_session)

    # Date with no schedules
    with pytest.raises(ScheduleNotFoundError):
        get_available_slots(sample_doctor.id, date(2030, 1, 1), db=db_session)
