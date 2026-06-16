/**
 * ProfilePage.jsx — User settings, profile data, and account deletion.
 *
 * Shows account info, fitness profile summary with edit option,
 * and danger zone.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PageWrapper from "../components/layout/PageWrapper";
import Card from "../components/common/Card";
import Input from "../components/common/Input";
import Button from "../components/common/Button";
import ConfirmDialog from "../components/common/ConfirmDialog";
import Spinner from "../components/common/Spinner";
import ErrorMessage from "../components/common/ErrorMessage";
import SuccessMessage from "../components/common/SuccessMessage";
import useAuthStore from "../store/authStore";
import useUserStore from "../store/userStore";
import userService from "../services/userService";

export default function ProfilePage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  
  const profile = useUserStore((s) => s.profile);
  const setProfile = useUserStore((s) => s.setProfile);
  const clearProfile = useUserStore((s) => s.clearProfile);

  const [isLoadingProfile, setIsLoadingProfile] = useState(!profile);
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [isSavingName, setIsSavingName] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await userService.getProfile();
        setProfile(res.data);
      } catch (err) {
        console.error("Failed to load profile:", err);
        setError("Failed to load fitness profile.");
      } finally {
        setIsLoadingProfile(false);
      }
    };
    if (!profile) fetchProfile();
  }, [profile, setProfile]);

  const handleSaveName = async () => {
    if (fullName === user.full_name) return;
    setIsSavingName(true);
    setError("");
    setSuccess("");
    try {
      const { data } = await userService.updateMe({ full_name: fullName });
      updateUser({ ...user, full_name: data.full_name });
      setSuccess("Profile updated successfully.");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update profile.");
    } finally {
      setIsSavingName(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    setError("");
    try {
      await userService.deleteAccount();
      clearAuth();
      clearProfile();
      localStorage.removeItem("refreshToken");
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete account.");
      setShowDeleteConfirm(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const nameChanged = fullName !== user?.full_name;

  if (isLoadingProfile) {
    return (
      <PageWrapper title="Profile">
        <div className="flex items-center justify-center py-20">
          <Spinner size="lg" />
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper title="Profile Settings">
      <div className="space-y-6 max-w-4xl mx-auto">
        {error && <ErrorMessage message={error} />}
        {success && <SuccessMessage message={success} />}

        {/* ── Account Info ────────────────────────────────────────────── */}
        <Card>
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center text-primary text-xl font-bold uppercase">
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <div>
              <h2 className="text-xl font-bold text-text-main">{user?.full_name}</h2>
              <p className="text-text-muted">{user?.email}</p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-text-main border-b border-border pb-2">Account Info</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  setSuccess("");
                }}
              />
              <Input
                label="Email"
                value={user?.email || ""}
                disabled
                className="opacity-70 bg-gray-50 cursor-not-allowed"
              />
            </div>
            {nameChanged && (
              <div className="flex justify-end">
                <Button variant="primary" onClick={handleSaveName} isLoading={isSavingName}>
                  Save Changes
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* ── Fitness Profile ─────────────────────────────────────────── */}
        <Card>
          <div className="flex items-center justify-between border-b border-border pb-2 mb-4">
            <h3 className="text-lg font-semibold text-text-main">Fitness Profile</h3>
            <Button
              variant="secondary"
              onClick={() => navigate("/onboarding")}
              className="py-1.5 px-3 text-xs"
            >
              Edit Profile
            </Button>
          </div>

          {profile ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-8 text-sm">
              <div className="flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Age</span>
                <span className="font-semibold">{profile.age}</span>
              </div>
              <div className="flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Gender</span>
                <span className="font-semibold capitalize">{profile.gender}</span>
              </div>
              <div className="flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Height</span>
                <span className="font-semibold">{profile.height_cm} cm</span>
              </div>
              <div className="flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Weight</span>
                <span className="font-semibold">{profile.weight_kg} kg</span>
              </div>
              <div className="flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Goal</span>
                <span className="font-semibold capitalize">{profile.fitness_goal?.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Activity Level</span>
                <span className="font-semibold capitalize">{profile.activity_level?.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Diet Type</span>
                <span className="font-semibold capitalize">{profile.diet_type?.replace('_', ' ')}</span>
              </div>
              <div className="flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Budget</span>
                <span className="font-semibold capitalize">{profile.budget_range?.replace('_', '-')}</span>
              </div>
              <div className="sm:col-span-2 flex justify-between border-b border-border/50 pb-2">
                <span className="text-text-muted">Equipment</span>
                <span className="font-semibold text-right">{profile.equipment?.join(", ") || "None"}</span>
              </div>
              <div className="sm:col-span-2 flex justify-between pb-2">
                <span className="text-text-muted">Allergies</span>
                <span className="font-semibold text-right">{profile.allergies || "None"}</span>
              </div>
            </div>
          ) : (
            <p className="text-text-muted text-sm py-4 text-center">
              Your fitness profile is incomplete.
            </p>
          )}
        </Card>

        {/* ── Danger Zone ─────────────────────────────────────────────── */}
        <Card className="border border-error/20 bg-error/5">
          <h3 className="text-lg font-semibold text-error mb-2">Danger Zone</h3>
          <p className="text-sm text-text-muted mb-4">
            Once you delete your account, there is no going back. This will permanently delete your user data, workout plans, and diet plans.
          </p>
          <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>
            Delete Account
          </Button>
        </Card>
      </div>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Account"
        message="Are you absolutely sure you want to delete your account? This action cannot be undone."
        confirmText="Yes, delete my account"
        onConfirm={handleDeleteAccount}
        onCancel={() => setShowDeleteConfirm(false)}
        isLoading={isDeleting}
        variant="danger"
      />
    </PageWrapper>
  );
}
