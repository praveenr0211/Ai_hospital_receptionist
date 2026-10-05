from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer, Text, DateTime, ForeignKey, CheckConstraint,
    Enum as SAEnum, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import NotificationChannel, NotificationStatus

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.patient import Patient
    from app.models.doctor import Doctor

class Notification(Base):
    __tablename__ = "notifications"

    __table_args__ = (
        CheckConstraint(
            "(patient_id IS NOT NULL AND doctor_id IS NULL) OR (patient_id IS NULL AND doctor_id IS NOT NULL)",
            name="chk_notification_single_recipient"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        SAEnum(NotificationChannel, values_callable=lambda obj: [e.value for e in obj], native_enum=False, length=20),
        default=NotificationChannel.SMS,
        nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        SAEnum(NotificationStatus, values_callable=lambda obj: [e.value for e in obj], native_enum=False, length=20),
        default=NotificationStatus.PENDING,
        nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="notifications")
    patient: Mapped["Patient | None"] = relationship("Patient", back_populates="notifications")
    doctor: Mapped["Doctor | None"] = relationship("Doctor", back_populates="notifications")

    def __repr__(self) -> str:
        recipient = f"patient={self.patient_id}" if self.patient_id else f"doctor={self.doctor_id}"
        return (
            f"<Notification(id={self.id}, apt={self.appointment_id}, {recipient}, "
            f"channel='{self.channel.value}', status='{self.status.value}', sent_at={self.sent_at})>"
        )
