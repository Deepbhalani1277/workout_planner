/**
 * User store — manages user profile and onboarding state.
 */

import { create } from "zustand";

const useUserStore = create((set) => ({
  // ── State ──────────────────────────────────────────────────
  profile: null,
  isOnboarded: false,

  // ── Actions ────────────────────────────────────────────────
  setProfile: (profile) => set({ profile }),
  clearProfile: () => set({ profile: null, isOnboarded: false }),
  setIsOnboarded: (isOnboarded) => set({ isOnboarded }),
}));

export default useUserStore;
