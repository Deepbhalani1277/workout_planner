"""
Workout endpoints.

Generates AI-powered workout plans and lets users retrieve
and manage their saved plans.

Thin controllers — all business logic lives in WorkoutService.

Security:
 • Every route requires get_current_user (Bearer token).
 • user_id is ALWAYS taken from the authenticated token.
 • Users can only access their own workout plans.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.workout import (
    DeleteWorkoutResponse,
    WorkoutPlanResponse,
)
from app.services.ai_service import AIService
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/workout", tags=["Workouts"])


# ── Generate workout plan ─────────────────────────────────────
# RATE LIMIT: 5 per user per day (enforced in middleware)

@router.post("/generate", response_model=WorkoutPlanResponse)
async def generate_workout(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate a new personalised 7-day workout plan via AI.

    Requires a complete profile (onboarding must be done first).
    Deactivates any existing active plan before creating the new one.
    """
    return WorkoutService.generate_plan(
        db=db,
        user_id=current_user.id,
        ai_service=AIService,
    )


# ── Get active workout plan ──────────────────────────────────

@router.get("/me", response_model=WorkoutPlanResponse)
async def get_workout(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retrieve the current active workout plan for the
    authenticated user.

    Returns 404 if no plan has been generated yet.
    """
    return WorkoutService.get_active_plan(
        db=db,
        user_id=current_user.id,
    )


# ── Delete active workout plan ───────────────────────────────

@router.delete("/me", response_model=DeleteWorkoutResponse)
async def delete_workout(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Soft-delete the current active workout plan.

    The plan data is preserved in the DB for history
    but is_active is set to False.
    """
    return WorkoutService.delete_plan(
        db=db,
        user_id=current_user.id,
    )
