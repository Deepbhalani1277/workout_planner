/**
 * DashboardPage.jsx — Main user dashboard after onboarding.
 *
 * Shows welcome message, quick stats, and CTA cards to view or generate plans.
 */

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import PageWrapper from "../components/layout/PageWrapper";
import Card from "../components/common/Card";
import Button from "../components/common/Button";
import useAuthStore from "../store/authStore";
import useUserStore from "../store/userStore";
import userService from "../services/userService";
import usePlan from "../hooks/usePlan";
import Spinner from "../components/common/Spinner";
import ErrorMessage from "../components/common/ErrorMessage";

export default function DashboardPage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const profile = useUserStore((s) => s.profile);
  const setProfile = useUserStore((s) => s.setProfile);

  const {
    workoutPlan,
    dietPlan,
    fetchWorkout,
    fetchDiet,
    generateWorkout,
    generateDiet,
    isGeneratingWorkout,
    isGeneratingDiet,
    getPlanError,
  } = usePlan();

  const [isLoadingProfile, setIsLoadingProfile] = useState(!profile);
  const [error, setError] = useState("");

  useEffect(() => {
    // Fetch profile and active plans on mount
    const loadData = async () => {
      try {
        if (!profile) {
          const res = await userService.getProfile();
          setProfile(res.data);
        }
        await Promise.all([fetchWorkout(), fetchDiet()]);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
      } finally {
        setIsLoadingProfile(false);
      }
    };
    loadData();
  }, [profile, setProfile, fetchWorkout, fetchDiet]);

  const handleGenerateWorkout = async () => {
    setError("");
    try {
      await generateWorkout();
      navigate("/workout");
    } catch (err) {
      setError(getPlanError(err));
    }
  };

  const handleGenerateDiet = async () => {
    setError("");
    try {
      await generateDiet();
      navigate("/diet");
    } catch (err) {
      setError(getPlanError(err));
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 18) return "Good Afternoon";
    return "Good Evening";
  };

  if (isLoadingProfile) {
    return (
      <PageWrapper title="Dashboard">
        <div className="flex items-center justify-center py-20">
          <Spinner size="lg" />
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper title="Dashboard">
      {error && <div className="mb-6"><ErrorMessage message={error} /></div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Welcome card */}
        <Card className="md:col-span-2 lg:col-span-3 bg-gradient-to-br from-primary/10 to-transparent border border-primary/20">
          <h2 className="text-2xl font-bold text-text-main mb-2">
            {getGreeting()}, {user?.full_name?.split(" ")[0] || "User"} 👋
          </h2>
          <p className="text-text-muted">
            Your AI-powered fitness companion is ready to help you reach your goals.
          </p>
        </Card>

        {/* Quick Stats Row */}
        {profile && (
          <div className="md:col-span-2 lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-border p-4 rounded-xl text-center shadow-sm">
              <span className="block text-xs font-semibold text-text-muted uppercase mb-1">Goal</span>
              <span className="font-bold text-primary capitalize">{profile.fitness_goal.replace('_', ' ')}</span>
            </div>
            <div className="bg-white border border-border p-4 rounded-xl text-center shadow-sm">
              <span className="block text-xs font-semibold text-text-muted uppercase mb-1">Diet</span>
              <span className="font-bold text-success capitalize">{profile.diet_type.replace('_', ' ')}</span>
            </div>
            <div className="bg-white border border-border p-4 rounded-xl text-center shadow-sm">
              <span className="block text-xs font-semibold text-text-muted uppercase mb-1">Activity</span>
              <span className="font-bold text-blue-600 capitalize">{profile.activity_level.replace('_', ' ')}</span>
            </div>
            <div className="bg-white border border-border p-4 rounded-xl text-center shadow-sm">
              <span className="block text-xs font-semibold text-text-muted uppercase mb-1">Equipment</span>
              <span className="font-bold text-gray-800 text-sm">{profile.equipment.length} items</span>
            </div>
          </div>
        )}

        {/* Workout card */}
        <Card className="flex flex-col hover:shadow-card-hover transition-shadow duration-300">
          <div className="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center mb-5">
            <svg className="w-7 h-7 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h4v12H4zm12 0h4v12h-4zM2 10h2v4H2zm18 0h2v4h-2zM8 11h8v2H8z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-text-main">Workout Plan</h3>
          <p className="text-sm text-text-muted mt-2 mb-6 flex-1">
            {workoutPlan
              ? `Generated on ${new Date(workoutPlan.generated_at).toLocaleDateString()}`
              : "No active workout plan. Generate one based on your profile!"}
          </p>
          {workoutPlan ? (
            <Link to="/workout">
              <Button variant="secondary" fullWidth>View Plan</Button>
            </Link>
          ) : (
            <Button
              variant="primary"
              onClick={handleGenerateWorkout}
              isLoading={isGeneratingWorkout}
              fullWidth
            >
              Generate Plan
            </Button>
          )}
        </Card>

        {/* Diet card */}
        <Card className="flex flex-col hover:shadow-card-hover transition-shadow duration-300">
          <div className="w-14 h-14 bg-success/10 rounded-2xl flex items-center justify-center mb-5">
            <svg className="w-7 h-7 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-text-main">Diet Plan</h3>
          <p className="text-sm text-text-muted mt-2 mb-6 flex-1">
            {dietPlan
              ? `Generated on ${new Date(dietPlan.generated_at).toLocaleDateString()}`
              : "No active diet plan. Let AI craft your meals!"}
          </p>
          {dietPlan ? (
            <Link to="/diet">
              <Button variant="secondary" fullWidth className="border-success text-success hover:bg-success">
                View Plan
              </Button>
            </Link>
          ) : (
            <Button
              variant="primary"
              onClick={handleGenerateDiet}
              isLoading={isGeneratingDiet}
              fullWidth
              className="bg-success hover:bg-green-600 shadow-[0_2px_8px_rgba(16,185,129,0.3)]"
            >
              Generate Plan
            </Button>
          )}
        </Card>

        {/* Profile card */}
        <Card className="flex flex-col hover:shadow-card-hover transition-shadow duration-300">
          <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-5">
            <svg className="w-7 h-7 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-text-main">Profile Settings</h3>
          <p className="text-sm text-text-muted mt-2 mb-6 flex-1">
            Update your body metrics, goals, or diet preferences to get better plans.
          </p>
          <Link to="/profile">
            <Button variant="secondary" fullWidth className="border-blue-500 text-blue-600 hover:bg-blue-500">
              Manage Profile
            </Button>
          </Link>
        </Card>
      </div>
    </PageWrapper>
  );
}
