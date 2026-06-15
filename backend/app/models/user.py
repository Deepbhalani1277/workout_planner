"""
User ORM model — the `users` table.

This is the central identity table. Every person who signs up (via
email/password or Google OAuth) gets a row here.

Key design decisions:
 • UUID primary keys   — avoids exposing sequential IDs in URLs and
                         makes future multi-DB merges trivial.
 • auth_provider ENUM  — distinguishes email-registered users from
                         Google OAuth users so the login flow knows
                         which credential to check.
 • password_hash nullable — Google users authenticate via ID-token,
                            so they never set a local password.
 • google_id           — the `sub` claim from Google's ID token,
                         used to match returning OAuth users.
 • is_verified         — email verification gate before granting
                         full access (OTP / link flow).
 • Relationships       — one-to-one with profile, one-to-many with
                         workout_plans, diet_plans, and refresh_tokens.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AuthProvider(str, enum.Enum):
    """How the user registered — email/password or Google OAuth."""
    EMAIL = "email"
    GOOGLE = "google"


class User(Base):
    __tablename__ = "users"

    # ── Primary key ───────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ── Credentials & identity ────────────────────────────────
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    full_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    # ── Auth provider ─────────────────────────────────────────
    auth_provider: Mapped[AuthProvider] = mapped_column(
        Enum(
            AuthProvider,
            name="auth_provider_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        server_default=AuthProvider.EMAIL.value,
        nullable=False,
    )
    google_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )

    # ── Account flags ─────────────────────────────────────────
    is_verified: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true")
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
    profile = relationship(
        "Profile", back_populates="user", uselist=False,
        cascade="all, delete-orphan",
    )
    workout_plans = relationship(
        "WorkoutPlan", back_populates="user",
        cascade="all, delete-orphan",
    )
    diet_plans = relationship(
        "DietPlan", back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user",
        cascade="all, delete-orphan",
    )
