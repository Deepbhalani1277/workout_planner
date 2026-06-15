/**
 * usePlan hook — workout & diet plan operations.
 *
 * Returns helpers for generating, fetching, and managing plans
 * with loading states and error handling.
 */

import { useState } from "react";
import useWorkoutStore from "../store/workoutStore";
import useDietStore from "../store/dietStore";
import workoutService from "../services/workoutService";
import dietService from "../services/dietService";

const ERROR_MESSAGES = {
  429: "Too many requests. Please wait before trying again.",
  500: "Something went wrong. Please try again later.",
  502: "AI service is temporarily unavailable. Please try again.",
  default: "Unable to connect. Please try again.",
};

function getPlanError(err) {
  if (err.response?.data?.detail) {
    return typeof err.response.data.detail === "string"
      ? err.response.data.detail
      : "Something went wrong.";
  }
  const status = err.response?.status;
  return ERROR_MESSAGES[status] || ERROR_MESSAGES.default;
}

export default function usePlan() {
  const setWorkoutPlan = useWorkoutStore((s) => s.setWorkoutPlan);
  const setDietPlan = useDietStore((s) => s.setDietPlan);
  const workoutPlan = useWorkoutStore((s) => s.workoutPlan);
  const dietPlan = useDietStore((s) => s.dietPlan);

  const [isGeneratingWorkout, setIsGeneratingWorkout] = useState(false);
  const [isGeneratingDiet, setIsGeneratingDiet] = useState(false);
  const [isFetchingWorkout, setIsFetchingWorkout] = useState(false);
  const [isFetchingDiet, setIsFetchingDiet] = useState(false);

  const fetchWorkout = async () => {
    setIsFetchingWorkout(true);
    try {
      const { data } = await workoutService.getActivePlan();
      setWorkoutPlan(data);
      return data;
    } catch (err) {
      if (err.response?.status === 404) {
        setWorkoutPlan(null);
        return null;
      }
      throw err;
    } finally {
      setIsFetchingWorkout(false);
    }
  };

  const fetchDiet = async () => {
    setIsFetchingDiet(true);
    try {
      const { data } = await dietService.getActivePlan();
      setDietPlan(data);
      return data;
    } catch (err) {
      if (err.response?.status === 404) {
        setDietPlan(null);
        return null;
      }
      throw err;
    } finally {
      setIsFetchingDiet(false);
    }
  };

  const generateWorkout = async () => {
    setIsGeneratingWorkout(true);
    try {
      const { data } = await workoutService.generatePlan();
      setWorkoutPlan(data);
      return data;
    } finally {
      setIsGeneratingWorkout(false);
    }
  };

  const generateDiet = async () => {
    setIsGeneratingDiet(true);
    try {
      const { data } = await dietService.generatePlan();
      setDietPlan(data);
      return data;
    } finally {
      setIsGeneratingDiet(false);
    }
  };

  const swapMeal = async (day, mealSlot) => {
    const { data } = await dietService.swapMeal(day, mealSlot);
    // Update the diet plan in store with the swapped meal
    if (dietPlan) {
      const updatedPlan = { ...dietPlan };
      const updatedWeek = updatedPlan.plan.week.map((d) => {
        if (d.day === data.day) {
          return {
            ...d,
            meals: {
              ...d.meals,
              [data.meal_slot]: data.meal,
            },
          };
        }
        return d;
      });
      updatedPlan.plan = { ...updatedPlan.plan, week: updatedWeek };
      setDietPlan(updatedPlan);
    }
    return data;
  };

  return {
    workoutPlan,
    dietPlan,
    isGeneratingWorkout,
    isGeneratingDiet,
    isFetchingWorkout,
    isFetchingDiet,
    fetchWorkout,
    fetchDiet,
    generateWorkout,
    generateDiet,
    swapMeal,
    getPlanError,
  };
}
