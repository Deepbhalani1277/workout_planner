/**
 * Reusable Card component.
 *
 * White background, rounded corners, soft shadow.
 */

export default function Card({ children, className = "" }) {
  return (
    <div
      className={`bg-card rounded-card shadow-card p-6 ${className}`}
    >
      {children}
    </div>
  );
}
