/**
 * Reset password page — handles the ?token= query param.
 */

import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import ErrorMessage from "../components/common/ErrorMessage";
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

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [form, setForm] = useState({ password: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  };

  const strength = getPasswordStrength(form.password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setIsLoading(true);
    setError("");

    try {
      await authService.resetPassword(token, form.password);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Reset failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-text-main">Reset Password</h2>
          <p className="text-text-muted mt-2">Enter your new password</p>
        </div>

        <div className="bg-card rounded-card shadow-card p-8">
          {success ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              </div>
              <p className="text-text-muted mb-4">Password reset successfully!</p>
              <Link to="/login">
                <Button variant="primary">Go to Login</Button>
              </Link>
            </div>
          ) : (
            <>
              {error && <ErrorMessage message={error} />}
              <form onSubmit={handleSubmit} className="space-y-5 mt-4">
                <div>
                  <Input
                    label="New Password"
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
                <Button type="submit" variant="primary" isLoading={isLoading} fullWidth>
                  Reset Password
                </Button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
