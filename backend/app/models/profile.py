"""
Profile ORM model — the `profiles` table.

Stores every piece of user-specific data the AI needs to generate
personalised workout and diet plans:

 • Physical attributes — age, gender, height, weight
 • Fitness context     — goal, activity level, available equipment
 • Dietary context     — diet type, allergies, budget range
 • is_complete flag    — the frontend uses this to decide whether to
                         show the onboarding wizard or the dashboard.

The equipment column uses a PostgreSQL ARRAY(VARCHAR) so a single user
can list multiple items (e.g. ['dumbbells', 'resistance_bands']).

One-to-one with users via a unique constraint on user_id.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, func, text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


# ── ENUMs ─────────────────────────────────────────────────────

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class FitnessGoal(str, enum.Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTAIN = "maintain"
    STAMINA = "stamina"


class ActivityLevel(str, enum.Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    VERY_ACTIVE = "very_active"


class DietType(str, enum.Enum):
    VEGETARIAN = "vegetarian"
    NON_VEGETARIAN = "non_vegetarian"
    VEGAN = "vegan"
    EGGETARIAN = "eggetarian"


class BudgetRange(str, enum.Enum):
    BELOW_3000 = "below_3000"
    RANGE_3000_6000 = "3000_6000"
    ABOVE_6000 = "above_6000"


# ── Model ─────────────────────────────────────────────────────

class Profile(Base):
    __tablename__ = "profiles"

    # ── Primary key ───────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ── Owner ─────────────────────────────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # ── Physical attributes ───────────────────────────────────
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, name="gender_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Fitness ───────────────────────────────────────────────
    fitness_goal: Mapped[FitnessGoal | None] = mapped_column(
        Enum(FitnessGoal, name="fitness_goal_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    activity_level: Mapped[ActivityLevel | None] = mapped_column(
        Enum(ActivityLevel, name="activity_level_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    equipment: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )

    # ── Diet ──────────────────────────────────────────────────
    diet_type: Mapped[DietType | None] = mapped_column(
        Enum(DietType, name="diet_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_range: Mapped[BudgetRange | None] = mapped_column(
        Enum(BudgetRange, name="budget_range_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )

    # ── Onboarding flag ───────────────────────────────────────
    is_complete: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )

    # ── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────
    user = relationship("User", back_populates="profile")
