/**
 * Workout API service — workout plan HTTP calls.
 */

import api from "./api";

const workoutService = {
  generatePlan: () => api.post("/workout/generate"),

  getActivePlan: () => api.get("/workout/me"),

  deletePlan: () => api.delete("/workout/me"),
};

export default workoutService;
