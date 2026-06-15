/**
 * Google Sign-In button using Google Identity Services (GSI).
 *
 * Renders the official Google "Sign in with Google" button.
 * On success, sends the credential (ID token) to the backend
 * for verification and account creation/login.
 */

import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../../store/authStore";
import useUserStore from "../../store/userStore";
import authService from "../../services/authService";
import ErrorMessage from "./ErrorMessage";

export default function GoogleLoginButton() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const setIsOnboarded = useUserStore((s) => s.setIsOnboarded);

  const buttonRef = useRef(null);
  const [error, setError] = useState("");

  useEffect(() => {
    // Wait for the Google SDK to load
    const initGoogle = () => {
      if (!window.google?.accounts?.id) {
        // SDK not loaded yet — retry after a short delay
        setTimeout(initGoogle, 200);
        return;
      }

      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
      });

      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: "outline",
        size: "large",
        width: "100%",
        text: "signin_with",
        shape: "rectangular",
        logo_alignment: "center",
      });
    };

    initGoogle();
  }, []);

  const handleCredentialResponse = async (response) => {
    setError("");

    try {
      const { data } = await authService.googleLogin(response.credential);
      setAuth(data.access_token, data.user);
      localStorage.setItem("refreshToken", data.refresh_token);

      if (data.user.is_onboarded) {
        setIsOnboarded(true);
        navigate("/dashboard");
      } else {
        navigate("/onboarding");
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || "Google sign-in failed. Please try again."
      );
    }
  };

  return (
    <div className="w-full">
      {error && <ErrorMessage message={error} />}
      <div ref={buttonRef} className="flex justify-center mt-2" />
    </div>
  );
}
