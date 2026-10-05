from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.doctor import Doctor

class Specialty(Base):
    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    doctors: Mapped[List["Doctor"]] = relationship("Doctor", back_populates="specialty")

    def __repr__(self) -> str:
        return f"<Specialty(id={self.id}, name='{self.name}', status={self.status})>"
