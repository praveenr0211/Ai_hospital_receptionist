import sys
import os

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from datetime import datetime, date, time, timedelta, timezone
from decimal import Decimal
from tabulate import tabulate
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.models import (
    Specialty,
    Doctor,
    Patient,
    DoctorSchedule,
    Appointment,
    Call,
    Notification,
    DoctorStatus,
    AppointmentStatus,
)

def format_time(t: time) -> str:
    return t.strftime("%I:%M %p")

def generate_slots(start_t: time, end_t: time, duration_mins: int):
    slots = []
    curr = datetime.combine(date.today(), start_t)
    end = datetime.combine(date.today(), end_t)
    delta = timedelta(minutes=duration_mins)
    while curr + delta <= end:
        slots.append((curr.time(), (curr + delta).time()))
        curr += delta
    return slots

def verify_all():
    db = SessionLocal()
    print("=" * 80)
    print("      HOSPITAL AI RECEPTIONIST — PHASE 1 DATABASE VERIFICATION")
    print("=" * 80)

    try:
        # Question 1 & 2: Which doctors exist & what specialty do they belong to?
        print("\n[QUESTION 1 & 2] Which doctors exist and what specialty do they belong to?")
        stmt = select(Doctor).join(Specialty).order_by(Specialty.name, Doctor.name)
        doctors = db.scalars(stmt).all()
        doc_table = [
            [d.id, d.name, d.specialty.name, d.qualification, f"{d.experience_years} yrs", f"Rs. {d.consultation_fee}", d.status.value]
            for d in doctors
        ]
        print(tabulate(doc_table, headers=["ID", "Doctor Name", "Specialty", "Qualification", "Experience", "Fee", "Status"], tablefmt="grid"))

        # Question 3: When is each doctor working?
        print("\n[QUESTION 3] When is each doctor working? (Doctor Schedules)")
        stmt = select(DoctorSchedule).join(Doctor).order_by(DoctorSchedule.date, DoctorSchedule.start_time)
        schedules = db.scalars(stmt).all()
        sched_table = [
            [s.id, s.doctor.name, s.date.strftime("%Y-%m-%d"), f"{format_time(s.start_time)} - {format_time(s.end_time)}", f"{s.slot_duration_minutes} min", s.status]
            for s in schedules
        ]
        print(tabulate(sched_table, headers=["Sched ID", "Doctor", "Date", "Working Hours", "Slot Duration", "Status"], tablefmt="grid"))

        # Question 4: Which slots are already booked?
        print("\n[QUESTION 4] Which slots are already booked?")
        stmt = select(Appointment).join(Doctor).join(Patient).where(Appointment.status != AppointmentStatus.CANCELLED).order_by(Appointment.appointment_date, Appointment.start_time)
        booked = db.scalars(stmt).all()
        booked_table = [
            [a.id, a.doctor.name, a.patient.name, a.appointment_date.strftime("%Y-%m-%d"), f"{format_time(a.start_time)} - {format_time(a.end_time)}", a.reason, a.status.value]
            for a in booked
        ]
        print(tabulate(booked_table, headers=["Apt ID", "Doctor", "Patient", "Date", "Time Slot", "Reason", "Status"], tablefmt="grid"))

        # Question 5: Which slots are available? (Calculation Engine demonstration)
        print("\n[QUESTION 5] Which slots are available? (Dynamic Availability Engine Proof)")
        # Demonstrating for Dr. Ravi Kumar on 2026-09-25
        ravi = db.scalars(select(Doctor).where(Doctor.name == "Dr. Ravi Kumar")).first()
        if ravi:
            ravi_sched = db.scalars(select(DoctorSchedule).where(DoctorSchedule.doctor_id == ravi.id, DoctorSchedule.date == date(2026, 9, 25))).first()
            if ravi_sched:
                all_slots = generate_slots(ravi_sched.start_time, ravi_sched.end_time, ravi_sched.slot_duration_minutes)
                active_apts = db.scalars(select(Appointment).where(
                    Appointment.doctor_id == ravi.id,
                    Appointment.appointment_date == date(2026, 9, 25),
                    Appointment.status != AppointmentStatus.CANCELLED
                )).all()
                booked_starts = {a.start_time for a in active_apts}

                slot_rows = []
                for st, et in all_slots:
                    is_booked = st in booked_starts
                    status_str = "[BOOKED]" if is_booked else "[AVAILABLE]"
                    matching_pat = next((a.patient.name for a in active_apts if a.start_time == st), "-")
                    slot_rows.append([f"{format_time(st)} - {format_time(et)}", status_str, matching_pat])

                print(f"Schedule breakdown for {ravi.name} on 2026-09-25 (Working: {format_time(ravi_sched.start_time)} - {format_time(ravi_sched.end_time)}):")
                print(tabulate(slot_rows, headers=["Slot", "Status", "Patient"], tablefmt="grid"))

        # Question 6: Which patients have appointments?
        print("\n[QUESTION 6] Which patients have appointments?")
        stmt = select(Patient).order_by(Patient.name)
        patients = db.scalars(stmt).all()
        pat_rows = []
        for p in patients:
            active_apts = [a for a in p.appointments if a.status != AppointmentStatus.CANCELLED]
            apt_summary = ", ".join([f"{a.doctor.name} ({a.appointment_date} {format_time(a.start_time)})" for a in active_apts]) if active_apts else "No active appointments"
            pat_rows.append([p.id, p.name, p.phone, f"{p.age} yrs / {p.gender}", apt_summary])
        print(tabulate(pat_rows, headers=["ID", "Patient Name", "Phone", "Age / Gender", "Active Appointments"], tablefmt="grid"))

        # Question 7: What calls have been received?
        print("\n[QUESTION 7] What calls have been received?")
        stmt = select(Call).order_by(Call.started_at)
        calls = db.scalars(stmt).all()
        call_rows = [
            [c.id, c.phone_number, c.patient.name if c.patient else "Anonymous", f"{c.duration_seconds}s", c.intent, c.specialty_detected, c.outcome.value, "YES" if c.escalated else "NO"]
            for c in calls
        ]
        print(tabulate(call_rows, headers=["Call ID", "Caller Phone", "Patient", "Duration", "Intent", "Specialty Detected", "Outcome", "Escalated?"], tablefmt="grid"))

        # Question 8: What notifications were sent?
        print("\n[QUESTION 8] What notifications were sent?")
        stmt = select(Notification).order_by(Notification.created_at)
        notifs = db.scalars(stmt).all()
        notif_rows = []
        for n in notifs:
            recip = f"Patient ({n.patient.name})" if n.patient else f"Doctor ({n.doctor.name})"
            sent_str = n.sent_at.strftime("%Y-%m-%d %H:%M:%S") if n.sent_at else "Pending"
            notif_rows.append([n.id, f"Apt #{n.appointment_id}", recip, n.channel.value, n.message[:45] + "...", n.status.value, sent_str])
        print(tabulate(notif_rows, headers=["Notif ID", "Apt Ref", "Recipient", "Channel", "Message Snippet", "Status", "Sent Timestamp"], tablefmt="grid"))

        # -------------------------------------------------------------
        # DATABASE INTEGRITY & CONSTRAINT TESTS
        # -------------------------------------------------------------
        print("\n" + "=" * 80)
        print("                DATABASE INTEGRITY & CONSTRAINT SUITE")
        print("=" * 80)

        # Test 1: Double Booking Constraint
        print("\n[TEST 1] Double Booking Prevention Test:")
        print("  -> Attempting to book Dr. Ravi Kumar on 2026-09-25 at 10:00 (already booked slot)...")
        test_session = SessionLocal()
        praveen = test_session.scalars(select(Patient).where(Patient.phone == "9876500001")).first()
        dr_ravi = test_session.scalars(select(Doctor).where(Doctor.name == "Dr. Ravi Kumar")).first()
        sched_ravi = test_session.scalars(select(DoctorSchedule).where(DoctorSchedule.doctor_id == dr_ravi.id)).first()

        duplicate_apt = Appointment(
            patient_id=praveen.id,
            doctor_id=dr_ravi.id,
            schedule_id=sched_ravi.id,
            appointment_date=date(2026, 9, 25),
            start_time=time(10, 0),
            end_time=time(10, 30),
            reason="Duplicate booking attempt test",
            status=AppointmentStatus.CONFIRMED
        )
        test_session.add(duplicate_apt)
        try:
            test_session.commit()
            print("  [FAIL]: Database permitted duplicate active appointment!")
            sys.exit(1)
        except IntegrityError as e:
            test_session.rollback()
            print("  [PASS]: Database raised IntegrityError as expected! Partial unique index enforced.")
            print(f"     Constraint details: {e.orig}")

        # Test 2: Cancelled Slot Reuse
        print("\n[TEST 2] Cancelled Slot Reuse Test:")
        print("  -> Creating an appointment at 12:00, cancelling it, then booking 12:00 again...")
        slot_apt1 = Appointment(
            patient_id=praveen.id,
            doctor_id=dr_ravi.id,
            schedule_id=sched_ravi.id,
            appointment_date=date(2026, 9, 25),
            start_time=time(12, 0),
            end_time=time(12, 30),
            reason="Temporary slot to cancel",
            status=AppointmentStatus.CANCELLED  # Marked cancelled
        )
        test_session.add(slot_apt1)
        test_session.commit()

        # Now book the same slot with another patient
        rohan = test_session.scalars(select(Patient).where(Patient.phone == "9876500002")).first()
        slot_apt2 = Appointment(
            patient_id=rohan.id,
            doctor_id=dr_ravi.id,
            schedule_id=sched_ravi.id,
            appointment_date=date(2026, 9, 25),
            start_time=time(12, 0),
            end_time=time(12, 30),
            reason="Re-booking previously cancelled slot",
            status=AppointmentStatus.CONFIRMED
        )
        test_session.add(slot_apt2)
        test_session.commit()
        print("  [PASS]: Cancelled slot was freed and successfully booked by another patient!")

        # Clean up test appointments
        test_session.delete(slot_apt2)
        test_session.delete(slot_apt1)
        test_session.commit()

        # Test 3: Schedule-Doctor Consistency Composite FK
        print("\n[TEST 3] Doctor-Schedule Consistency Composite FK Test:")
        dr_priya = test_session.scalars(select(Doctor).where(Doctor.name == "Dr. Priya Sharma")).first()
        print(f"  -> Attempting to book Dr. Priya ({dr_priya.id}) with Dr. Ravi's schedule ({sched_ravi.id})...")
        mismatched_apt = Appointment(
            patient_id=praveen.id,
            doctor_id=dr_priya.id,
            schedule_id=sched_ravi.id,  # Mismatched!
            appointment_date=date(2026, 9, 25),
            start_time=time(16, 0),
            end_time=time(16, 30),
            reason="Cross-doctor schedule mismatch test",
            status=AppointmentStatus.CONFIRMED
        )
        test_session.add(mismatched_apt)
        try:
            test_session.commit()
            print("  [FAIL]: Database allowed an appointment with mismatched schedule_id and doctor_id!")
            sys.exit(1)
        except IntegrityError as e:
            test_session.rollback()
            print("  [PASS]: Database rejected mismatched schedule/doctor foreign key as expected!")

        # Test 4: Notification Single Recipient CHECK Constraint
        print("\n[TEST 4] Notification Single Recipient CHECK Constraint Test:")
        print("  -> Attempting to create notification with both patient_id AND doctor_id set...")
        first_apt = test_session.scalars(select(Appointment)).first()
        invalid_notif = Notification(
            appointment_id=first_apt.id,
            patient_id=praveen.id,
            doctor_id=dr_ravi.id,  # Both set! Violates CHECK constraint
            channel=first_apt.notifications[0].channel,
            message="Invalid multi-recipient test",
            status=first_apt.notifications[0].status
        )
        test_session.add(invalid_notif)
        try:
            test_session.commit()
            print("  [FAIL]: Database allowed notification with dual recipients!")
            sys.exit(1)
        except IntegrityError as e:
            test_session.rollback()
            print("  [PASS]: Database rejected dual recipients via CHECK constraint!")

        test_session.close()

        print("\n" + "=" * 80)
        print("  ALL 8 BLUEPRINT QUESTIONS ANSWERED AND ALL INTEGRITY TESTS PASSED!")
        print("=" * 80)

    except Exception as e:
        print(f"Verification error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    verify_all()
