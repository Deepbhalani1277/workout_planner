"""
Diet endpoints.

Generates AI-powered diet/meal plans and lets users retrieve,
list, and manage their saved plans.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/diet", tags=["Diet"])


@router.post("/generate")
async def generate_diet():
    """Generate a personalised diet plan via AI."""
    return {"message": "generate diet — not yet implemented"}


@router.get("/")
async def list_diets():
    """List all saved diet plans for the current user."""
    return {"message": "list diets — not yet implemented"}


@router.get("/{plan_id}")
async def get_diet(plan_id: int):
    """Retrieve a specific diet plan by ID."""
    return {"message": f"get diet {plan_id} — not yet implemented"}
