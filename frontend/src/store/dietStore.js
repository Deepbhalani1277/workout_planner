/**
 * Diet store — manages diet plan state.
 */

import { create } from "zustand";

const useDietStore = create((set) => ({
  // ── State ──────────────────────────────────────────────────
  dietPlan: null,
  isLoading: false,

  // ── Actions ────────────────────────────────────────────────
  setDietPlan: (plan) => set({ dietPlan: plan }),
  clearDietPlan: () => set({ dietPlan: null }),
  setLoading: (isLoading) => set({ isLoading }),
}));

export default useDietStore;
