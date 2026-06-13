"""
Workout service — business logic for generating, saving,
and retrieving AI-powered workout plans.

Flow:
 1. User hits POST /workout/generate
 2. WorkoutService fetches their profile
 3. Passes profile to AIService.generate_workout_plan()
 4. Deactivates any existing active plan (only one active at a time)
 5. Stores the new plan as JSONB in workout_plans table
 6. Returns the plan with its DB id and timestamp

Security:
 • user_id always comes from the JWT token
 • Ownership check before returning any plan data
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class WorkoutService:
    """
    Stateless service class — all methods are static so they
    can be called without instantiation.
    """

    # ── 1. Generate Plan ──────────────────────────────────────

    @staticmethod
    def generate_plan(db: Session, user_id: uuid.UUID, ai_service) -> dict:
        """
        Generate a new 7-day workout plan via Gemini AI.

        Steps:
         1. Fetch the user's profile and check is_complete
         2. Call AI service to generate the plan
         3. Deactivate any existing active plan
         4. Store the new plan in DB
         5. Return plan_id, generated_at, and plan data
        """
        from app.models.profile import Profile
        from app.models.workout_plan import WorkoutPlan

        # Fetch profile
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile or not profile.is_complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please complete your profile before generating a plan",
            )

        # Generate plan via AI
        plan_data = ai_service.generate_workout_plan(profile)

        # Deactivate existing active plan (only one active at a time)
        existing = (
            db.query(WorkoutPlan)
            .filter(
                WorkoutPlan.user_id == user_id,
                WorkoutPlan.is_active == True,  # noqa: E712
            )
            .first()
        )
        if existing:
            existing.is_active = False

        # Create new plan
        new_plan = WorkoutPlan(
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
        Retrieve the user's current active workout plan.

        Each user has at most one active plan at a time.
        Returns 404 if no plan exists — the frontend should
        redirect to the "Generate Plan" flow.
        """
        from app.models.workout_plan import WorkoutPlan

        plan = (
            db.query(WorkoutPlan)
            .filter(
                WorkoutPlan.user_id == user_id,
                WorkoutPlan.is_active == True,  # noqa: E712
            )
            .first()
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No workout plan found. Please generate a plan first.",
            )

        return {
            "plan_id": plan.id,
            "generated_at": plan.generated_at,
            "plan": plan.plan_data,
        }

    # ── 3. Delete Plan ────────────────────────────────────────

    @staticmethod
    def delete_plan(db: Session, user_id: uuid.UUID) -> dict:
        """
        Soft-delete the user's active workout plan.

        Sets is_active=False — the plan data stays in the DB
        for potential history/analytics features later.
        """
        from app.models.workout_plan import WorkoutPlan

        plan = (
            db.query(WorkoutPlan)
            .filter(
                WorkoutPlan.user_id == user_id,
                WorkoutPlan.is_active == True,  # noqa: E712
            )
            .first()
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active workout plan found to delete.",
            )

        plan.is_active = False
        db.commit()

        return {"message": "Workout plan deleted successfully"}
