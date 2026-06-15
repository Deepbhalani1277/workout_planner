/**
 * Onboarding page — placeholder.
 * Will be fully implemented in the next phase.
 */

import PageWrapper from "../components/layout/PageWrapper";
import Card from "../components/common/Card";

export default function OnboardingPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <Card className="max-w-lg w-full text-center">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-text-main mb-2">Complete Your Profile</h2>
        <p className="text-text-muted">Onboarding wizard coming soon...</p>
      </Card>
    </div>
  );
}
