import sys
from datetime import date, time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Doctor, Patient, Appointment
from app.services import (
    generate_slots,
    validate_slot_alignment,
    check_schedules_overlap,
    get_available_slots,
    check_slot_availability,
    find_alternative_slots,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
    get_appointment,
    SlotNotAvailableError,
    SlotAlreadyBookedError,
    InvalidSlotError,
)

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_verification():
    db = SessionLocal()
    print("=" * 60)
    print("PHASE 2 — AVAILABILITY & BOOKING ENGINE VERIFICATION")
    print("=" * 60)

    try:
        # Load sample entities
        dr_ravi = db.scalars(select(Doctor).where(Doctor.name == "Dr. Ravi Kumar")).first()
        praveen = db.scalars(select(Patient).where(Patient.phone == "9876500001")).first()
        rohan = db.scalars(select(Patient).where(Patient.phone == "9876500002")).first()
        target_date = date(2026, 9, 25)

        # -------------------------------------------------------------
        # [1] Slot Generation & Schedule Overlap
        # -------------------------------------------------------------
        print("\n[1] Slot Generation & Schedule Overlap Prevention")
        slots_30m = generate_slots(time(9, 0), time(13, 0), 30)
        assert len(slots_30m) == 8, f"Expected 8 slots, got {len(slots_30m)}"
        slots_20m = generate_slots(time(10, 0), time(14, 0), 20)
        assert len(slots_20m) == 12, f"Expected 12 slots, got {len(slots_20m)}"
        slots_trunc = generate_slots(time(9, 0), time(13, 10), 30)
        assert len(slots_trunc) == 8, f"Expected 8 slots with truncation, got {len(slots_trunc)}"

        # Verify schedule overlap prevention
        assert check_schedules_overlap([(time(9, 0), time(12, 0)), (time(11, 0), time(14, 0))]) is True
        assert check_schedules_overlap([(time(9, 0), time(12, 0)), (time(14, 0), time(17, 0))]) is False
        print("    [PASS] 30m, 20m, remainder-truncated slots and schedule overlap detection verified")

        # -------------------------------------------------------------
        # [2] Availability Calculation
        # -------------------------------------------------------------
        print("\n[2] Availability Calculation")
        avail = get_available_slots(dr_ravi.id, target_date, db=db)
        assert avail["total_slots"] == 8
        assert avail["available_count"] == 6
        booked_starts = {s["start"] for s in avail["slots"] if not s["available"]}
        assert "10:00" in booked_starts and "11:30" in booked_starts
        print("    [PASS] Booked slots (10:00, 11:30) excluded from available slots")

        # -------------------------------------------------------------
        # [3] Specific Slot Check
        # -------------------------------------------------------------
        print("\n[3] Specific Slot Check")
        free_check = check_slot_availability(dr_ravi.id, target_date, time(9, 30), db=db)
        assert free_check["available"] is True
        print("    [PASS] Available slot (09:30) detected")

        occupied_check = check_slot_availability(dr_ravi.id, target_date, time(10, 0), db=db)
        assert occupied_check["available"] is False
        print("    [PASS] Occupied slot (10:00) rejected")

        try:
            check_slot_availability(dr_ravi.id, target_date, time(10, 15), db=db)
            assert False, "Misaligned slot should fail"
        except InvalidSlotError:
            print("    [PASS] Misaligned boundary slot (10:15) rejected via InvalidSlotError")

        # -------------------------------------------------------------
        # [4] Booking
        # -------------------------------------------------------------
        print("\n[4] Booking")
        new_booking = book_appointment(
            patient_id=praveen.id,
            doctor_id=dr_ravi.id,
            appointment_date=target_date,
            start_time=time(9, 0),
            reason="Phase 2 E2E booking test",
            db=db
        )
        test_apt_id = new_booking["appointment_id"]
        assert new_booking["success"] is True
        assert new_booking["start_time"] == "09:00"
        print(f"    [PASS] Appointment #{test_apt_id} successfully booked at 09:00")

        # -------------------------------------------------------------
        # [5] Booking Protection (Double Booking)
        # -------------------------------------------------------------
        print("\n[5] Booking Protection")
        try:
            book_appointment(
                patient_id=rohan.id,
                doctor_id=dr_ravi.id,
                appointment_date=target_date,
                start_time=time(9, 0),
                reason="Duplicate booking attempt",
                db=db
            )
            assert False, "Double booking must be rejected"
        except SlotNotAvailableError:
            print("    [PASS] Double booking of same slot (09:00) rejected")

        # -------------------------------------------------------------
        # [6] Cancellation & Slot Release
        # -------------------------------------------------------------
        print("\n[6] Cancellation")
        cancel_res = cancel_appointment(test_apt_id, cancellation_reason="E2E test cancel", db=db)
        assert cancel_res["status"] == "cancelled"
        assert cancel_res["cancellation_reason"] == "E2E test cancel"

        apt_in_db = db.scalars(select(Appointment).where(Appointment.id == test_apt_id)).first()
        assert apt_in_db is not None
        assert apt_in_db.cancellation_reason == "E2E test cancel"

        freed_check = check_slot_availability(dr_ravi.id, target_date, time(9, 0), db=db)
        assert freed_check["available"] is True
        print("    [PASS] Appointment cancelled, cancellation_reason persisted, and slot (09:00) released")

        # Clean up test appointment
        apt_record = db.scalars(select(Appointment).where(Appointment.id == test_apt_id)).first()
        if apt_record:
            db.delete(apt_record)
            db.commit()

        # -------------------------------------------------------------
        # [7] Rescheduling (Success & Failure Safety)
        # -------------------------------------------------------------
        print("\n[7] Rescheduling")
        resched_apt = book_appointment(
            patient_id=praveen.id,
            doctor_id=dr_ravi.id,
            appointment_date=target_date,
            start_time=time(9, 30),
            reason="Reschedule test appointment",
            db=db
        )
        resched_id = resched_apt["appointment_id"]

        try:
            # 1. Failed reschedule to occupied slot (11:30)
            try:
                reschedule_appointment(resched_id, target_date, time(11, 30), db=db)
                assert False, "Reschedule to occupied slot must fail"
            except SlotNotAvailableError:
                print("    [PASS] Failed reschedule rejected and preserved original booking")

            # Verify original 09:30 is still booked
            orig_check = get_appointment(resched_id, db=db)
            assert orig_check["start_time"] == "09:30"

            # 2. Successful reschedule to free slot (10:30)
            resched_success = reschedule_appointment(resched_id, target_date, time(10, 30), db=db)
            assert resched_success["success"] is True
            assert resched_success["new_start_time"] == "10:30"
            print("    [PASS] Appointment successfully rescheduled to 10:30, slot 09:30 released")

        finally:
            apt_rec = db.scalars(select(Appointment).where(Appointment.id == resched_id)).first()
            if apt_rec:
                db.delete(apt_rec)
                db.commit()

        # -------------------------------------------------------------
        # [8] Alternative Slots
        # -------------------------------------------------------------
        print("\n[8] Alternative Slots")
        alts = find_alternative_slots(dr_ravi.id, target_date, time(10, 0), limit=3, db=db)
        assert alts["available"] is False
        assert len(alts["alternatives"]) == 3
        print(f"    [PASS] Nearest available slots returned for requested 10:00: {alts['alternatives']}")

        # -------------------------------------------------------------
        # [9] Multi-Threaded Concurrency Test
        # -------------------------------------------------------------
        print("\n[9] Concurrency Collision Test")
        collision_time = time(12, 30)
        c_results = []
        c_errors = []

        def worker(pat_id: int):
            t_db = SessionLocal()
            try:
                with t_db.begin():
                    res = book_appointment(
                        patient_id=pat_id,
                        doctor_id=dr_ravi.id,
                        appointment_date=target_date,
                        start_time=collision_time,
                        reason="Thread collision test",
                        db=t_db
                    )
                c_results.append(res)
            except (SlotAlreadyBookedError, SlotNotAvailableError) as e:
                c_errors.append(e)
            finally:
                t_db.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            fut1 = executor.submit(worker, praveen.id)
            fut2 = executor.submit(worker, rohan.id)
            fut1.result()
            fut2.result()

        assert len(c_results) == 1, f"Expected 1 success, got {len(c_results)}"
        assert len(c_errors) == 1, f"Expected 1 collision error, got {len(c_errors)}"
        print(f"    [PASS] Concurrency: 1 succeeded (#{c_results[0]['appointment_id']}), 1 rejected with {type(c_errors[0]).__name__}")

        # Clean up concurrency appointment
        for r in c_results:
            apt_c = db.scalars(select(Appointment).where(Appointment.id == r["appointment_id"])).first()
            if apt_c:
                db.delete(apt_c)
        db.commit()

        print("\n" + "=" * 60)
        print("ALL 9 PHASE 2 SCENARIOS VERIFIED AND PASSED!")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    run_verification()
