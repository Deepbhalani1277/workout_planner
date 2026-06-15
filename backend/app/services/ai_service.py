"""
AI service — wrapper around Google Gemini.

Provides a single interface for the rest of the app to request
AI-generated workout and diet plans.  Prompt construction is
delegated to utils/prompt_builder.py.

Architecture:
 • _get_gemini_client()        → initialises the Gemini model
 • _generate_with_retry()      → calls Gemini with retry logic
 • _parse_and_validate_response() → strips fences, parses JSON,
                                    validates structure
 • generate_workout_plan()     → builds prompt, calls Gemini,
                                  caches in Redis
 • generate_diet_plan()        → same pattern for diet
 • swap_meal()                 → generates a single replacement
                                  meal (no caching)

Security:
 • GEMINI_API_KEY loaded from env only, never hardcoded.
 • Never logs or exposes the API key.
 • Never sends user PII (name, email) to Gemini.
 • Free-text fields sanitised in prompt_builder before insertion.
"""

import hashlib
import json
import re
import time

from fastapi import HTTPException, status

from app.config import get_settings
from app.core.redis import delete_token, get_token, store_token
from app.utils.prompt_builder import (
    build_diet_prompt,
    build_swap_meal_prompt,
    build_workout_prompt,
)

settings = get_settings()


# ═══════════════════════════════════════════════════════════════
#  AIService
# ═══════════════════════════════════════════════════════════════

class AIService:
    """
    Stateless service class — all methods are static so they
    can be called without instantiation.
    """

    # ── Gemini client ─────────────────────────────────────────

    @staticmethod
    def _get_gemini_client():
        """
        Initialise and return a Gemini GenerativeModel instance.

        Uses google.generativeai (the currently installed SDK).
        Configures with GEMINI_API_KEY from environment and
        returns the gemini-1.5-flash model — fast and cheap,
        ideal for structured JSON generation.

        Raises a clear error if the API key is missing so the
        developer knows exactly what to fix.
        """
        import google.generativeai as genai

        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key == "your-gemini-api-key":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GEMINI_API_KEY is not configured. Set it in .env",
            )

        genai.configure(api_key=api_key)

        return genai.GenerativeModel("gemini-flash-latest")

    # ── Response parsing & validation ─────────────────────────

    @staticmethod
    def _parse_and_validate_response(
        response_text: str,
        plan_type: str,
    ) -> dict:
        """
        Parse raw Gemini output into a validated Python dict.

        Steps:
         1. Strip markdown code fences (```json ... ``` or ``` ... ```)
         2. Strip leading/trailing whitespace
         3. Parse as JSON
         4. Validate required keys based on plan_type

        Raises HTTPException 502 if parsing or validation fails —
        502 signals "bad gateway" (upstream service returned garbage),
        prompting the client to retry.
        """
        text = response_text.strip()

        # Strip markdown code fences — Gemini sometimes wraps
        # output in ```json ... ``` despite being told not to
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        # Parse JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}. Raw text: {repr(text)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI returned invalid response. Please try again.",
            )

        # Validate structure based on plan type
        if plan_type in ("workout", "diet"):
            if "week" not in data:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI returned invalid response. Please try again.",
                )
            if not isinstance(data["week"], list) or len(data["week"]) != 7:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI returned invalid response. Please try again.",
                )

        elif plan_type == "meal":
            required_keys = {
                "name", "calories", "protein_g",
                "carbs_g", "fat_g", "prep_note",
            }
            if not required_keys.issubset(data.keys()):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI returned invalid response. Please try again.",
                )

        return data

    # ── Retry wrapper ─────────────────────────────────────────

    @staticmethod
    def _generate_with_retry(
        prompt: str,
        max_retries: int = 3,
    ) -> str:
        """
        Call Gemini API with automatic retry on failure.

        Retries up to max_retries times with a 2-second delay
        between attempts.  If all retries fail, raises 502
        so the client knows the AI backend is temporarily down.

        Returns the raw response text on success.
        """
        model = AIService._get_gemini_client()
        last_error = None

        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                print(f"Gemini raw response (attempt {attempt}):", response.text)
                return response.text
            except Exception as e:
                print(f"Gemini error on attempt {attempt}:", repr(e))
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2)  # Brief pause before retry

        # All retries exhausted
        print("All Gemini retries exhausted. Last error:", repr(last_error))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service temporarily unavailable: {repr(last_error)}",
        )

    # ── Cache key builder ─────────────────────────────────────

    @staticmethod
    def _build_cache_key(prefix: str, **fields) -> str:
        """
        Build a deterministic cache key from profile fields.

        SHA-256-hashes the concatenated field values so the key
        is always a fixed length and doesn't leak PII into Redis.
        """
        raw = "|".join(str(v) for v in fields.values())
        hash_val = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_val}"

    # ── Generate Workout Plan ─────────────────────────────────
    # RATE LIMIT: max 5 calls per user per day (enforced in middleware)

    @staticmethod
    def generate_workout_plan(profile) -> dict:
        """
        Generate a 7-day personalised workout plan.

        Flow:
         1. Build a cache key from the profile fields that
            influence the workout (age, gender, weight, height,
            goal, equipment, activity level)
         2. Check Redis — if cached, return immediately
            (saves an API call and ~2-3 seconds of latency)
         3. Build the prompt via prompt_builder
         4. Call Gemini with retry
         5. Parse and validate the JSON response
         6. Cache for 24 hours in Redis
         7. Return the validated plan
        """
        # Cache key from workout-relevant fields
        cache_key = AIService._build_cache_key(
            "workout",
            age=profile.age,
            gender=profile.gender,
            weight=profile.weight_kg,
            height=profile.height_cm,
            goal=profile.fitness_goal,
            equipment=str(profile.equipment or []),
            activity=profile.activity_level,
        )

        # Check cache
        cached = get_token(cache_key)
        if cached:
            return json.loads(cached)

        # Generate
        prompt = build_workout_prompt(profile)
        response_text = AIService._generate_with_retry(prompt)
        plan = AIService._parse_and_validate_response(response_text, "workout")

        # Cache for 24 hours
        store_token(cache_key, json.dumps(plan), ttl_seconds=86400)

        return plan

    # ── Generate Diet Plan ────────────────────────────────────
    # RATE LIMIT: max 5 calls per user per day (enforced in middleware)

    @staticmethod
    def generate_diet_plan(profile) -> dict:
        """
        Generate a 7-day personalised Indian diet plan.

        Same flow as generate_workout_plan but with diet-specific
        cache key fields (includes diet_type, allergies, budget).
        """
        # Cache key from diet-relevant fields
        cache_key = AIService._build_cache_key(
            "diet",
            age=profile.age,
            gender=profile.gender,
            weight=profile.weight_kg,
            height=profile.height_cm,
            goal=profile.fitness_goal,
            diet_type=profile.diet_type,
            allergies=profile.allergies or "",
            budget=profile.budget_range,
        )

        # Check cache
        cached = get_token(cache_key)
        if cached:
            return json.loads(cached)

        # Generate
        prompt = build_diet_prompt(profile)
        response_text = AIService._generate_with_retry(prompt)
        plan = AIService._parse_and_validate_response(response_text, "diet")

        # Cache for 24 hours
        store_token(cache_key, json.dumps(plan), ttl_seconds=86400)

        return plan

    # ── Swap Meal ─────────────────────────────────────────────

    @staticmethod
    def swap_meal(profile, day: str, meal_slot: str) -> dict:
        """
        Generate a single replacement meal.

        NOT cached — every swap should return a different meal
        to give the user variety.

        Args:
            profile: ORM Profile object
            day: e.g. "Monday"
            meal_slot: one of "breakfast", "lunch", "dinner",
                       "snack_1", "snack_2"
        """
        prompt = build_swap_meal_prompt(profile, day, meal_slot)
        response_text = AIService._generate_with_retry(prompt)
        meal = AIService._parse_and_validate_response(response_text, "meal")

        return meal
