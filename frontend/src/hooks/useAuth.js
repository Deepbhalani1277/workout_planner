/**
 * useAuth hook — wraps authentication operations.
 *
 * Returns { user, isAuthenticated, isLoading, login, register, logout, googleLogin }
 * Handles token storage, store updates, and navigation after auth events.
 */

import { useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import useUserStore from "../store/userStore";
import useWorkoutStore from "../store/workoutStore";
import useDietStore from "../store/dietStore";
import authService from "../services/authService";

const ERROR_MESSAGES = {
  401: "Invalid email or password.",
  409: "An account with this email already exists.",
  422: "Please check your input and try again.",
  429: "Too many requests. Please wait before trying again.",
  500: "Something went wrong. Please try again later.",
  502: "Service is temporarily unavailable. Please try again.",
  default: "Unable to connect. Please try again.",
};

function getErrorMessage(err) {
  if (err.response?.data?.detail) {
    return typeof err.response.data.detail === "string"
      ? err.response.data.detail
      : "Validation error. Please check your input.";
  }
  const status = err.response?.status;
  return ERROR_MESSAGES[status] || ERROR_MESSAGES.default;
}

export default function useAuth() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const setAuth = useAuthStore((s) => s.setAuth);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const setIsOnboarded = useUserStore((s) => s.setIsOnboarded);
  const clearProfile = useUserStore((s) => s.clearProfile);
  const clearWorkoutPlan = useWorkoutStore((s) => s.clearWorkoutPlan);
  const clearDietPlan = useDietStore((s) => s.clearDietPlan);

  const login = async (email, password) => {
    const { data } = await authService.login(email, password);
    setAuth(data.access_token, data.user);
    localStorage.setItem("refreshToken", data.refresh_token);

    if (data.user.is_onboarded) {
      setIsOnboarded(true);
      navigate("/dashboard");
    } else {
      navigate("/onboarding");
    }
  };

  const register = async (fullName, email, password) => {
    await authService.register(fullName, email, password);
  };

  const logout = () => {
    const refreshToken = localStorage.getItem("refreshToken");
    if (refreshToken) {
      authService.logout(refreshToken).catch(() => {});
    }
    clearAuth();
    clearProfile();
    clearWorkoutPlan();
    clearDietPlan();
    localStorage.removeItem("refreshToken");
    navigate("/");
  };

  const googleLogin = async (credential) => {
    const { data } = await authService.googleLogin(credential);
    setAuth(data.access_token, data.user);
    localStorage.setItem("refreshToken", data.refresh_token);

    if (data.user.is_onboarded) {
      setIsOnboarded(true);
      navigate("/dashboard");
    } else {
      navigate("/onboarding");
    }
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    googleLogin,
    getErrorMessage,
  };
}

export { getErrorMessage };
