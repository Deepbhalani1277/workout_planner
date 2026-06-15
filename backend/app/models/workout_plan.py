"""
WorkoutPlan ORM model — the `workout_plans` table.

Each row is one AI-generated workout plan stored as JSONB.
Using JSONB (not TEXT) because:
 • PostgreSQL can index inside the JSON for fast queries
 • The plan structure may evolve without needing migrations
 • The frontend can receive the data as-is without parsing

is_active lets us soft-deactivate old plans when a new one is
generated, so the user always sees only their current plan while
history is preserved.

expires_at is nullable — set when plans have a time-bound validity
(e.g. a 4-week programme).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

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
    user = relationship("User", back_populates="workout_plans")
