/**
 * Reusable Button component.
 *
 * Variants: primary (orange), secondary (outline), danger (red)
 * Shows a spinner when isLoading=true.
 */

import Spinner from "./Spinner";

export default function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  isLoading = false,
  disabled = false,
  className = "",
  fullWidth = false,
}) {
  const base =
    "inline-flex items-center justify-center gap-2 font-semibold text-sm px-6 py-3 transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed";

  const variants = {
    primary:
      "bg-primary text-white hover:bg-primary-hover shadow-button rounded-button active:scale-[0.98]",
    secondary:
      "bg-transparent text-primary border-2 border-primary hover:bg-primary hover:text-white rounded-button active:scale-[0.98]",
    danger:
      "bg-error text-white hover:bg-red-600 rounded-button active:scale-[0.98]",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`${base} ${variants[variant]} ${fullWidth ? "w-full" : ""} ${className}`}
    >
      {isLoading ? (
        <>
          <Spinner size="sm" />
          <span>Loading...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
