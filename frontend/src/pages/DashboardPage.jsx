/**
 * Dashboard page — placeholder.
 * Will be fully implemented in the next phase.
 */

import PageWrapper from "../components/layout/PageWrapper";
import Card from "../components/common/Card";
import useAuthStore from "../store/authStore";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <PageWrapper title="Dashboard">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Welcome card */}
        <Card className="md:col-span-2 lg:col-span-3">
          <h2 className="text-xl font-bold text-text-main mb-1">
            Welcome back, {user?.full_name || "User"} 👋
          </h2>
          <p className="text-text-muted">
            Your AI-powered fitness companion is ready.
          </p>
        </Card>

        {/* Workout card */}
        <Card className="hover:shadow-card-hover transition-shadow duration-300">
          <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h4v12H4zm12 0h4v12h-4zM2 10h2v4H2zm18 0h2v4h-2zM8 11h8v2H8z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-text-main">Workout Plan</h3>
          <p className="text-sm text-text-muted mt-1">View or generate your workout plan</p>
        </Card>

        {/* Diet card */}
        <Card className="hover:shadow-card-hover transition-shadow duration-300">
          <div className="w-12 h-12 bg-success/10 rounded-xl flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-text-main">Diet Plan</h3>
          <p className="text-sm text-text-muted mt-1">View or generate your diet plan</p>
        </Card>

        {/* Profile card */}
        <Card className="hover:shadow-card-hover transition-shadow duration-300">
          <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-text-main">Profile</h3>
          <p className="text-sm text-text-muted mt-1">Update your profile and preferences</p>
        </Card>
      </div>
    </PageWrapper>
  );
}
