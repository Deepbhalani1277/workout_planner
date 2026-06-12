"""
Prompt builder — constructs structured prompts for Google Gemini.

Keeps prompt engineering in one place so that services just call
`build_workout_prompt(profile)` or `build_diet_prompt(profile)`
without worrying about formatting.
"""


def build_workout_prompt(profile: dict) -> str:
    """
    Build a Gemini prompt for generating a personalised workout plan.

    Args:
        profile: dict with keys like age, gender, height_cm,
                 weight_kg, fitness_level, fitness_goal, etc.
    """
    return (
        "You are a certified personal trainer. "
        "Create a detailed, personalised weekly workout plan based on "
        "the following user profile:\n\n"
        f"Age: {profile.get('age', 'N/A')}\n"
        f"Gender: {profile.get('gender', 'N/A')}\n"
        f"Height: {profile.get('height_cm', 'N/A')} cm\n"
        f"Weight: {profile.get('weight_kg', 'N/A')} kg\n"
        f"Fitness Level: {profile.get('fitness_level', 'N/A')}\n"
        f"Goal: {profile.get('fitness_goal', 'N/A')}\n"
        f"Workout Frequency: {profile.get('workout_frequency', 'N/A')} days/week\n\n"
        "Respond with a structured JSON workout plan."
    )


def build_diet_prompt(profile: dict) -> str:
    """
    Build a Gemini prompt for generating a personalised diet plan.

    Args:
        profile: dict with keys like age, gender, height_cm,
                 weight_kg, dietary_preference, allergies, etc.
    """
    return (
        "You are a certified nutritionist. "
        "Create a detailed, personalised daily meal plan based on "
        "the following user profile:\n\n"
        f"Age: {profile.get('age', 'N/A')}\n"
        f"Gender: {profile.get('gender', 'N/A')}\n"
        f"Height: {profile.get('height_cm', 'N/A')} cm\n"
        f"Weight: {profile.get('weight_kg', 'N/A')} kg\n"
        f"Dietary Preference: {profile.get('dietary_preference', 'N/A')}\n"
        f"Allergies: {profile.get('allergies', 'None')}\n"
        f"Calorie Target: {profile.get('calorie_target', 'N/A')} kcal/day\n"
        f"Goal: {profile.get('fitness_goal', 'N/A')}\n\n"
        "Respond with a structured JSON meal plan."
    )
