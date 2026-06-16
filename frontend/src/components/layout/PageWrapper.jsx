/**
 * PageWrapper — main layout shell for authenticated pages.
 *
 * Sidebar on the left (desktop), main content on the right.
 * Includes the mobile navbar with hamburger menu.
 */

import { useState } from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

export default function PageWrapper({ children, title }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile navbar */}
        <Navbar onMenuToggle={() => setSidebarOpen((prev) => !prev)} />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto px-4 py-6 lg:px-8 lg:py-8">
          {title && (
            <h1 className="text-2xl lg:text-3xl font-bold text-text-main mb-6">
              {title}
            </h1>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
