/**
 * Error message display component.
 *
 * Red box with exclamation icon and error text.
 */

export default function ErrorMessage({ message }) {
  if (!message) return null;

  return (
    <div className="flex items-center gap-3 bg-error/10 border border-error/20 text-error rounded-input px-4 py-3 text-sm">
      <svg
        className="w-5 h-5 shrink-0"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
          clipRule="evenodd"
        />
      </svg>
      <span>{message}</span>
    </div>
  );
}
