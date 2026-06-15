"""
Declarative base class — separated from base.py to avoid
circular imports.

Models import Base from HERE (not base.py).
base.py imports Base from here + all models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models (2.0 style)."""
    pass
