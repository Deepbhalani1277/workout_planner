"""
Database engine, session factory, and FastAPI dependency.

- `engine`        – The single SQLAlchemy engine bound to DATABASE_URL.
- `SessionLocal`  – A session factory; each call produces an independent
                    database session (connection + transaction).
- `get_db()`      – A FastAPI dependency that yields a session and
                    guarantees it is closed after the request finishes.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # verify connections before checkout
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — provides a SQLAlchemy session per request.
    The `finally` block ensures the connection is always returned
    to the pool, even if the endpoint raises an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
