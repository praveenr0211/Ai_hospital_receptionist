from datetime import date as dt_date, time as dt_time
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Date, Time, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.doctor import Doctor
    from app.models.appointment import Appointment

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    __table_args__ = (
        UniqueConstraint("id", "doctor_id", name="uq_schedule_doctor"),
        CheckConstraint("start_time < end_time", name="chk_schedule_time_order"),
        CheckConstraint("slot_duration_minutes > 0", name="chk_slot_duration_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[dt_date] = mapped_column(Date, index=True, nullable=False)
    start_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    end_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="schedule",
        foreign_keys="[Appointment.schedule_id, Appointment.doctor_id]",
        overlaps="appointments,doctor"
    )

    def __repr__(self) -> str:
        return (
            f"<DoctorSchedule(id={self.id}, doctor_id={self.doctor_id}, date={self.date}, "
            f"hours={self.start_time}-{self.end_time}, duration={self.slot_duration_minutes}m)>"
        )
