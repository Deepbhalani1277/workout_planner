"""
Workout Pydantic schemas — request/response bodies for
workout plan generation and retrieval.
"""

from datetime import datetime

from pydantic import BaseModel


class WorkoutGenerateRequest(BaseModel):
    goal: str | None = None
    duration_weeks: int = 4
    notes: str | None = None


class WorkoutPlanOut(BaseModel):
    id: int
    user_id: int
    title: str
    plan_data: str
    duration_weeks: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
