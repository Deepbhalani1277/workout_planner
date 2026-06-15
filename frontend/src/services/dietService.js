/**
 * Diet API service — diet plan HTTP calls.
 */

import api from "./api";

const dietService = {
  generatePlan: () => api.post("/diet/generate"),

  getActivePlan: () => api.get("/diet/me"),

  swapMeal: (day, mealSlot) =>
    api.post("/diet/swap-meal", { day, meal_slot: mealSlot }),

  deletePlan: () => api.delete("/diet/me"),
};

export default dietService;
