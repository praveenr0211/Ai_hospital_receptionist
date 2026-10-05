import pytest
from datetime import time
from app.services.schedule_service import generate_slots, validate_slot_alignment, check_schedules_overlap

def test_generate_slots_30_minutes():
    """09:00 -> 13:00 with 30-minute intervals produces exactly 8 slots."""
    slots = generate_slots(time(9, 0), time(13, 0), 30)
    assert len(slots) == 8
    assert slots[0] == (time(9, 0), time(9, 30))
    assert slots[1] == (time(9, 30), time(10, 0))
    assert slots[7] == (time(12, 30), time(13, 0))

def test_generate_slots_20_minutes():
    """09:00 -> 13:00 with 20-minute intervals produces exactly 12 slots."""
    slots = generate_slots(time(9, 0), time(13, 0), 20)
    assert len(slots) == 12
    assert slots[0] == (time(9, 0), time(9, 20))
    assert slots[11] == (time(12, 40), time(13, 0))

def test_generate_slots_with_remainder_truncation():
    """09:00 -> 13:10 with 30-minute intervals produces 8 slots, omitting 13:00-13:10."""
    slots = generate_slots(time(9, 0), time(13, 10), 30)
    assert len(slots) == 8
    assert slots[-1] == (time(12, 30), time(13, 0))

def test_generate_slots_invalid_start_end():
    """start_time >= end_time raises ValueError."""
    with pytest.raises(ValueError, match="strictly earlier"):
        generate_slots(time(13, 0), time(9, 0), 30)
    with pytest.raises(ValueError, match="strictly earlier"):
        generate_slots(time(10, 0), time(10, 0), 30)

def test_generate_slots_invalid_duration():
    """slot_duration_minutes <= 0 raises ValueError."""
    with pytest.raises(ValueError, match="greater than zero"):
        generate_slots(time(9, 0), time(13, 0), 0)
    with pytest.raises(ValueError, match="greater than zero"):
        generate_slots(time(9, 0), time(13, 0), -15)

def test_validate_slot_alignment():
    """validate_slot_alignment correctly identifies valid vs misaligned start times."""
    is_valid, et = validate_slot_alignment(time(10, 0), time(9, 0), time(13, 0), 30)
    assert is_valid is True
    assert et == time(10, 30)

    is_valid, et = validate_slot_alignment(time(10, 15), time(9, 0), time(13, 0), 30)
    assert is_valid is False
    assert et is None

    is_valid, et = validate_slot_alignment(time(13, 0), time(9, 0), time(13, 0), 30)
    assert is_valid is False
    assert et is None

def test_check_schedules_overlap():
    """check_schedules_overlap correctly detects overlapping and non-overlapping shifts."""
    # Non-overlapping
    assert check_schedules_overlap([
        (time(9, 0), time(12, 0)),
        (time(14, 0), time(17, 0))
    ]) is False

    # Back-to-back (touching at boundary is allowed)
    assert check_schedules_overlap([
        (time(9, 0), time(12, 0)),
        (time(12, 0), time(15, 0))
    ]) is False

    # Overlapping (09:00-12:00 and 11:00-14:00)
    assert check_schedules_overlap([
        (time(9, 0), time(12, 0)),
        (time(11, 0), time(14, 0))
    ]) is True

    # Empty or single interval
    assert check_schedules_overlap([]) is False
    assert check_schedules_overlap([(time(9, 0), time(12, 0))]) is False
