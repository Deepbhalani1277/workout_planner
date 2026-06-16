"""
Diet service — business logic for generating, saving,
swapping meals in, and retrieving AI-powered diet / meal plans.

Flow (generate):
 1. User hits POST /diet/generate
 2. DietService fetches their profile
 3. Passes profile to AIService.generate_diet_plan()
 4. Deactivates any existing active diet plan (only one active at a time)
 5. Stores the new plan as JSONB in diet_plans table
 6. Returns the plan with its DB id and timestamp

Flow (swap_meal):
 1. User hits POST /diet/swap-meal with day + meal_slot
 2. DietService validates both values
 3. Calls AIService.swap_meal() to get a new meal
 4. Updates the specific slot in the plan_data JSONB
 5. Returns the new meal

Security:
 • user_id always comes from the JWT token
 • Ownership check before returning or mutating any plan data
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session


# ── Valid values for day and meal_slot ────────────────────────
VALID_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
VALID_MEAL_SLOTS = {"breakfast", "lunch", "dinner", "snack_1", "snack_2"}


class DietService:
    """
    Stateless service class — all methods are static so they
    can be called without instantiation.
    """

    # ── 1. Generate Plan ──────────────────────────────────────

    @staticmethod
    def generate_plan(db: Session, user_id: uuid.UUID, ai_service) -> dict:
        """
        Generate a new 7-day diet/meal plan via Gemini AI.

        Steps:
         1. Fetch the user's profile and check is_complete
         2. Call AI service to generate the plan
         3. Deactivate any existing active plan
         4. Store the new plan in DB
         5. Return plan_id, generated_at, and plan data
        """
        from app.models.diet_plan import DietPlan
        from app.models.profile import Profile

        # Fetch profile
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile or not profile.is_complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please complete your profile before generating a plan",
            )

        # Generate plan via AI
        plan_data = ai_service.generate_diet_plan(profile)

        # Deactivate existing active plan (only one active at a time)
        existing = (
            db.query(DietPlan)
            .filter(
                DietPlan.user_id == user_id,
                DietPlan.is_active == True,  # noqa: E712
            )
            .first()
        )
        if existing:
            existing.is_active = False

        # Create new plan
        new_plan = DietPlan(
            user_id=user_id,
            plan_data=plan_data,
            is_active=True,
        )
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)

        return {
            "plan_id": new_plan.id,
            "generated_at": new_plan.generated_at,
            "plan": plan_data,
        }

    # ── 2. Get Active Plan ────────────────────────────────────

    @staticmethod
    def get_active_plan(db: Session, user_id: uuid.UUID) -> dict:
        """
        Retrieve the user's current active diet plan.

        Each user has at most one active plan at a time.
        Returns 404 if no plan exists — the frontend should
        redirect to the "Generate Plan" flow.
        """
        from app.models.diet_plan import DietPlan

        plan = (
            db.query(DietPlan)
            .filter(
                DietPlan.user_id == user_id,
                DietPlan.is_active == True,  # noqa: E712
            )
            .first()
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No diet plan found. Please generate a plan first.",
            )

        return {
            "plan_id": plan.id,
            "generated_at": plan.generated_at,
            "plan": plan.plan_data,
        }

    # ── 3. Swap Meal ──────────────────────────────────────────

    @staticmethod
    def swap_meal(
        db: Session,
        user_id: uuid.UUID,
        day: str,
        meal_slot: str,
        ai_service,
    ) -> dict:
        """
        Swap a single meal in the active diet plan.

        Steps:
         1. Fetch the active diet plan → 404 if not found
         2. Fetch the user's profile
         3. Validate day (Monday–Sunday)
         4. Validate meal_slot (breakfast, lunch, dinner, snack_1, snack_2)
         5. Call AIService.swap_meal() to get a replacement meal
         6. Update plan_data[day][meal_slot] in the JSONB
         7. Persist to DB
         8. Return the new meal
        """
        from app.models.diet_plan import DietPlan
        from app.models.profile import Profile

        # Get active plan
        plan = (
            db.query(DietPlan)
            .filter(
                DietPlan.user_id == user_id,
                DietPlan.is_active == True,  # noqa: E712
            )
            .first()
        )
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active diet plan found.",
            )

        # Get profile for AI prompt context
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        # Validate day
        if day not in VALID_DAYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid day: '{day}'. Must be one of {sorted(VALID_DAYS)}",
            )

        # Validate meal_slot
        if meal_slot not in VALID_MEAL_SLOTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid meal_slot: '{meal_slot}'. Must be one of {sorted(VALID_MEAL_SLOTS)}",
            )

        # Generate a replacement meal via AI
        new_meal = ai_service.swap_meal(profile, day, meal_slot)

        # Update the specific meal slot in plan_data JSONB
        # plan_data structure: {"week": [{"day": "Monday", "meals": {...}}, ...]}
        plan_data = plan.plan_data
        for day_entry in plan_data.get("week", []):
            if day_entry.get("day") == day:
                day_entry["meals"][meal_slot] = new_meal
                break

        # Mark the JSONB column as modified so SQLAlchemy persists it
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(plan, "plan_data")
        db.commit()

        return {
            "day": day,
            "meal_slot": meal_slot,
            "meal": new_meal,
        }

    # ── 4. Delete Plan ────────────────────────────────────────

    @staticmethod
    def delete_plan(db: Session, user_id: uuid.UUID) -> dict:
        """
        Soft-delete the user's active diet plan.

        Sets is_active=False — the plan data stays in the DB
        for potential history/analytics features later.
        """
        from app.models.diet_plan import DietPlan

        plan = (
            db.query(DietPlan)
            .filter(
                DietPlan.user_id == user_id,
                DietPlan.is_active == True,  # noqa: E712
            )
            .first()
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active diet plan found to delete.",
            )

        plan.is_active = False
        db.commit()

        return {"message": "Diet plan deleted successfully"}
