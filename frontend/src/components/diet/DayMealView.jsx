/**
 * DayMealView — renders all 5 meals for a selected day
 * with the daily total calories at the top.
 */

import MealCard from "./MealCard";

const MEAL_SLOTS = ["breakfast", "snack_1", "lunch", "snack_2", "dinner"];

export default function DayMealView({ dayData, onSwapMeal }) {
  if (!dayData) return null;

  const handleSwap = async (mealSlot) => {
    if (onSwapMeal) {
      await onSwapMeal(dayData.day, mealSlot);
    }
  };

  return (
    <div>
      {/* Daily total calories */}
      <div className="flex items-center gap-3 mb-6 p-4 bg-primary/5 rounded-card border border-primary/10">
        <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
          <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 6.75 6.75 0 009 18.75a6.75 6.75 0 006.362-13.536z" />
          </svg>
        </div>
        <div>
          <p className="text-sm text-text-muted font-medium">Daily Target</p>
          <p className="text-xl font-bold text-primary">{dayData.total_calories} kcal</p>
        </div>
      </div>

      {/* Meal cards */}
      <div className="space-y-4">
        {MEAL_SLOTS.map((slot) => {
          const meal = dayData.meals[slot];
          if (!meal) return null;
          return (
            <MealCard
              key={slot}
              meal={meal}
              slotKey={slot}
              onSwap={handleSwap}
            />
          );
        })}
      </div>
    </div>
  );
}
