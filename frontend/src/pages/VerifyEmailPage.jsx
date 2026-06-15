/**
 * Email verification page — handles the ?token= query param.
 */

import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Button from "../components/common/Button";
import Spinner from "../components/common/Spinner";
import authService from "../services/authService";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("No verification token provided.");
      return;
    }

    authService
      .verifyEmail(token)
      .then((res) => {
        setStatus("success");
        setMessage(res.data.message);
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err.response?.data?.detail || "Verification failed.");
      });
  }, [token]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="bg-card rounded-card shadow-card p-8 max-w-md w-full text-center">
        {status === "loading" && (
          <>
            <Spinner size="lg" className="mx-auto mb-4" />
            <p className="text-text-muted">Verifying your email...</p>
          </>
        )}
        {status === "success" && (
          <>
            <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-text-main mb-2">Email Verified!</h2>
            <p className="text-text-muted mb-6">{message}</p>
            <Link to="/login">
              <Button variant="primary">Go to Login</Button>
            </Link>
          </>
        )}
        {status === "error" && (
          <>
            <div className="w-16 h-16 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-text-main mb-2">Verification Failed</h2>
            <p className="text-text-muted mb-6">{message}</p>
            <Link to="/login">
              <Button variant="secondary">Back to Login</Button>
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
