/**
 * Root application component.
 *
 * On app load, attempts to restore auth state by calling
 * GET /users/me with any existing refresh token. If it fails,
 * clears auth and shows the public pages.
 */

import { useEffect } from "react";
import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes";
import useAuthStore from "./store/authStore";
import useUserStore from "./store/userStore";
import userService from "./services/userService";
import authService from "./services/authService";

export default function App() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const setLoading = useAuthStore((s) => s.setLoading);
  const setIsOnboarded = useUserStore((s) => s.setIsOnboarded);

  useEffect(() => {
    const restoreAuth = async () => {
      const refreshToken = localStorage.getItem("refreshToken");

      if (!refreshToken) {
        clearAuth();
        return;
      }

      try {
        // Try to get a fresh access token
        const refreshRes = await authService.refreshToken(refreshToken);
        const { access_token, refresh_token } = refreshRes.data;

        // Store new refresh token (rotation)
        localStorage.setItem("refreshToken", refresh_token);

        // Temporarily set token so the next API call is authenticated
        useAuthStore.setState({ accessToken: access_token });

        // Fetch user info
        const userRes = await userService.getMe();
        const user = userRes.data;

        setAuth(access_token, user);

        // Check onboarding
        if (user.is_onboarded !== undefined) {
          setIsOnboarded(user.is_onboarded);
        } else {
          // Fallback: check profile
          try {
            const profileRes = await userService.getProfile();
            setIsOnboarded(profileRes.data.is_complete);
          } catch {
            setIsOnboarded(false);
          }
        }
      } catch {
        // Refresh failed — user must log in again
        localStorage.removeItem("refreshToken");
        clearAuth();
      }
    };

    restoreAuth();
  }, []);

  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
