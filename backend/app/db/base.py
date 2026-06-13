"""
SQLAlchemy declarative base + model registry.

Every ORM model inherits from `Base`.  We also import every model
here so that `Base.metadata` contains ALL table definitions.  Alembic's
autogenerate reads this metadata to detect schema changes.

If you add a new model file, import it here — otherwise Alembic
will not see it and will not generate a migration for it.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models (2.0 style)."""
    pass


# ── Import every model so Base.metadata registers their tables ──
from app.models.user import User                    # noqa: E402, F401
from app.models.profile import Profile              # noqa: E402, F401
from app.models.workout_plan import WorkoutPlan      # noqa: E402, F401
from app.models.diet_plan import DietPlan            # noqa: E402, F401
from app.models.refresh_token import RefreshToken    # noqa: E402, F401
