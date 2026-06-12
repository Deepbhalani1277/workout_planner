"""
SQLAlchemy declarative base.

Every ORM model in the project inherits from `Base`. This single base
keeps all models registered in one metadata object, which Alembic uses
to auto-generate migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for all SQLAlchemy models.
    Using the modern DeclarativeBase class (SQLAlchemy 2.0 style).
    """
    pass
