/**
 * User API service — user profile and onboarding HTTP calls.
 */

import api from "./api";

const userService = {
  getMe: () => api.get("/users/me"),

  updateMe: (data) => api.put("/users/me", data),

  getProfile: () => api.get("/users/profile"),

  saveOnboarding: (data) => api.post("/users/onboarding", data),

  updateOnboarding: (data) => api.put("/users/onboarding", data),

  deleteAccount: () => api.delete("/users/me"),
};

export default userService;
