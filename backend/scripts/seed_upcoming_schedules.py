"""Seed doctor schedules for the next 14 days for all active doctors."""

from datetime import date, time, timedelta
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.doctor import Doctor
from app.models.schedule import DoctorSchedule

def seed_schedules():
    db = SessionLocal()
    try:
        doctors = db.scalars(select(Doctor).where(Doctor.status == "active")).all()
        print(f"Found {len(doctors)} active doctors.")
        
        today = date.today()
        # Seed for today + next 14 days
        dates_to_seed = [today + timedelta(days=i) for i in range(15)]
        
        # Schedule patterns:
        # Morning shift: 09:00 - 13:00 (30 min slots)
        # Afternoon shift: 14:00 - 18:00 (30 min slots)
        shifts = [
            (time(9, 0), time(13, 0), 30),
            (time(14, 0), time(18, 0), 30),
        ]
        
        created_count = 0
        for doc in doctors:
            for day in dates_to_seed:
                # Give doctors morning shift, or alternating shifts
                doc_shifts = shifts if doc.id % 2 == 0 else [shifts[0]]
                for start_t, end_t, dur in doc_shifts:
                    existing = db.scalars(
                        select(DoctorSchedule).where(
                            DoctorSchedule.doctor_id == doc.id,
                            DoctorSchedule.date == day,
                            DoctorSchedule.start_time == start_t
                        )
                    ).first()
                    
                    if not existing:
                        sched = DoctorSchedule(
                            doctor_id=doc.id,
                            date=day,
                            start_time=start_t,
                            end_time=end_t,
                            slot_duration_minutes=dur,
                            status="active"
                        )
                        db.add(sched)
                        created_count += 1
                        
        db.commit()
        print(f"[SUCCESS] Created {created_count} doctor schedule blocks for {len(dates_to_seed)} days.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_schedules()
