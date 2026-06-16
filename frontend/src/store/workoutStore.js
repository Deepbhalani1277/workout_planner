/**
 * Workout store — manages workout plan state.
 */

import { create } from "zustand";

const useWorkoutStore = create((set) => ({
  // ── State ──────────────────────────────────────────────────
  workoutPlan: null,
  isLoading: false,

  // ── Actions ────────────────────────────────────────────────
  setWorkoutPlan: (plan) => set({ workoutPlan: plan }),
  clearWorkoutPlan: () => set({ workoutPlan: null }),
  setLoading: (isLoading) => set({ isLoading }),
}));

export default useWorkoutStore;
