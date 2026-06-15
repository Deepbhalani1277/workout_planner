/**
 * Landing page — public home page for unauthenticated users.
 */

import { Link } from "react-router-dom";
import Button from "../components/common/Button";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 lg:px-12 py-4">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
          </div>
          <span className="text-xl font-bold text-text-main">FitPlan</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="secondary">Log In</Button>
          </Link>
          <Link to="/register">
            <Button variant="primary">Sign Up</Button>
          </Link>
        </div>
      </header>

      {/* Hero */}
      <main className="flex-1 flex items-center justify-center px-6 lg:px-12">
        <div className="max-w-2xl text-center">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary text-sm font-medium px-4 py-2 rounded-full mb-6">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            AI-Powered Fitness
          </div>

          <h1 className="text-4xl lg:text-6xl font-extrabold text-text-main leading-tight mb-6">
            Your Personal{" "}
            <span className="text-primary">Workout & Diet</span>{" "}
            Planner
          </h1>

          <p className="text-lg text-text-muted mb-8 max-w-lg mx-auto">
            Get AI-generated workout and diet plans tailored to your body,
            goals, and preferences. Powered by Google Gemini.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button variant="primary" className="text-base px-8 py-4">
                Get Started Free →
              </Button>
            </Link>
          </div>

          {/* Feature pills */}
          <div className="flex flex-wrap justify-center gap-3 mt-12">
            {["Personalized Plans", "Indian Diet", "Meal Swapping", "Progress Tracking"].map((f) => (
              <span
                key={f}
                className="bg-white shadow-card px-4 py-2 rounded-full text-sm text-text-muted font-medium"
              >
                {f}
              </span>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
