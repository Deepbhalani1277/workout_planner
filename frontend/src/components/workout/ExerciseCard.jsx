/**
 * ExerciseCard — displays a single exercise with name, sets, reps, rest, and tip.
 *
 * Uses orange accent badges for sets/reps and gray for rest time.
 */

export default function ExerciseCard({ exercise }) {
  const { name, sets, reps, rest_seconds, tip } = exercise;

  return (
    <div className="bg-card rounded-card shadow-card p-5 hover:shadow-card-hover transition-all duration-300 border border-border/50">
      <h4 className="text-base font-bold text-text-main mb-3">{name}</h4>

      <div className="flex flex-wrap gap-2 mb-3">
        {/* Sets x Reps badge */}
        <span className="inline-flex items-center gap-1 bg-primary/10 text-primary text-xs font-semibold px-3 py-1.5 rounded-full">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h4v12H4zm12 0h4v12h-4zM8 11h8v2H8z" />
          </svg>
          {sets} × {reps}
        </span>

        {/* Rest time badge */}
        <span className="inline-flex items-center gap-1 bg-gray-100 text-text-muted text-xs font-medium px-3 py-1.5 rounded-full">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {rest_seconds}s rest
        </span>
      </div>

      {tip && (
        <p className="text-xs text-text-muted italic leading-relaxed">
          💡 {tip}
        </p>
      )}
    </div>
  );
}
