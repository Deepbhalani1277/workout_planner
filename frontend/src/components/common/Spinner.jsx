/**
 * Animated spinner component.
 *
 * Orange spinning circle with three size options.
 */

const sizes = {
  sm: "w-4 h-4 border-2",
  md: "w-8 h-8 border-3",
  lg: "w-12 h-12 border-4",
};

export default function Spinner({ size = "md", className = "" }) {
  return (
    <div
      className={`${sizes[size]} border-primary/30 border-t-primary rounded-full animate-spin ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}
