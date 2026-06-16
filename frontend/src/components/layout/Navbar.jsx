/**
 * Mobile navbar — hamburger menu + centered logo.
 *
 * Visible on mobile only (hidden on lg+ screens).
 */

export default function Navbar({ onMenuToggle }) {
  return (
    <header className="lg:hidden sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-border px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Hamburger */}
        <button
          onClick={onMenuToggle}
          className="p-2 rounded-button text-text-muted hover:text-text-main hover:bg-gray-100 transition-colors cursor-pointer"
          aria-label="Toggle menu"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>

        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
          </div>
          <span className="text-base font-bold text-text-main">FitPlan</span>
        </div>

        {/* Spacer for centering */}
        <div className="w-10" />
      </div>
    </header>
  );
}
