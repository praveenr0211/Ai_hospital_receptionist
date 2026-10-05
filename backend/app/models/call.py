from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import CallOutcome

if TYPE_CHECKING:
    from app.models.patient import Patient

class Call(Base):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.id", ondelete="SET NULL"), index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    intent: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty_detected: Mapped[str | None] = mapped_column(String(100), nullable=True)
    outcome: Mapped[CallOutcome] = mapped_column(
        SAEnum(CallOutcome, values_callable=lambda obj: [e.value for e in obj], native_enum=False, length=50),
        default=CallOutcome.APPOINTMENT_BOOKED,
        nullable=False
    )
    escalated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Telephony and Voice Integration (Phase 6)
    provider: Mapped[str | None] = mapped_column(String(50), default="exotel", nullable=True)
    provider_call_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    stream_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    call_status: Mapped[str | None] = mapped_column(String(50), default="completed", nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    transfer_requested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    transfer_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recording_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transcript: Mapped[str | None] = mapped_column(String(4000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    patient: Mapped["Patient | None"] = relationship("Patient", back_populates="calls")

    def __repr__(self) -> str:
        return (
            f"<Call(id={self.id}, phone='{self.phone_number}', intent='{self.intent}', "
            f"outcome='{self.outcome.value}', call_status='{self.call_status}', escalated={self.escalated})>"
        )
