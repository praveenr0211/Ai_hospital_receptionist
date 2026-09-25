from datetime import date, time, datetime, timedelta

def generate_slots(
    start_time: time,
    end_time: time,
    slot_duration_minutes: int
) -> list[tuple[time, time]]:
    """
    Generate appointment slots from a start time, end time, and duration.
    
    Boundary rules:
    - start_time < end_time must be strictly true.
    - slot_duration_minutes must be > 0.
    - Each slot finishes within the schedule: curr + duration <= end.
    - Any remainder that cannot fit a full slot is omitted.
    """
    if start_time >= end_time:
        raise ValueError(f"start_time ({start_time}) must be strictly earlier than end_time ({end_time}).")
    if slot_duration_minutes <= 0:
        raise ValueError(f"slot_duration_minutes ({slot_duration_minutes}) must be greater than zero.")

    slots: list[tuple[time, time]] = []
    dummy_date = date(2000, 1, 1)
    curr = datetime.combine(dummy_date, start_time)
    end = datetime.combine(dummy_date, end_time)
    delta = timedelta(minutes=slot_duration_minutes)

    while curr + delta <= end:
        slots.append((curr.time(), (curr + delta).time()))
        curr += delta

    return slots


def validate_slot_alignment(
    requested_start: time,
    schedule_start: time,
    schedule_end: time,
    slot_duration_minutes: int
) -> tuple[bool, time | None]:
    """
    Check if a requested start time falls exactly on a valid slot boundary
    within the schedule block and return (is_valid, calculated_end_time).
    """
    slots = generate_slots(schedule_start, schedule_end, slot_duration_minutes)
    for st, et in slots:
        if st == requested_start:
            return True, et
    return False, None


def check_schedules_overlap(schedule_intervals: list[tuple[time, time]]) -> bool:
    """
    Check if any schedule intervals in the list overlap with one another.
    Each element is (start_time, end_time).
    """
    if len(schedule_intervals) <= 1:
        return False

    sorted_intervals = sorted(schedule_intervals, key=lambda s: s[0])
    for i in range(len(sorted_intervals) - 1):
        if sorted_intervals[i][1] > sorted_intervals[i + 1][0]:
            return True
    return False
