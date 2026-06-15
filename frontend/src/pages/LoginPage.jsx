/**
 * Login page.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import ErrorMessage from "../components/common/ErrorMessage";
import GoogleLoginButton from "../components/common/GoogleLoginButton";
import useAuthStore from "../store/authStore";
import useUserStore from "../store/userStore";
import authService from "../services/authService";
import userService from "../services/userService";

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const setIsOnboarded = useUserStore((s) => s.setIsOnboarded);

  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const { data } = await authService.login(form.email, form.password);
      setAuth(data.access_token, data.user);
      localStorage.setItem("refreshToken", data.refresh_token);

      // Check onboarding status
      if (data.user.is_onboarded) {
        setIsOnboarded(true);
        navigate("/dashboard");
      } else {
        navigate("/onboarding");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2">
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center">
              <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
            </div>
            <span className="text-2xl font-bold text-text-main">FitPlan</span>
          </Link>
          <h2 className="text-2xl font-bold text-text-main mt-6">Welcome back</h2>
          <p className="text-text-muted mt-2">Sign in to your account</p>
        </div>

        {/* Form */}
        <div className="bg-card rounded-card shadow-card p-8">
          {error && <ErrorMessage message={error} />}

          <form onSubmit={handleSubmit} className="space-y-5 mt-4">
            <Input
              label="Email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
            />
            <Input
              label="Password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />

            <div className="flex justify-end">
              <Link
                to="/forgot-password"
                className="text-sm text-primary hover:text-primary-hover font-medium"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              variant="primary"
              isLoading={isLoading}
              fullWidth
            >
              Sign In
            </Button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs text-text-muted font-medium">OR CONTINUE WITH</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Google Sign-In */}
          <GoogleLoginButton />
        </div>

        <p className="text-center text-sm text-text-muted mt-6">
          Don't have an account?{" "}
          <Link to="/register" className="text-primary hover:text-primary-hover font-semibold">
            Sign Up
          </Link>
        </p>
      </div>
    </div>
  );
}
