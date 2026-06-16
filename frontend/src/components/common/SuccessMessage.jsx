/**
 * Success message box — green with check icon.
 */

export default function SuccessMessage({ message }) {
  if (!message) return null;

  return (
    <div className="flex items-center gap-3 bg-success/10 border border-success/20 text-green-700 rounded-input px-4 py-3 text-sm">
      <svg className="w-5 h-5 shrink-0 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{message}</span>
    </div>
  );
}
