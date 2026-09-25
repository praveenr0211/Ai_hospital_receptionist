from datetime import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import DoctorStatus

if TYPE_CHECKING:
    from app.models.specialty import Specialty
    from app.models.schedule import DoctorSchedule
    from app.models.appointment import Appointment
    from app.models.notification import Notification

class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id", ondelete="RESTRICT"), index=True, nullable=False)
    qualification: Mapped[str] = mapped_column(String(150), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    consultation_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    status: Mapped[DoctorStatus] = mapped_column(
        SAEnum(DoctorStatus, values_callable=lambda obj: [e.value for e in obj], native_enum=False, length=20),
        default=DoctorStatus.ACTIVE,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    specialty: Mapped["Specialty"] = relationship("Specialty", back_populates="doctors")
    schedules: Mapped[List["DoctorSchedule"]] = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="doctor")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="doctor")

    def __repr__(self) -> str:
        return f"<Doctor(id={self.id}, name='{self.name}', specialty_id={self.specialty_id}, status='{self.status.value}')>"
