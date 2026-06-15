/**
 * WorkoutDayView — renders either a rest day card or an exercise grid
 * for the selected day.
 */

import ExerciseCard from "./ExerciseCard";

export default function WorkoutDayView({ dayData }) {
  if (!dayData) return null;

  // Rest day
  if (dayData.is_rest_day) {
    return (
      <div className="bg-card rounded-card shadow-card p-8 text-center max-w-md mx-auto">
        <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-text-main mb-2">Rest Day 😴</h3>
        <p className="text-text-muted text-sm">
          Take it easy today! Your muscles need time to recover and grow stronger.
        </p>
      </div>
    );
  }

  // Workout day
  return (
    <div>
      {/* Focus badge */}
      <div className="mb-6">
        <span className="inline-flex items-center gap-2 bg-primary/10 text-primary font-semibold text-sm px-4 py-2 rounded-full">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 6.75 6.75 0 009 18.75a6.75 6.75 0 006.362-13.536z" />
          </svg>
          {dayData.focus}
        </span>
      </div>

      {/* Exercise grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {dayData.exercises.map((exercise, idx) => (
          <ExerciseCard key={idx} exercise={exercise} />
        ))}
      </div>
    </div>
  );
}
