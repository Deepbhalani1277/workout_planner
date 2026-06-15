/**
 * DietPlanPage.jsx — Shows the 7-day diet plan.
 *
 * Has 7 day tabs (Mon-Sun), and renders DayMealView for the selected day.
 */

import { useState, useEffect } from "react";
import PageWrapper from "../components/layout/PageWrapper";
import Card from "../components/common/Card";
import Button from "../components/common/Button";
import ConfirmDialog from "../components/common/ConfirmDialog";
import Spinner from "../components/common/Spinner";
import ErrorMessage from "../components/common/ErrorMessage";
import DayMealView from "../components/diet/DayMealView";
import usePlan from "../hooks/usePlan";

const DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default function DietPlanPage() {
  const {
    dietPlan,
    fetchDiet,
    generateDiet,
    swapMeal,
    isFetchingDiet,
    isGeneratingDiet,
    getPlanError,
  } = usePlan();

  const [activeDay, setActiveDay] = useState(
    DAYS_OF_WEEK[new Date().getDay() === 0 ? 6 : new Date().getDay() - 1]
  );
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!dietPlan) {
      fetchDiet().catch((err) => {
        if (err.response?.status !== 404) setError(getPlanError(err));
      });
    }
  }, [dietPlan, fetchDiet, getPlanError]);

  const handleRegenerate = async () => {
    setError("");
    try {
      await generateDiet();
      setShowConfirm(false);
    } catch (err) {
      setError(getPlanError(err));
      setShowConfirm(false);
    }
  };

  const handleSwapMeal = async (day, mealSlot) => {
    setError("");
    try {
      await swapMeal(day, mealSlot);
    } catch (err) {
      setError(getPlanError(err));
    }
  };

  if (isFetchingDiet) {
    return (
      <PageWrapper title="Your Meal Plan">
        <div className="flex items-center justify-center py-20">
          <Spinner size="lg" />
        </div>
      </PageWrapper>
    );
  }

  if (!dietPlan) {
    return (
      <PageWrapper title="Your Meal Plan">
        {error && <div className="mb-6"><ErrorMessage message={error} /></div>}
        <Card className="text-center py-16">
          <div className="w-20 h-20 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-text-main mb-2">No Plan Found</h2>
          <p className="text-text-muted mb-8 max-w-md mx-auto">
            You don't have an active diet plan. Let our AI generate a personalized 7-day meal plan based on your preferences.
          </p>
          <Button
            variant="primary"
            onClick={generateDiet}
            isLoading={isGeneratingDiet}
            className="px-8 bg-success hover:bg-green-600 shadow-[0_2px_8px_rgba(16,185,129,0.3)]"
          >
            Generate Meal Plan
          </Button>
        </Card>
      </PageWrapper>
    );
  }

  const activeDayData = dietPlan.plan.week.find((d) => d.day === activeDay);

  return (
    <PageWrapper title="Your Meal Plan">
      {error && <div className="mb-6"><ErrorMessage message={error} /></div>}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
        <p className="text-sm text-text-muted">
          Last updated: {new Date(dietPlan.generated_at).toLocaleDateString()}
        </p>
        <Button variant="secondary" onClick={() => setShowConfirm(true)} className="border-success text-success hover:bg-success">
          Regenerate Plan
        </Button>
      </div>

      {/* Day Tabs */}
      <div className="flex overflow-x-auto pb-4 mb-6 hide-scrollbar gap-2">
        {DAYS_OF_WEEK.map((day) => {
          const isActive = day === activeDay;
          return (
            <button
              key={day}
              onClick={() => setActiveDay(day)}
              className={`whitespace-nowrap px-5 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 cursor-pointer ${
                isActive
                  ? "bg-success text-white shadow-md"
                  : "bg-white text-text-muted hover:bg-gray-50 border border-border"
              }`}
            >
              {day.substring(0, 3)}
            </button>
          );
        })}
      </div>

      {/* Selected Day View */}
      <DayMealView dayData={activeDayData} onSwapMeal={handleSwapMeal} />

      <ConfirmDialog
        isOpen={showConfirm}
        title="Regenerate Plan?"
        message="This will overwrite your current 7-day diet plan with a new one. Are you sure?"
        confirmText="Yes, Regenerate"
        onConfirm={handleRegenerate}
        onCancel={() => setShowConfirm(false)}
        isLoading={isGeneratingDiet}
      />
    </PageWrapper>
  );
}
