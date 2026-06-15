/**
 * Application routes with protected and public route guards.
 *
 * ProtectedRoute: redirects to /login if not authenticated,
 *   or /onboarding if not yet onboarded.
 * PublicRoute: redirects to /dashboard if already authenticated.
 */

import { Routes, Route, Navigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import useUserStore from "../store/userStore";
import Spinner from "../components/common/Spinner";

// ── Pages ────────────────────────────────────────────────────
import LandingPage from "../pages/LandingPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import VerifyEmailPage from "../pages/VerifyEmailPage";
import ForgotPasswordPage from "../pages/ForgotPasswordPage";
import ResetPasswordPage from "../pages/ResetPasswordPage";
import OnboardingPage from "../pages/OnboardingPage";
import DashboardPage from "../pages/DashboardPage";
import WorkoutPlanPage from "../pages/WorkoutPlanPage";
import DietPlanPage from "../pages/DietPlanPage";
import ProfilePage from "../pages/ProfilePage";

// ── Route Guards ─────────────────────────────────────────────

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const isOnboarded = useUserStore((s) => s.isOnboarded);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function OnboardedRoute({ children }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const isOnboarded = useUserStore((s) => s.isOnboarded);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!isOnboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  return children;
}

function PublicRoute({ children }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

// ── Route Definitions ────────────────────────────────────────

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/forgot-password" element={<PublicRoute><ForgotPasswordPage /></PublicRoute>} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Protected: needs auth only (onboarding can be incomplete) */}
      <Route path="/onboarding" element={<ProtectedRoute><OnboardingPage /></ProtectedRoute>} />

      {/* Protected: needs auth + onboarding complete */}
      <Route path="/dashboard" element={<OnboardedRoute><DashboardPage /></OnboardedRoute>} />
      <Route path="/workout" element={<OnboardedRoute><WorkoutPlanPage /></OnboardedRoute>} />
      <Route path="/diet" element={<OnboardedRoute><DietPlanPage /></OnboardedRoute>} />
      <Route path="/profile" element={<OnboardedRoute><ProfilePage /></OnboardedRoute>} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
