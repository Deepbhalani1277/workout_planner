"""
Diet endpoints.

Generates AI-powered diet/meal plans and lets users retrieve,
swap meals in, and manage their saved plans.

Thin controllers — all business logic lives in DietService.

Security:
 • Every route requires get_current_user (Bearer token).
 • user_id is ALWAYS taken from the authenticated token.
 • Users can only access their own diet plans.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.diet import (
    DeleteDietResponse,
    DietPlanResponse,
    SwapMealRequest,
    SwapMealResponse,
)
from app.services.ai_service import AIService
from app.services.diet_service import DietService

router = APIRouter(prefix="/diet", tags=["Diet"])


# ── Generate diet plan ────────────────────────────────────────
# RATE LIMIT: 5 per user per day (enforced in middleware)

@router.post("/generate", response_model=DietPlanResponse)
async def generate_diet(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate a new personalised 7-day diet plan via AI.

    Requires a complete profile (onboarding must be done first).
    Deactivates any existing active plan before creating the new one.
    """
    return DietService.generate_plan(
        db=db,
        user_id=current_user.id,
        ai_service=AIService,
    )


# ── Get active diet plan ─────────────────────────────────────

@router.get("/me", response_model=DietPlanResponse)
async def get_diet(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retrieve the current active diet plan for the
    authenticated user.

    Returns 404 if no plan has been generated yet.
    """
    return DietService.get_active_plan(
        db=db,
        user_id=current_user.id,
    )


# ── Swap a meal ──────────────────────────────────────────────

@router.post("/swap-meal", response_model=SwapMealResponse)
async def swap_meal(
    body: SwapMealRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Swap a single meal in the active diet plan.

    Provide the day (e.g. "Monday") and the meal_slot
    (breakfast, lunch, dinner, snack_1, snack_2).
    Returns the newly generated replacement meal.
    """
    return DietService.swap_meal(
        db=db,
        user_id=current_user.id,
        day=body.day,
        meal_slot=body.meal_slot,
        ai_service=AIService,
    )


# ── Delete active diet plan ──────────────────────────────────

@router.delete("/me", response_model=DeleteDietResponse)
async def delete_diet(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Soft-delete the current active diet plan.

    The plan data is preserved in the DB for history
    but is_active is set to False.
    """
    return DietService.delete_plan(
        db=db,
        user_id=current_user.id,
    )
