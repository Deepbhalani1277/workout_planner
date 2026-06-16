"""
AI service — wrapper around Groq API.

Provides a single interface for the rest of the app to request
AI-generated workout and diet plans. Prompt construction is
delegated to utils/prompt_builder.py.

Architecture:
 • _generate_with_retry()      → calls Groq with multi-key rotation and retry logic
 • _parse_and_validate_response() → parses JSON, validates structure
 • generate_workout_plan()     → builds prompt, calls Groq, caches in Redis
 • generate_diet_plan()        → same pattern for diet
 • swap_meal()                 → generates a single replacement meal (no caching)

Security:
 • GROQ_API_KEYS loaded from env only, never hardcoded.
 • Never sends user PII (name, email) to Groq.
 • Free-text fields sanitised in prompt_builder before insertion.
"""

import hashlib
import json
import re
import time

from fastapi import HTTPException, status
import groq

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

    _current_key_index = 0

    # ── Response parsing & validation ─────────────────────────

    @staticmethod
    def _parse_and_validate_response(
        response_text: str,
        plan_type: str,
    ) -> dict:
        """
        Parse raw Groq output into a validated Python dict.

        Steps:
         1. Strip markdown code fences (```json ... ``` or ``` ... ```)
         2. Strip leading/trailing whitespace
         3. Parse as JSON
         4. Validate required keys based on plan_type
        """
        text = response_text.strip()

        # Strip markdown code fences just in case
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

    # ── Retry & Rotation wrapper ──────────────────────────────

    @staticmethod
    def _generate_with_retry(
        prompt: str,
        max_retries: int = 3,
    ) -> str:
        """
        Call Groq API with automatic multi-key rotation and retry on failure.

        If a key hits a RateLimitError (quota exceeded) or AuthenticationError,
        it automatically switches to the next key in the comma-separated list
        from the environment variables.
        """
        keys = [k.strip() for k in settings.GROQ_API_KEYS.split(",") if k.strip()]
        if not keys:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GROQ_API_KEYS is not configured. Set it in .env"
            )

        last_error = None

        # Try up to the number of keys we have available
        for _ in range(len(keys)):
            current_key = keys[AIService._current_key_index % len(keys)]
            client = groq.Groq(api_key=current_key)

            for attempt in range(max_retries):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a helpful JSON generation assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    return response.choices[0].message.content
                except (groq.RateLimitError, groq.AuthenticationError) as e:
                    # Quota exceeded or Invalid key — rotate immediately!
                    print(f"Groq Key starting with {current_key[:12]}... failed: {e.__class__.__name__}. Rotating to next key.")
                    last_error = e
                    break  # Break inner loop to move to the next key
                except Exception as e:
                    # Random API timeout or error — retry same key
                    print(f"Groq Error on attempt {attempt}: {repr(e)}")
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(2)
            
            # Increment the index to use the next key for the next loop iteration (or future requests)
            AIService._current_key_index += 1

        # If we exit the outer loop, all keys and retries failed
        print("All API keys and retries exhausted. Last error:", repr(last_error))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable. Quota/Rate limit exceeded on all keys.",
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

    @staticmethod
    def generate_workout_plan(profile) -> dict:
        """
        Generate a 7-day personalised workout plan using Groq.
        """
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

        cached = get_token(cache_key)
        if cached:
            return json.loads(cached)

        prompt = build_workout_prompt(profile)
        response_text = AIService._generate_with_retry(prompt)
        plan = AIService._parse_and_validate_response(response_text, "workout")

        store_token(cache_key, json.dumps(plan), ttl_seconds=86400)
        return plan

    # ── Generate Diet Plan ────────────────────────────────────

    @staticmethod
    def generate_diet_plan(profile) -> dict:
        """
        Generate a 7-day personalised Indian diet plan using Groq.
        """
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

        cached = get_token(cache_key)
        if cached:
            return json.loads(cached)

        prompt = build_diet_prompt(profile)
        response_text = AIService._generate_with_retry(prompt)
        plan = AIService._parse_and_validate_response(response_text, "diet")

        store_token(cache_key, json.dumps(plan), ttl_seconds=86400)
        return plan

    # ── Swap Meal ─────────────────────────────────────────────

    @staticmethod
    def swap_meal(profile, day: str, meal_slot: str) -> dict:
        """
        Generate a single replacement meal using Groq.
        """
        prompt = build_swap_meal_prompt(profile, day, meal_slot)
        response_text = AIService._generate_with_retry(prompt)
        meal = AIService._parse_and_validate_response(response_text, "meal")

        return meal
