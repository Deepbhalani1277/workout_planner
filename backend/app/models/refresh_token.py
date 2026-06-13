"""
RefreshToken ORM model — the `refresh_tokens` table.

Stores hashed refresh tokens in the database so we can:
 • Revoke individual tokens on logout (is_revoked = True)
 • Revoke ALL tokens for a user on password change (bulk update)
 • Enforce token expiry server-side (expires_at check)

The actual token value is never stored — only its SHA-256 hash
(token_hash). This way, even if the DB is compromised, the raw
tokens cannot be replayed.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

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

    # ── Token data ────────────────────────────────────────────
    token_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )

    # ── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ─────────────────────────────────────────
    user = relationship("User", back_populates="refresh_tokens")
