/**
 * MealCard — displays a single meal with name, calories, macros, prep note,
 * and a swap button.
 */

import { useState } from "react";
import Spinner from "../common/Spinner";

const SLOT_LABELS = {
  breakfast: "🌅 Breakfast",
  lunch: "☀️ Lunch",
  dinner: "🌙 Dinner",
  snack_1: "🍎 Snack 1",
  snack_2: "🥤 Snack 2",
};

export default function MealCard({ meal, slotKey, onSwap }) {
  const [isSwapping, setIsSwapping] = useState(false);

  const handleSwap = async () => {
    setIsSwapping(true);
    try {
      await onSwap(slotKey);
    } finally {
      setIsSwapping(false);
    }
  };

  return (
    <div className="bg-card rounded-card shadow-card p-5 hover:shadow-card-hover transition-all duration-300 border border-border/50">
      {/* Slot label */}
      <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
        {SLOT_LABELS[slotKey] || slotKey}
      </span>

      {/* Meal name + calories */}
      <div className="flex items-start justify-between mt-2 mb-3">
        <h4 className="text-base font-bold text-text-main leading-snug flex-1 mr-2">
          {meal.name}
        </h4>
        <span className="shrink-0 inline-flex items-center bg-primary/10 text-primary text-xs font-bold px-3 py-1 rounded-full">
          {meal.calories} kcal
        </span>
      </div>

      {/* Macro pills */}
      <div className="flex flex-wrap gap-2 mb-3">
        <span className="inline-flex items-center bg-blue-50 text-blue-600 text-xs font-medium px-2.5 py-1 rounded-full">
          Protein: {meal.protein_g}g
        </span>
        <span className="inline-flex items-center bg-green-50 text-green-600 text-xs font-medium px-2.5 py-1 rounded-full">
          Carbs: {meal.carbs_g}g
        </span>
        <span className="inline-flex items-center bg-yellow-50 text-yellow-600 text-xs font-medium px-2.5 py-1 rounded-full">
          Fat: {meal.fat_g}g
        </span>
      </div>

      {/* Prep note */}
      {meal.prep_note && (
        <p className="text-xs text-text-muted italic leading-relaxed mb-3">
          📝 {meal.prep_note}
        </p>
      )}

      {/* Swap button */}
      <button
        onClick={handleSwap}
        disabled={isSwapping}
        className="inline-flex items-center gap-1.5 text-xs font-medium text-primary border border-primary/30
          px-3 py-1.5 rounded-lg hover:bg-primary/5 transition-all duration-200 cursor-pointer
          disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSwapping ? (
          <>
            <Spinner size="sm" />
            Swapping...
          </>
        ) : (
          <>
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
            </svg>
            Swap Meal
          </>
        )}
      </button>
    </div>
  );
}
