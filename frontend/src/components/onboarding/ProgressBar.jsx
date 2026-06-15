/**
 * Onboarding progress bar — shows step X of 7.
 *
 * Filled orange segments for completed steps, current step pulsing,
 * remaining steps in gray.
 */

export default function ProgressBar({ currentStep, totalSteps = 7 }) {
  const percent = ((currentStep) / totalSteps) * 100;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold text-text-main">
          Step {currentStep} of {totalSteps}
        </span>
        <span className="text-sm font-medium text-primary">
          {Math.round(percent)}%
        </span>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
          style={{ width: `${percent}%` }}
        />
      </div>
      <div className="flex gap-1 mt-3">
        {Array.from({ length: totalSteps }, (_, i) => (
          <div
            key={i}
            className={`flex-1 h-1 rounded-full transition-all duration-300 ${
              i < currentStep
                ? "bg-primary"
                : "bg-gray-200"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
