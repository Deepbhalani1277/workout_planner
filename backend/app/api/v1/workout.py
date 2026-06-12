"""
Workout endpoints.

Generates AI-powered workout plans and lets users retrieve,
list, and manage their saved plans.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.post("/generate")
async def generate_workout():
    """Generate a personalised workout plan via AI."""
    return {"message": "generate workout — not yet implemented"}


@router.get("/")
async def list_workouts():
    """List all saved workout plans for the current user."""
    return {"message": "list workouts — not yet implemented"}


@router.get("/{plan_id}")
async def get_workout(plan_id: int):
    """Retrieve a specific workout plan by ID."""
    return {"message": f"get workout {plan_id} — not yet implemented"}
