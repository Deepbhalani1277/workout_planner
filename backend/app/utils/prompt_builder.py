"""
Prompt builder — constructs structured prompts for Google Gemini.

Keeps all prompt engineering in one place so that services just call
build_workout_prompt(profile) or build_diet_prompt(profile)
without worrying about formatting or JSON schema enforcement.

Security:
 • NEVER include user PII (name, email) in any prompt.
 • Free-text fields (allergies) are sanitised before insertion
   to prevent prompt injection attacks.
"""

import re


# ── Sanitisation ──────────────────────────────────────────────

def _sanitise_text(text: str | None, max_length: int = 200) -> str:
    """
    Sanitise free-text input before inserting into a prompt.

    Strips characters that could be used for prompt injection:
      < > { } [ ] | \\

    Truncates to max_length to prevent oversized prompts.
    Returns "None" if input is None or empty.
    """
    if not text or not text.strip():
        return "None"

    # Strip dangerous characters
    cleaned = re.sub(r"[<>{}\[\]|\\]", "", text)
    # Collapse whitespace
    cleaned = " ".join(cleaned.split())
    # Truncate
    return cleaned[:max_length]


# ── TDEE Calculator ──────────────────────────────────────────

def _calculate_tdee(
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    activity_level: str,
) -> int:
    """
    Estimate Total Daily Energy Expenditure (TDEE) using the
    Mifflin-St Jeor equation — the most accurate for general
    populations.

    BMR formula:
     • Male:   10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161 + 166
     • Female: 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161

    Activity multipliers:
     • sedentary:    1.2  (desk job, no exercise)
     • light:        1.375 (1-3 days/week)
     • moderate:     1.55 (3-5 days/week)
     • very_active:  1.725 (6-7 days/week)
    """
    # Mifflin-St Jeor BMR
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    if gender and gender.lower() == "male":
        bmr += 166  # +5 net adjustment for males

    # Activity multiplier
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
    }
    multiplier = multipliers.get(activity_level, 1.55)

    return round(bmr * multiplier)


# ── Budget description mapping ────────────────────────────────

_BUDGET_DESCRIPTIONS = {
    "below_3000": "very budget-friendly ingredients only (under ₹3000/month)",
    "3000_6000": "moderate cost ingredients (₹3000-6000/month)",
    "above_6000": "premium ingredients allowed (above ₹6000/month)",
}


# ═══════════════════════════════════════════════════════════════
#  Prompt Builders
# ═══════════════════════════════════════════════════════════════

def build_workout_prompt(profile) -> str:
    """
    Build a structured prompt for a 7-day personalised workout plan.

    Args:
        profile: ORM Profile object with attributes like age,
                 gender, height_cm, weight_kg, etc.

    The prompt instructs Gemini to:
     1. Act as a certified fitness trainer
     2. Generate 7 days with appropriate rest days
     3. Return ONLY valid JSON — no markdown, no explanation
     4. Follow the exact schema we specify
    """
    # Extract profile fields (safe — no PII)
    age = profile.age or "N/A"
    gender = profile.gender or "N/A"
    weight = profile.weight_kg or "N/A"
    height = profile.height_cm or "N/A"
    goal = profile.fitness_goal or "N/A"
    activity = profile.activity_level or "N/A"
    budget = profile.budget_range or "N/A"

    # Equipment list → comma-separated string
    equipment_list = profile.equipment or []
    equipment_str = ", ".join(equipment_list) if equipment_list else "No equipment (bodyweight only)"

    return f"""You are a certified fitness trainer with 15+ years of experience.

Generate a 7-day personalised workout plan based on this profile:

- Age: {age}
- Gender: {gender}
- Weight: {weight} kg
- Height: {height} cm
- Fitness Goal: {goal}
- Activity Level: {activity}
- Available Equipment: {equipment_str}
- Budget: {_BUDGET_DESCRIPTIONS.get(str(budget), str(budget))}

Rules:
1. Plan must cover all 7 days (Monday to Sunday).
2. Include appropriate rest days based on activity level:
   - sedentary/light: 3 rest days
   - moderate: 2 rest days
   - very_active: 1 rest day
3. Each workout day must have 4-6 exercises.
4. Each exercise must include: name, sets, reps, rest_seconds, tip.
5. Exercises must match available equipment.
6. On rest days, set is_rest_day=true and exercises=[].

Return ONLY valid JSON. No explanation. No markdown. No code fences.

Follow this EXACT JSON structure:
{{"week": [{{"day": "Monday", "focus": "Chest and Triceps", "is_rest_day": false, "exercises": [{{"name": "Push-ups", "sets": 3, "reps": "12-15", "rest_seconds": 60, "tip": "Keep core tight"}}]}}, {{"day": "Tuesday", "focus": "Rest", "is_rest_day": true, "exercises": []}}]}}"""


def build_diet_prompt(profile) -> str:
    """
    Build a structured prompt for a 7-day personalised Indian meal plan.

    Calculates approximate TDEE from profile data and includes
    it as the target daily calorie count.

    Args:
        profile: ORM Profile object.
    """
    age = profile.age or 25
    gender = profile.gender or "N/A"
    weight = profile.weight_kg or 70
    height = profile.height_cm or 170
    goal = profile.fitness_goal or "N/A"
    activity = profile.activity_level or "moderate"
    diet_type = profile.diet_type or "N/A"
    allergies = _sanitise_text(profile.allergies)
    budget = profile.budget_range or "N/A"

    # Calculate TDEE and adjust for goal
    tdee = _calculate_tdee(
        age=int(age),
        gender=str(gender),
        weight_kg=float(weight),
        height_cm=float(height),
        activity_level=str(activity),
    )

    # Adjust calories based on fitness goal
    goal_str = str(goal)
    if goal_str == "weight_loss":
        target_calories = tdee - 400  # ~400 cal deficit
        calorie_note = f"TDEE is ~{tdee} kcal. Target ~{target_calories} kcal (400 cal deficit for weight loss)."
    elif goal_str == "muscle_gain":
        target_calories = tdee + 300  # ~300 cal surplus
        calorie_note = f"TDEE is ~{tdee} kcal. Target ~{target_calories} kcal (300 cal surplus for muscle gain)."
    else:
        target_calories = tdee
        calorie_note = f"TDEE is ~{tdee} kcal. Target ~{target_calories} kcal (maintenance)."

    return f"""You are a certified Indian nutritionist with 15+ years of experience.

Generate a 7-day personalised Indian meal plan based on this profile:

- Age: {age}
- Gender: {gender}
- Weight: {weight} kg
- Height: {height} cm
- Fitness Goal: {goal}
- Activity Level: {activity}
- Diet Type: {diet_type}
- Allergies: {allergies}
- Budget: {_BUDGET_DESCRIPTIONS.get(str(budget), str(budget))}
- {calorie_note}

Rules:
1. ALL meals must be Indian cuisine ONLY.
2. Plan must cover all 7 days (Monday to Sunday).
3. Strictly respect diet type:
   - vegetarian: no meat, no eggs, no fish
   - non_vegetarian: all foods allowed
   - vegan: no animal products at all
   - eggetarian: vegetarian + eggs allowed
4. NEVER include any food the user is allergic to: {allergies}
5. Each day must have exactly 5 meals: breakfast, lunch, dinner, snack_1, snack_2.
6. Each meal must include: name, calories, protein_g, carbs_g, fat_g, prep_note.
7. Daily total_calories must be close to {target_calories} kcal.
8. Keep meals budget-friendly: {_BUDGET_DESCRIPTIONS.get(str(budget), str(budget))}.

Return ONLY valid JSON. No explanation. No markdown. No code fences.

Follow this EXACT JSON structure:
{{"week": [{{"day": "Monday", "total_calories": {target_calories}, "meals": {{"breakfast": {{"name": "Poha with peanuts", "calories": 350, "protein_g": 10, "carbs_g": 58, "fat_g": 8, "prep_note": "Add lemon juice at end"}}, "lunch": {{}}, "dinner": {{}}, "snack_1": {{}}, "snack_2": {{}}}}}}]}}"""


def build_swap_meal_prompt(profile, day: str, meal_slot: str) -> str:
    """
    Build a prompt to generate a single replacement meal.

    Args:
        profile: ORM Profile object.
        day: e.g. "Monday"
        meal_slot: one of "breakfast", "lunch", "dinner",
                   "snack_1", "snack_2"
    """
    age = profile.age or 25
    gender = profile.gender or "N/A"
    weight = profile.weight_kg or 70
    height = profile.height_cm or 170
    goal = profile.fitness_goal or "N/A"
    activity = profile.activity_level or "moderate"
    diet_type = profile.diet_type or "N/A"
    allergies = _sanitise_text(profile.allergies)
    budget = profile.budget_range or "N/A"

    tdee = _calculate_tdee(
        age=int(age),
        gender=str(gender),
        weight_kg=float(weight),
        height_cm=float(height),
        activity_level=str(activity),
    )

    return f"""You are a certified Indian nutritionist.

Generate ONE different Indian {meal_slot.replace("_", " ")} meal for {day}.

User profile:
- Age: {age}, Gender: {gender}
- Weight: {weight} kg, Height: {height} cm
- Goal: {goal}, Activity: {activity}
- Diet Type: {diet_type}
- Allergies: {allergies}
- Budget: {_BUDGET_DESCRIPTIONS.get(str(budget), str(budget))}
- Daily calorie target: ~{tdee} kcal

Rules:
1. Must be Indian cuisine ONLY.
2. Must be DIFFERENT from a typical {meal_slot.replace("_", " ")} meal.
3. Respect diet type ({diet_type}) strictly.
4. NEVER include allergens: {allergies}
5. Include: name, calories, protein_g, carbs_g, fat_g, prep_note.

Return ONLY valid JSON. No explanation. No markdown. No code fences.

Return this EXACT structure:
{{"name": "Dal Tadka with Roti", "calories": 420, "protein_g": 18, "carbs_g": 60, "fat_g": 10, "prep_note": "Use ghee for tadka"}}"""
