"""
Shared pytest fixtures for the Workout Planner test suite.

Sets up:
 • A separate PostgreSQL test database (never touches dev/prod)
 • Overrides for FastAPI dependencies (DB session, settings)
 • A TestClient (httpx) pointed at the test app
 • Helper functions for creating users and auth tokens
 • Mocks for Redis and email services

The test database is workout_planner_test — configured via
TEST_DATABASE_URL in the .env file.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv

# ── Load .env so TEST_DATABASE_URL is available ──────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:admin123@localhost:5432/workout_planner_test",
)

# ── Override DATABASE_URL before importing the app ────────────
# This ensures the app's Settings object picks up the test DB,
# not the dev DB, when it is first instantiated.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# ── Mock Redis and email BEFORE importing the app ─────────────
# This prevents the app from connecting to real Redis on import.

mock_redis_store: dict[str, str] = {}


def mock_store_token(key: str, value: str, ttl_seconds: int) -> None:
    mock_redis_store[key] = value


def mock_get_token(key: str) -> str | None:
    return mock_redis_store.get(key)


def mock_delete_token(key: str) -> None:
    mock_redis_store.pop(key, None)


# Patch Redis functions before importing app modules
import app.core.redis as redis_module

redis_module.store_token = mock_store_token      # type: ignore[assignment]
redis_module.get_token = mock_get_token          # type: ignore[assignment]
redis_module.delete_token = mock_delete_token    # type: ignore[assignment]

# Patch the redis_client used by the rate limiter
redis_module.redis_client = MagicMock()          # type: ignore[assignment]
redis_module.get_redis = MagicMock(return_value=None)  # Disable rate limiting in tests

# Patch email sending
import app.utils.email as email_module

email_module.send_verification_email = MagicMock()       # type: ignore[assignment]
email_module.send_password_reset_email = MagicMock()     # type: ignore[assignment]

# Clear settings cache so test env vars are picked up
from app.config import get_settings

get_settings.cache_clear()

# ── Now import app components ─────────────────────────────────
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
)

# ── Import all models so Base.metadata is fully populated ─────
from app.models.user import User            # noqa: F401
from app.models.profile import Profile      # noqa: F401
from app.models.workout_plan import WorkoutPlan  # noqa: F401
from app.models.diet_plan import DietPlan   # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401


# ═══════════════════════════════════════════════════════════════
#  PostgreSQL Test Database Setup
# ═══════════════════════════════════════════════════════════════

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    """Provide a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


# ═══════════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def setup_database():
    """
    Create all tables before each test and drop them after.

    Ensures each test runs with a completely clean database.
    Uses PostgreSQL (workout_planner_test) so all PG-specific
    types like ARRAY and JSONB work correctly.
    """
    Base.metadata.create_all(bind=engine)
    mock_redis_store.clear()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Provide a test HTTP client."""
    return TestClient(fastapi_app)


@pytest.fixture
def db_session():
    """Provide a raw database session for test setup."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════
#  Helper Functions
# ═══════════════════════════════════════════════════════════════

def create_test_user(
    db,
    email: str = "test@example.com",
    password: str = "Test@1234",
    full_name: str = "Test User",
    is_verified: bool = True,
    is_active: bool = True,
):
    """
    Create a test user directly in the DB (bypassing registration).

    Also creates the associated empty Profile row, just like the
    real registration flow does.
    """
    from app.models.user import AuthProvider, User
    from app.models.profile import Profile

    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        auth_provider=AuthProvider.EMAIL,
        is_verified=is_verified,
        is_active=is_active,
    )
    db.add(user)
    db.flush()

    profile = Profile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(user)

    return user


def create_onboarded_user(db, email: str = "test@example.com"):
    """
    Create a user with a fully completed profile.

    This user has gone through the onboarding wizard —
    is_complete=True — so they can generate workout/diet plans.
    """
    from app.models.profile import Profile

    user = create_test_user(db, email=email)

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    profile.age = 25
    profile.gender = "male"
    profile.height_cm = 175.0
    profile.weight_kg = 70.0
    profile.fitness_goal = "muscle_gain"
    profile.activity_level = "moderate"
    profile.equipment = ["dumbbells", "barbell"]
    profile.diet_type = "non_vegetarian"
    profile.allergies = None
    profile.budget_range = "3000_6000"
    profile.is_complete = True
    db.commit()
    db.refresh(user)

    return user


def get_auth_header(user) -> dict[str, str]:
    """Generate an Authorization header for a test user."""
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


def get_refresh_token_for_user(db, user) -> str:
    """Create and store a refresh token for a test user."""
    from app.models.refresh_token import RefreshToken

    raw_token = create_refresh_token({"sub": str(user.id)})
    token_hash_val = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash_val,
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()

    return raw_token
