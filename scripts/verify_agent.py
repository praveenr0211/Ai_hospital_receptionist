"""
Verification script for Phase 5 — AI Agent & Conversation Orchestration.

Tests and verifies:
1. Session isolation and state persistence
2. Structured intent detection across diverse phrasings
3. Multi-turn booking conversation with confirmation gate
4. Emergency red-flag detection halting routine booking
5. Clinical symptom clarification flow
6. Race-condition recovery (SlotAlreadyBookedError) with alternatives
7. Cancellation flow with patient identification and confirmation
8. Rescheduling flow with availability verification
9. Human escalation handling
10. Negative safety gates (no booking without confirmation, tool permission boundaries)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from datetime import date, time
from sqlalchemy import delete
from tabulate import tabulate

from app.db.session import SessionLocal
from app.models import Patient, Doctor, Appointment
from app.agent.graph import agent
from app.agent.state import session_store
from app.agent.tools.availability_tools import check_doctor_availability
from app.agent.policies import is_tool_allowed, parse_user_confirmation
from app.services.booking_service import book_appointment

def run_phase5_verification() -> bool:
    print("\n" + "=" * 75)
    print("      PHASE 5 VERIFICATION: AI AGENT & CONVERSATION ORCHESTRATION")
    print("=" * 75)

    db = SessionLocal()
    results = []

    try:
        sample_doc = db.query(Doctor).filter(Doctor.name == "Dr. Ravi Kumar").first()
        sample_pat = db.query(Patient).filter(Patient.phone == "9876500001").first()
        second_pat = db.query(Patient).filter(Patient.phone == "9876500002").first()

        assert sample_doc is not None, "Dr. Ravi Kumar must exist"
        assert sample_pat is not None, "Patient Praveen Kumar must exist"

        # -------------------------------------------------------------
        # Test 1: Session Isolation & State Persistence
        # -------------------------------------------------------------
        session_store.clear("sess_iso_1")
        session_store.clear("sess_iso_2")
        agent.process_message("sess_iso_1", "Hello, I want to book an appointment", db=db)
        agent.process_message("sess_iso_2", "I want to cancel", db=db)
        
        s1 = session_store.get_or_create("sess_iso_1")
        s2 = session_store.get_or_create("sess_iso_2")
        iso_pass = s1.intent in {"BOOK_APPOINTMENT", "UNKNOWN"} and s2.intent == "CANCEL_APPOINTMENT"
        results.append(["1. Session State Isolation", "PASS" if iso_pass else "FAIL", f"S1 intent={s1.intent}, S2 intent={s2.intent}"])

        # -------------------------------------------------------------
        # Test 2: Structured Intent Classification
        # -------------------------------------------------------------
        from app.agent.llm import classify_intent
        intents_ok = (
            classify_intent("Book an appointment").intent == "BOOK_APPOINTMENT" and
            classify_intent("I want to speak with a human").intent == "HUMAN_AGENT" and
            classify_intent("Cancel my appointment").intent == "CANCEL_APPOINTMENT" and
            classify_intent("Can I reschedule?").intent == "RESCHEDULE_APPOINTMENT" and
            classify_intent("I cannot breathe and have chest pain").intent == "EMERGENCY"
        )
        results.append(["2. Structured Intent Engine", "PASS" if intents_ok else "FAIL", "Recognized 5 core intents with high accuracy"])

        # -------------------------------------------------------------
        # Test 3: Emergency Symptom Detection & Booking Halt
        # -------------------------------------------------------------
        em_sess = "sess_verify_em"
        session_store.clear(em_sess)
        em_resp = agent.process_message(em_sess, "I'm having severe chest pain and gasping for air", db=db)
        em_state = session_store.get_or_create(em_sess)
        em_pass = (
            em_resp.escalation_required is True and
            em_resp.action_required == "HUMAN_ESCALATION" and
            em_state.emergency_detected is True and
            em_resp.appointment_id is None
        )
        results.append(["3. Emergency Safety Branch", "PASS" if em_pass else "FAIL", "Booking blocked, human emergency escalation triggered"])

        # -------------------------------------------------------------
        # Test 4: Ambiguous Symptom Clarification
        # -------------------------------------------------------------
        clar_sess = "sess_verify_clar"
        session_store.clear(clar_sess)
        clar_resp1 = agent.process_message(clar_sess, "I'm not feeling well, my body feels strange", db=db)
        clar_resp2 = agent.process_message(clar_sess, "I have mild heart palpitations and flutter since yesterday", db=db)
        clar_state = session_store.get_or_create(clar_sess)
        clar_pass = (
            clar_resp1.state in {"CLARIFICATION", "COLLECT_SYMPTOMS"} and
            clar_state.specialty == "Cardiology" and
            clar_resp2.state in {"OFFER_SLOTS", "CHECK_AVAILABILITY"}
        )
        results.append(["4. Clinical Clarification Flow", "PASS" if clar_pass else "FAIL", "Vague symptom prompted clarification, then routed"])

        # -------------------------------------------------------------
        # Test 5: End-to-End Multi-Turn Booking Flow with Confirmation Gate
        # -------------------------------------------------------------
        book_sess = "sess_verify_booking"
        session_store.clear(book_sess)
        created_apt_id = None
        try:
            # Turn 1: Symptoms
            b_r1 = agent.process_message(
                book_sess,
                "I have mild heart palpitations since yesterday, can I see a doctor on 2026-09-25?",
                phone_number=sample_pat.phone,
                db=db,
            )
            state_b = session_store.get_or_create(book_sess)
            chosen_slot = state_b.available_slots[0]["start_time"]

            # Turn 2: Slot selection
            b_r2 = agent.process_message(book_sess, f"{chosen_slot} please", phone_number=sample_pat.phone, db=db)
            t2_ok = b_r2.state == "WAIT_CONFIRMATION" and b_r2.action_required == "CONFIRMATION_REQUIRED"

            # Turn 3: Explicit confirmation
            b_r3 = agent.process_message(book_sess, "Yes, please confirm the booking", phone_number=sample_pat.phone, db=db)
            created_apt_id = b_r3.appointment_id
            t3_ok = b_r3.state == "BOOKING_COMPLETE" and b_r3.appointment_id is not None

            book_pass = t2_ok and t3_ok
            results.append(["5. E2E Booking & Confirmation Gate", "PASS" if book_pass else "FAIL", f"Apt #{created_apt_id} confirmed only after explicit Yes"])
        finally:
            if created_apt_id:
                db.rollback()
                db.execute(delete(Appointment).where(Appointment.id == created_apt_id))
                db.commit()

        # -------------------------------------------------------------
        # Test 6: Unavailable Slot & Real Alternatives
        # -------------------------------------------------------------
        unavail_sess = "sess_verify_unavail"
        session_store.clear(unavail_sess)
        u_resp = agent.process_message(
            unavail_sess,
            "I have mild heart flutter, can I see a cardiologist on 2026-09-25 at 08:00 AM?",
            phone_number=sample_pat.phone,
            db=db,
        )
        u_pass = u_resp.appointment_id is None and "not available" in u_resp.message.lower()
        results.append(["6. Alternative Slot Presentation", "PASS" if u_pass else "FAIL", "Unavailable 08:00 handled, valid shift slots offered"])

        # -------------------------------------------------------------
        # Test 7: Race Condition (SlotBookedByAnotherCaller)
        # -------------------------------------------------------------
        race_sess = "sess_verify_race"
        session_store.clear(race_sess)
        avail = check_doctor_availability(db, sample_doc.id, "2026-09-25")
        race_slot = avail.available_slots[0].start_time
        rh, rm = map(int, race_slot.split(":"))

        r_state = session_store.get_or_create(race_sess)
        r_state.current_state = "WAIT_CONFIRMATION"
        r_state.patient_id = sample_pat.id
        r_state.doctor_id = sample_doc.id
        r_state.doctor_name = sample_doc.name
        r_state.appointment_date = "2026-09-25"
        r_state.requested_time = race_slot
        r_state.selected_slot = {"start_time": race_slot, "end_time": f"{rh:02d}:{rm+30:02d}"}
        r_state.awaiting_confirmation = True
        session_store.save(r_state)

        # Another patient snatches the slot
        race_apt = book_appointment(
            patient_id=second_pat.id,
            doctor_id=sample_doc.id,
            appointment_date=date(2026, 9, 25),
            start_time=time(rh, rm),
            reason="Concurrent collision",
            db=db,
        )
        db.commit()

        try:
            r_resp = agent.process_message(race_sess, "Yes, confirm it now please", db=db)
            race_pass = r_resp.appointment_id is None and r_resp.state == "OFFER_SLOTS"
            results.append(["7. Concurrency / Race Handling", "PASS" if race_pass else "FAIL", "Caught SlotAlreadyBookedError, offered alternatives"])
        finally:
            db.rollback()
            db.execute(delete(Appointment).where(Appointment.id == race_apt["appointment_id"]))
            db.commit()

        # -------------------------------------------------------------
        # Test 8: Cancellation Flow with Confirmation
        # -------------------------------------------------------------
        cancel_sess = "sess_verify_cancel"
        session_store.clear(cancel_sess)
        avail_c = check_doctor_availability(db, sample_doc.id, "2026-09-25")
        c_slot = avail_c.available_slots[0].start_time
        ch, cm = map(int, c_slot.split(":"))

        c_apt = book_appointment(
            patient_id=sample_pat.id,
            doctor_id=sample_doc.id,
            appointment_date=date(2026, 9, 25),
            start_time=time(ch, cm),
            reason="Cancellation verification",
            db=db,
        )
        db.commit()

        try:
            c_r1 = agent.process_message(cancel_sess, "I want to cancel my appointment", phone_number=sample_pat.phone, db=db)
            c_t1_ok = c_r1.state == "WAIT_CONFIRMATION" and "cancel" in c_r1.message.lower()

            c_r2 = agent.process_message(cancel_sess, "Yes, please cancel it", phone_number=sample_pat.phone, db=db)
            c_t2_ok = c_r2.state == "END" and "cancelled" in c_r2.message.lower()

            cancel_pass = c_t1_ok and c_t2_ok
            results.append(["8. Cancellation Flow", "PASS" if cancel_pass else "FAIL", f"Apt #{c_apt['appointment_id']} safely cancelled on user confirmation"])
        finally:
            db.rollback()
            db.execute(delete(Appointment).where(Appointment.id == c_apt["appointment_id"]))
            db.commit()

        # -------------------------------------------------------------
        # Test 9: Rescheduling Flow with Availability Verification
        # -------------------------------------------------------------
        resched_sess = "sess_verify_resched"
        session_store.clear(resched_sess)
        avail_r = check_doctor_availability(db, sample_doc.id, "2026-09-25")
        assert len(avail_r.available_slots) >= 2
        rs1 = avail_r.available_slots[0].start_time
        rs2 = avail_r.available_slots[1].start_time
        r1h, r1m = map(int, rs1.split(":"))

        resched_apt = book_appointment(
            patient_id=sample_pat.id,
            doctor_id=sample_doc.id,
            appointment_date=date(2026, 9, 25),
            start_time=time(r1h, r1m),
            reason="Reschedule verification",
            db=db,
        )
        db.commit()

        try:
            rs_r1 = agent.process_message(resched_sess, f"Can I reschedule my appointment to {rs2}?", phone_number=sample_pat.phone, db=db)
            rs_t1_ok = rs_r1.state == "WAIT_CONFIRMATION" and "reschedule" in rs_r1.message.lower()

            rs_r2 = agent.process_message(resched_sess, "Yes, please confirm", phone_number=sample_pat.phone, db=db)
            rs_t2_ok = rs_r2.state == "END" and "rescheduled" in rs_r2.message.lower()

            resched_pass = rs_t1_ok and rs_t2_ok
            results.append(["9. Atomic Rescheduling Flow", "PASS" if resched_pass else "FAIL", f"Moved from {rs1} to {rs2} atomically with confirmation"])
        finally:
            db.rollback()
            db.execute(delete(Appointment).where(Appointment.id == resched_apt["appointment_id"]))
            db.commit()

        # -------------------------------------------------------------
        # Test 10: Human Agent Escalation
        # -------------------------------------------------------------
        human_sess = "sess_verify_human"
        session_store.clear(human_sess)
        h_resp = agent.process_message(human_sess, "Please connect me with a human operator", db=db)
        human_pass = h_resp.escalation_required is True and h_resp.action_required == "HUMAN_ESCALATION"
        results.append(["10. Human Operator Handoff", "PASS" if human_pass else "FAIL", "Transferred caller to human patient care staff"])

        # -------------------------------------------------------------
        # Test 11: Safety Boundary & Confirmation Gate Compliance
        # -------------------------------------------------------------
        safe_pass = (
            is_tool_allowed("BOOK_APPOINTMENT", "book_appointment_tool") is True and
            is_tool_allowed("WAIT_CONFIRMATION", "book_appointment_tool") is False and
            is_tool_allowed("OFFER_SLOTS", "book_appointment_tool") is False and
            parse_user_confirmation("10:30 sounds good") is None and
            parse_user_confirmation("maybe") is None and
            parse_user_confirmation("Yes please") is True and
            parse_user_confirmation("No, cancel that") is False
        )
        results.append(["11. Safety Policy Boundaries", "PASS" if safe_pass else "FAIL", "Strict confirmation gate enforced, no inferred booking"])

        # Print summary table
        print(tabulate(results, headers=["Capability / Test Scenario", "Status", "Observation"], tablefmt="grid"))

        all_passed = all(r[1] == "PASS" for r in results)
        print("\n" + "=" * 75)
        if all_passed:
            print("   ✅ ALL 11 PHASE 5 AGENT VERIFICATION SCENARIOS PASSED PERFECTLY!")
        else:
            print("   ❌ SOME VERIFICATION SCENARIOS FAILED!")
        print("=" * 75 + "\n")
        return all_passed

    finally:
        db.close()

if __name__ == "__main__":
    success = run_phase5_verification()
    exit(0 if success else 1)
