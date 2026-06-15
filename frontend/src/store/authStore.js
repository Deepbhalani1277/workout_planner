/**
 * Auth store — manages authentication state in memory.
 *
 * The access token is NEVER stored in localStorage — it lives
 * only in Zustand's in-memory store. This prevents XSS attacks
 * from stealing tokens. The refresh token is sent via httpOnly
 * cookie or stored temporarily for the refresh flow.
 */

import { create } from "zustand";

const useAuthStore = create((set) => ({
  // ── State ──────────────────────────────────────────────────
  accessToken: null,
  user: null,
  isAuthenticated: false,
  isLoading: true, // true initially while checking auth on app load

  // ── Actions ────────────────────────────────────────────────
  setAuth: (token, user) =>
    set({
      accessToken: token,
      user,
      isAuthenticated: true,
      isLoading: false,
    }),

  clearAuth: () =>
    set({
      accessToken: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
    }),

  setLoading: (isLoading) => set({ isLoading }),

  updateUser: (user) => set({ user }),
}));

export default useAuthStore;
