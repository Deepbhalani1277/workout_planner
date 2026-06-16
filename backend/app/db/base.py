"""
SQLAlchemy declarative base + model registry.

Every ORM model inherits from `Base`.  We also import every model
here so that `Base.metadata` contains ALL table definitions.  Alembic's
autogenerate reads this metadata to detect schema changes.

If you add a new model file, import it here — otherwise Alembic
will not see it and will not generate a migration for it.

IMPORTANT: Models should import Base from `app.db.base_class` (not
this file) to avoid circular imports.  This file is the ONLY place
that imports all models — it's the "registry" entrypoint.
"""

from app.db.base_class import Base  # noqa: F401

# ── Import every model so Base.metadata registers their tables ──
from app.models.user import User                    # noqa: E402, F401
from app.models.profile import Profile              # noqa: E402, F401
from app.models.workout_plan import WorkoutPlan      # noqa: E402, F401
from app.models.diet_plan import DietPlan            # noqa: E402, F401
from app.models.refresh_token import RefreshToken    # noqa: E402, F401
