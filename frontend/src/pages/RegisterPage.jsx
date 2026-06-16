/**
 * Register page.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import ErrorMessage from "../components/common/ErrorMessage";
import GoogleLoginButton from "../components/common/GoogleLoginButton";
import authService from "../services/authService";

const getPasswordStrength = (password) => {
  if (!password) return { label: "", color: "bg-gray-200", width: "w-0" };
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecial = /[^a-zA-Z0-d]/.test(password);
  const length = password.length;

  if (length >= 8 && hasLetter && hasNumber && hasSpecial) {
    return { label: "Strong", color: "bg-success", width: "w-full" };
  }
  if (length >= 6 && hasLetter && hasNumber) {
    return { label: "Medium", color: "bg-warning", width: "w-2/3" };
  }
  return { label: "Weak", color: "bg-error", width: "w-1/3" };
};

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  };

  const strength = getPasswordStrength(form.password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      setIsLoading(false);
      return;
    }

    try {
      await authService.register(form.full_name, form.email, form.password);
      navigate("/login", {
        state: { message: "Registration successful! Please check your email to verify your account." },
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-8">
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
          <h2 className="text-2xl font-bold text-text-main mt-6">Create your account</h2>
          <p className="text-text-muted mt-2">Start your fitness journey today</p>
        </div>

        {/* Form */}
        <div className="bg-card rounded-card shadow-card p-8">
          {error && <ErrorMessage message={error} />}

          <form onSubmit={handleSubmit} className="space-y-5 mt-4">
            <Input
              label="Full Name"
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              placeholder="John Doe"
              required
            />
            <Input
              label="Email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
            />
            <div>
              <Input
                label="Password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Min 8 chars, 1 number, 1 special"
                required
              />
              {form.password && (
                <div className="mt-2">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-medium text-text-muted">Password strength:</span>
                    <span className={`text-xs font-bold ${strength.label === "Weak" ? "text-error" : strength.label === "Medium" ? "text-warning" : "text-success"}`}>
                      {strength.label}
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div className={`h-full ${strength.color} ${strength.width} transition-all duration-300`} />
                  </div>
                </div>
              )}
            </div>
            <Input
              label="Confirm Password"
              name="confirmPassword"
              type="password"
              value={form.confirmPassword}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />

            <Button
              type="submit"
              variant="primary"
              isLoading={isLoading}
              fullWidth
            >
              Create Account
            </Button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs text-text-muted font-medium">OR SIGN UP WITH</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Google Sign-In */}
          <GoogleLoginButton />
        </div>

        <p className="text-center text-sm text-text-muted mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-primary hover:text-primary-hover font-semibold">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
