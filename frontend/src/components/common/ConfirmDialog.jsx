/**
 * Confirm dialog — modal overlay with cancel/confirm buttons.
 */

export default function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "danger",
  onConfirm,
  onCancel,
  isLoading = false,
}) {
  if (!isOpen) return null;

  const confirmStyles = {
    danger: "bg-error text-white hover:bg-red-600",
    primary: "bg-primary text-white hover:bg-primary-hover shadow-button",
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={!isLoading ? onCancel : undefined}
      />

      {/* Dialog */}
      <div className="relative bg-white rounded-card shadow-2xl p-6 max-w-sm w-full animate-in fade-in zoom-in">
        <h3 className="text-lg font-bold text-text-main mb-2">{title}</h3>
        <p className="text-sm text-text-muted mb-6">{message}</p>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2.5 text-sm font-medium text-text-muted bg-gray-100 rounded-button
              hover:bg-gray-200 transition-all duration-200 cursor-pointer disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className={`px-4 py-2.5 text-sm font-medium rounded-button transition-all duration-200
              cursor-pointer disabled:opacity-50 ${confirmStyles[variant]}`}
          >
            {isLoading ? "Please wait..." : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
