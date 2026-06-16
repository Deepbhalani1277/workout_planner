"""
DietPlan ORM model — the `diet_plans` table.

Mirrors the workout_plans structure: JSONB plan stored per user with
an is_active flag and optional expiry.

Kept as a separate table (rather than merging with workout_plans)
because:
 • Workout and diet plans have independent generation cycles
 • A user may regenerate one without touching the other
 • Query patterns differ (e.g. "show my meal plan" vs "show my workout")
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class DietPlan(Base):
    __tablename__ = "diet_plans"

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
        index=True,
        nullable=False,
    )

    # ── Plan content ──────────────────────────────────────────
    plan_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # ── Status ────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true")
    )

    # ── Timestamps ────────────────────────────────────────────
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ─────────────────────────────────────────
    user = relationship("User", back_populates="diet_plans")
