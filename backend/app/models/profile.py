"""
Profile ORM model.

Stores user-specific fitness and dietary attributes used
by the AI service to personalise plans.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Physical attributes
    age: Mapped[int | None] = mapped_column(Integer)
    gender: Mapped[str | None] = mapped_column(String(20))
    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)

    # Fitness
    fitness_level: Mapped[str | None] = mapped_column(String(50))
    fitness_goal: Mapped[str | None] = mapped_column(String(100))
    workout_frequency: Mapped[int | None] = mapped_column(Integer)

    # Diet
    dietary_preference: Mapped[str | None] = mapped_column(String(100))
    allergies: Mapped[str | None] = mapped_column(Text)
    calorie_target: Mapped[int | None] = mapped_column(Integer)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="profile")
