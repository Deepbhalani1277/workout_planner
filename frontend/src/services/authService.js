/**
 * Auth API service — all authentication-related HTTP calls.
 */

import api from "./api";

const authService = {
  register: (fullName, email, password) =>
    api.post("/auth/register", {
      full_name: fullName,
      email,
      password,
    }),

  login: (email, password) =>
    api.post("/auth/login", { email, password }),

  googleLogin: (credential) =>
    api.post("/auth/google", { credential }),

  refreshToken: (refreshToken) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),

  logout: (refreshToken) =>
    api.post("/auth/logout", { refresh_token: refreshToken }),

  forgotPassword: (email) =>
    api.post("/auth/forgot-password", { email }),

  resetPassword: (token, newPassword) =>
    api.post("/auth/reset-password", {
      token,
      new_password: newPassword,
    }),

  verifyEmail: (token) =>
    api.post("/auth/verify-email", { token }),
};

export default authService;
