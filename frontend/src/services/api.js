/**
 * Axios instance with interceptors for auth token management.
 *
 * Security:
 *  • Access token is read from Zustand store (in-memory only)
 *  • On 401 responses, automatically attempts a silent refresh
 *  • If refresh fails, clears auth state and redirects to /login
 *  • Never stores access tokens in localStorage
 */

import axios from "axios";
import useAuthStore from "../store/authStore";

// ── Axios instance ──────────────────────────────────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Track whether we're currently refreshing to avoid infinite loops
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// ── Request interceptor — attach Bearer token ───────────────
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor — handle 401 + silent refresh ──────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only attempt refresh on 401 and if we haven't already retried
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Don't refresh on auth endpoints (login, register, etc.)
    if (originalRequest.url?.includes("/auth/")) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // Queue this request — it will be retried after refresh completes
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      // Attempt to refresh using the stored refresh token
      const refreshToken = localStorage.getItem("refreshToken");
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken },
        { headers: { "Content-Type": "application/json" } }
      );

      const { access_token, refresh_token } = response.data;

      // Update store with new tokens
      const currentUser = useAuthStore.getState().user;
      useAuthStore.getState().setAuth(access_token, currentUser);

      // Store new refresh token (refresh token rotation)
      localStorage.setItem("refreshToken", refresh_token);

      // Retry all queued requests
      processQueue(null, access_token);

      // Retry the original request
      originalRequest.headers.Authorization = `Bearer ${access_token}`;
      return api(originalRequest);
    } catch (refreshError) {
      // Refresh failed — clear auth and redirect to login
      processQueue(refreshError, null);
      useAuthStore.getState().clearAuth();
      localStorage.removeItem("refreshToken");
      window.location.href = "/login";
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
