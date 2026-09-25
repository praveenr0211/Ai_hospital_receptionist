from datetime import datetime, date as dt_date, time as dt_time
from typing import List, TYPE_CHECKING
from sqlalchemy import (
    Integer, Text, Date, Time, DateTime, ForeignKeyConstraint,
    CheckConstraint, Index, Enum as SAEnum, func, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import AppointmentStatus

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.doctor import Doctor
    from app.models.schedule import DoctorSchedule
    from app.models.notification import Notification

class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        ForeignKeyConstraint(
            ["schedule_id", "doctor_id"],
            ["doctor_schedules.id", "doctor_schedules.doctor_id"],
            ondelete="CASCADE",
            name="fk_appointment_schedule_doctor"
        ),
        ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            ondelete="RESTRICT",
            name="fk_appointment_patient"
        ),
        ForeignKeyConstraint(
            ["doctor_id"],
            ["doctors.id"],
            ondelete="RESTRICT",
            name="fk_appointment_doctor"
        ),
        CheckConstraint("start_time < end_time", name="chk_appointment_time_order"),
        Index(
            "uq_doctor_active_slot",
            "doctor_id",
            "appointment_date",
            "start_time",
            unique=True,
            postgresql_where=text("status != 'cancelled'")
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    doctor_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    schedule_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    appointment_date: Mapped[dt_date] = mapped_column(Date, index=True, nullable=False)
    start_time: Mapped[dt_time] = mapped_column(Time, index=True, nullable=False)
    end_time: Mapped[dt_time] = mapped_column(Time, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(AppointmentStatus, values_callable=lambda obj: [e.value for e in obj], native_enum=False, length=20),
        default=AppointmentStatus.CONFIRMED,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(
        "Doctor",
        back_populates="appointments",
        foreign_keys=[doctor_id],
        overlaps="appointments,schedule"
    )
    schedule: Mapped["DoctorSchedule"] = relationship(
        "DoctorSchedule",
        back_populates="appointments",
        foreign_keys=[schedule_id, doctor_id],
        overlaps="appointments,doctor"
    )
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="appointment")

    def __repr__(self) -> str:
        return (
            f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, "
            f"date={self.appointment_date}, time={self.start_time}-{self.end_time}, status='{self.status.value}')>"
        )
