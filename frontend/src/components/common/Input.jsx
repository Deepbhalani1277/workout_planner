/**
 * Reusable Input component.
 *
 * Shows label above, error message below in red.
 * Orange focus ring styling.
 */

export default function Input({
  label,
  type = "text",
  value,
  onChange,
  error,
  placeholder,
  required = false,
  name,
  className = "",
  ...props
}) {
  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label
          htmlFor={name}
          className="text-sm font-medium text-text-main"
        >
          {label}
          {required && <span className="text-error ml-1">*</span>}
        </label>
      )}

      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={`w-full px-4 py-3 bg-white border text-text-main placeholder-text-muted
          rounded-input text-sm transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
          ${error ? "border-error" : "border-border"}
          ${className}`}
        {...props}
      />

      {error && (
        <p className="text-xs text-error mt-0.5 flex items-center gap-1">
          <svg
            className="w-3.5 h-3.5 shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
