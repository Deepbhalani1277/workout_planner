"""
Workout Pydantic schemas — request/response bodies for
workout plan generation, retrieval, and deletion.

These schemas validate the JSON structure that Gemini returns
and define the shape of API responses.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Exercise ──────────────────────────────────────────────────

class ExerciseSchema(BaseModel):
    """
    A single exercise within a workout day.

    Fields:
     • name:         exercise name (e.g. "Push-ups")
     • sets:         number of sets
     • reps:         rep range as string (e.g. "12-15")
     • rest_seconds: rest between sets in seconds
     • tip:          form or technique tip
    """
    name: str
    sets: int
    reps: str
    rest_seconds: int
    tip: str


# ── Workout Day ───────────────────────────────────────────────

class WorkoutDaySchema(BaseModel):
    """
    One day within the 7-day workout plan.

    On rest days, is_rest_day=True and exercises=[] (empty list).
    """
    day: str
    focus: str
    is_rest_day: bool
    exercises: list[ExerciseSchema]


# ── Full Plan Data ────────────────────────────────────────────

class WorkoutPlanDataSchema(BaseModel):
    """
    The top-level structure returned by Gemini.
    Must contain exactly 7 days (Monday–Sunday).
    """
    week: list[WorkoutDaySchema] = Field(..., min_length=7, max_length=7)


# ── API Responses ─────────────────────────────────────────────

class WorkoutPlanResponse(BaseModel):
    """
    Response body for POST /workout/generate and GET /workout/me.

    plan_id and generated_at come from the DB row; plan is the
    validated Gemini output.
    """
    plan_id: uuid.UUID
    generated_at: datetime
    plan: WorkoutPlanDataSchema


class DeleteWorkoutResponse(BaseModel):
    message: str
