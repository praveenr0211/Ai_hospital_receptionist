from datetime import date, time, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
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
    NotificationChannel,
    NotificationStatus,
    CallOutcome,
)

def seed_database():
    db = SessionLocal()
    try:
        print("--- Starting Idempotent Database Seeding ---")

        # 1. Seed 10 Specialties
        specialties_data = [
            ("Cardiology", "Heart, vascular, and cardiovascular care"),
            ("Dermatology", "Skin, hair, nail conditions and allergies"),
            ("Orthopedics", "Bone, joint, spine, and musculoskeletal system"),
            ("Neurology", "Brain, spinal cord, and nervous system disorders"),
            ("Pediatrics", "Infant, child, and adolescent healthcare"),
            ("ENT", "Ear, nose, and throat medical and surgical care"),
            ("Gastroenterology", "Digestive system, liver, and gastrointestinal tract"),
            ("General Medicine", "Primary healthcare, common illnesses, and preventive medicine"),
            ("Gynecology", "Women's reproductive health and obstetrics"),
            ("Urology", "Urinary tract system and male reproductive health"),
        ]

        specialty_map = {}
        for name, desc in specialties_data:
            stmt = select(Specialty).where(Specialty.name == name)
            existing = db.scalars(stmt).first()
            if not existing:
                spec = Specialty(name=name, description=desc, status=True)
                db.add(spec)
                db.flush()
                specialty_map[name] = spec
            else:
                specialty_map[name] = existing

        print(f"[OK] Specialties: {len(specialty_map)} verified/seeded.")

        # 2. Seed 16 Doctors
        doctors_data = [
            # Cardiology
            ("Dr. Ravi Kumar", "Cardiology", "MD, DM Cardiology", 12, "9876543210", "ravi.kumar@hospital.com", Decimal("800.00"), DoctorStatus.ACTIVE),
            ("Dr. Priya Sharma", "Cardiology", "MD, FACC Cardiology", 15, "9876543211", "priya.sharma@hospital.com", Decimal("1000.00"), DoctorStatus.ACTIVE),
            # Dermatology
            ("Dr. Anil Kumar", "Dermatology", "MD Dermatology (AIIMS)", 10, "9876543212", "anil.kumar@hospital.com", Decimal("700.00"), DoctorStatus.ACTIVE),
            ("Dr. Sneha Rao", "Dermatology", "MBBS, DVD Dermatology", 8, "9876543213", "sneha.rao@hospital.com", Decimal("600.00"), DoctorStatus.ACTIVE),
            # Orthopedics
            ("Dr. Kiran Reddy", "Orthopedics", "MS Orthopedics, MCh", 14, "9876543214", "kiran.reddy@hospital.com", Decimal("900.00"), DoctorStatus.ACTIVE),
            ("Dr. Rajesh Verma", "Orthopedics", "MS Ortho, Joint Replacement Fellow", 11, "9876543215", "rajesh.verma@hospital.com", Decimal("850.00"), DoctorStatus.ACTIVE),
            # Neurology
            ("Dr. Vikram Seth", "Neurology", "MD, DM Neurology", 16, "9876543216", "vikram.seth@hospital.com", Decimal("1200.00"), DoctorStatus.ACTIVE),
            ("Dr. Ananya Iyer", "Neurology", "MBBS, DNB Neurology", 9, "9876543217", "ananya.iyer@hospital.com", Decimal("950.00"), DoctorStatus.ACTIVE),
            # Pediatrics
            ("Dr. Meena Rao", "Pediatrics", "MD Pediatrics", 13, "9876543218", "meena.rao@hospital.com", Decimal("650.00"), DoctorStatus.ACTIVE),
            ("Dr. Sanjay Gupta", "Pediatrics", "DCH, DNB Pediatrics", 7, "9876543219", "sanjay.gupta@hospital.com", Decimal("550.00"), DoctorStatus.ACTIVE),
            # ENT
            ("Dr. Manoj Joshi", "ENT", "MS ENT (Head & Neck)", 12, "9876543220", "manoj.joshi@hospital.com", Decimal("700.00"), DoctorStatus.ACTIVE),
            # Gastroenterology
            ("Dr. Ramesh Patel", "Gastroenterology", "MD, DM Gastroenterology", 14, "9876543221", "ramesh.patel@hospital.com", Decimal("1100.00"), DoctorStatus.ACTIVE),
            # General Medicine
            ("Dr. Sunita Deshmukh", "General Medicine", "MD Internal Medicine", 18, "9876543222", "sunita.deshmukh@hospital.com", Decimal("500.00"), DoctorStatus.ACTIVE),
            ("Dr. Amit Roy", "General Medicine", "MBBS, DNB Family Medicine", 6, "9876543223", "amit.roy@hospital.com", Decimal("450.00"), DoctorStatus.ACTIVE),
            # Gynecology
            ("Dr. Pooja Menon", "Gynecology", "MS OBGYN, DGO", 11, "9876543224", "pooja.menon@hospital.com", Decimal("800.00"), DoctorStatus.ACTIVE),
            # Urology
            ("Dr. Suresh Nair", "Urology", "MS, MCh Urology", 15, "9876543225", "suresh.nair@hospital.com", Decimal("1000.00"), DoctorStatus.ACTIVE),
        ]

        doctor_map = {}
        for name, spec_name, qual, exp, phone, email, fee, status in doctors_data:
            stmt = select(Doctor).where(Doctor.email == email)
            existing = db.scalars(stmt).first()
            if not existing:
                doc = Doctor(
                    name=name,
                    specialty_id=specialty_map[spec_name].id,
                    qualification=qual,
                    experience_years=exp,
                    phone=phone,
                    email=email,
                    consultation_fee=fee,
                    status=status
                )
                db.add(doc)
                db.flush()
                doctor_map[name] = doc
            else:
                doctor_map[name] = existing

        print(f"[OK] Doctors: {len(doctor_map)} verified/seeded.")

        # 3. Seed 6 Patients
        patients_data = [
            ("Praveen Kumar", "9876500001", "praveen.k@example.com", 29, "Male"),
            ("Rohan Sharma", "9876500002", "rohan.s@example.com", 45, "Male"),
            ("Sunita Verma", "9876500003", "sunita.v@example.com", 38, "Female"),
            ("Priya Patel", "9876500004", "priya.p@example.com", 24, "Female"),
            ("Anand Kulkarni", "9876500005", "anand.k@example.com", 62, "Male"),
            ("Deepa Nair", "9876500006", "deepa.n@example.com", 33, "Female"),
        ]

        patient_map = {}
        for name, phone, email, age, gender in patients_data:
            stmt = select(Patient).where(Patient.phone == phone)
            existing = db.scalars(stmt).first()
            if not existing:
                pat = Patient(name=name, phone=phone, email=email, age=age, gender=gender)
                db.add(pat)
                db.flush()
                patient_map[name] = pat
            else:
                patient_map[name] = existing

        print(f"[OK] Patients: {len(patient_map)} verified/seeded.")

        # 4. Seed Schedules
        target_date = date(2026, 9, 25)
        schedules_to_create = [
            # Dr. Ravi Kumar: Morning shift (09:00 - 13:00), 30 min slots
            ("Dr. Ravi Kumar", target_date, time(9, 0), time(13, 0), 30),
            # Dr. Priya Sharma: Afternoon shift (14:00 - 18:00), 30 min slots
            ("Dr. Priya Sharma", target_date, time(14, 0), time(18, 0), 30),
            # Dr. Anil Kumar: Dermatology (10:00 - 14:00), 20 min slots
            ("Dr. Anil Kumar", target_date, time(10, 0), time(14, 0), 20),
            # Dr. Kiran Reddy: Orthopedics (09:00 - 13:00), 30 min slots
            ("Dr. Kiran Reddy", target_date, time(9, 0), time(13, 0), 30),
            # Dr. Meena Rao: Pediatrics (11:00 - 16:00), 30 min slots
            ("Dr. Meena Rao", target_date, time(11, 0), time(16, 0), 30),
            # Dr. Sunita Deshmukh: General Medicine (09:00 - 12:00), 30 min slots
            ("Dr. Sunita Deshmukh", target_date, time(9, 0), time(12, 0), 30),
        ]

        schedule_map = {}
        for doc_name, sched_date, s_time, e_time, dur in schedules_to_create:
            doc = doctor_map[doc_name]
            stmt = select(DoctorSchedule).where(
                DoctorSchedule.doctor_id == doc.id,
                DoctorSchedule.date == sched_date,
                DoctorSchedule.start_time == s_time
            )
            existing = db.scalars(stmt).first()
            if not existing:
                sched = DoctorSchedule(
                    doctor_id=doc.id,
                    date=sched_date,
                    start_time=s_time,
                    end_time=e_time,
                    slot_duration_minutes=dur,
                    status="active"
                )
                db.add(sched)
                db.flush()
                schedule_map[doc_name] = sched
            else:
                schedule_map[doc_name] = existing

        print(f"[OK] Schedules: {len(schedule_map)} verified/seeded.")

        # 5. Seed Test Appointments
        ravi_sched = schedule_map["Dr. Ravi Kumar"]
        priya_sched = schedule_map["Dr. Priya Sharma"]
        anil_sched = schedule_map["Dr. Anil Kumar"]

        appointments_data = [
            # Dr. Ravi at 10:00 (Patient: Praveen)
            (
                patient_map["Praveen Kumar"].id,
                doctor_map["Dr. Ravi Kumar"].id,
                ravi_sched.id,
                target_date,
                time(10, 0),
                time(10, 30),
                "Chest discomfort and routine cardiac consultation",
                AppointmentStatus.CONFIRMED,
            ),
            # Dr. Ravi at 11:30 (Patient: Rohan)
            (
                patient_map["Rohan Sharma"].id,
                doctor_map["Dr. Ravi Kumar"].id,
                ravi_sched.id,
                target_date,
                time(11, 30),
                time(12, 0),
                "Follow-up ECG consultation",
                AppointmentStatus.CONFIRMED,
            ),
            # Dr. Priya at 15:00 (Patient: Sunita)
            (
                patient_map["Sunita Verma"].id,
                doctor_map["Dr. Priya Sharma"].id,
                priya_sched.id,
                target_date,
                time(15, 0),
                time(15, 30),
                "Cardiac evaluation and second opinion",
                AppointmentStatus.CONFIRMED,
            ),
            # Dr. Anil at 10:40 (Patient: Priya Patel) - 20 min slot
            (
                patient_map["Priya Patel"].id,
                doctor_map["Dr. Anil Kumar"].id,
                anil_sched.id,
                target_date,
                time(10, 40),
                time(11, 0),
                "Persistent skin allergy and itching",
                AppointmentStatus.CONFIRMED,
            ),
        ]

        appointment_records = []
        for pat_id, doc_id, sch_id, apt_date, st, et, reason, status in appointments_data:
            stmt = select(Appointment).where(
                Appointment.doctor_id == doc_id,
                Appointment.appointment_date == apt_date,
                Appointment.start_time == st
            )
            existing = db.scalars(stmt).first()
            if not existing:
                apt = Appointment(
                    patient_id=pat_id,
                    doctor_id=doc_id,
                    schedule_id=sch_id,
                    appointment_date=apt_date,
                    start_time=st,
                    end_time=et,
                    reason=reason,
                    status=status
                )
                db.add(apt)
                db.flush()
                appointment_records.append(apt)
            else:
                appointment_records.append(existing)

        print(f"[OK] Appointments: {len(appointment_records)} verified/seeded.")

        # 6. Seed Calls
        calls_data = [
            (
                patient_map["Praveen Kumar"].id,
                "9876500001",
                datetime(2026, 9, 23, 10, 15, tzinfo=timezone.utc),
                datetime(2026, 9, 23, 10, 19, tzinfo=timezone.utc),
                240,
                "appointment_booking",
                "Cardiology",
                CallOutcome.APPOINTMENT_BOOKED,
                False,
            ),
            (
                patient_map["Rohan Sharma"].id,
                "9876500002",
                datetime(2026, 9, 23, 11, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 23, 11, 3, tzinfo=timezone.utc),
                180,
                "appointment_booking",
                "Cardiology",
                CallOutcome.APPOINTMENT_BOOKED,
                False,
            ),
            (
                patient_map["Anand Kulkarni"].id,
                "9876500005",
                datetime(2026, 9, 23, 11, 30, tzinfo=timezone.utc),
                datetime(2026, 9, 23, 11, 35, tzinfo=timezone.utc),
                300,
                "emergency_triage",
                "Cardiology",
                CallOutcome.HUMAN_TRANSFER,
                True,
            ),
        ]

        call_count = 0
        for pat_id, phone, st, et, dur, intent, spec, outcome, esc in calls_data:
            stmt = select(Call).where(
                Call.phone_number == phone,
                Call.started_at == st
            )
            existing = db.scalars(stmt).first()
            if not existing:
                call_record = Call(
                    patient_id=pat_id,
                    phone_number=phone,
                    started_at=st,
                    ended_at=et,
                    duration_seconds=dur,
                    intent=intent,
                    specialty_detected=spec,
                    outcome=outcome,
                    escalated=esc
                )
                db.add(call_record)
                call_count += 1

        db.flush()
        print(f"[OK] Calls: {len(calls_data)} verified/seeded.")

        # 7. Seed Notifications
        if appointment_records:
            first_apt = appointment_records[0]
            notifications_data = [
                # Patient SMS
                (
                    first_apt.id,
                    first_apt.patient_id,
                    None,
                    NotificationChannel.SMS,
                    f"Dear Praveen Kumar, your appointment with Dr. Ravi Kumar is confirmed for 25-Sep-2026 at 10:00 AM.",
                    NotificationStatus.SENT,
                    datetime.now(timezone.utc)
                ),
                # Doctor WhatsApp
                (
                    first_apt.id,
                    None,
                    first_apt.doctor_id,
                    NotificationChannel.WHATSAPP,
                    f"Dr. Ravi Kumar, new appointment booked: Praveen Kumar on 25-Sep-2026 at 10:00 AM. Reason: Chest discomfort.",
                    NotificationStatus.SENT,
                    datetime.now(timezone.utc)
                ),
            ]

            notif_count = 0
            for apt_id, pat_id, doc_id, ch, msg, st, sent_t in notifications_data:
                stmt = select(Notification).where(
                    Notification.appointment_id == apt_id,
                    Notification.patient_id == pat_id,
                    Notification.doctor_id == doc_id
                )
                existing = db.scalars(stmt).first()
                if not existing:
                    notif = Notification(
                        appointment_id=apt_id,
                        patient_id=pat_id,
                        doctor_id=doc_id,
                        channel=ch,
                        message=msg,
                        status=st,
                        sent_at=sent_t
                    )
                    db.add(notif)
                    notif_count += 1

        db.commit()
        print("\n--- Seeding Complete: All entities committed idempotently! ---")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
