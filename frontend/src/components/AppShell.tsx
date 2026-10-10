'use client';

import React, { useState } from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from '@/components/Sidebar';
import { Topbar } from '@/components/Topbar';
import { EthicalBanner } from '@/components/EthicalBanner';
import { PublicNavbar } from '@/components/PublicNavbar';
import { PublicFooter } from '@/components/PublicFooter';
import { ThemeProvider } from '@/context/ThemeContext';
import { ToastProvider } from '@/context/ToastContext';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const pathname = usePathname();
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // Determine if current route is a public marketing/auth route
  const isPublicRoute = pathname === '/' || pathname === '/login';

  return (
    <ThemeProvider>
      <ToastProvider>
        {isPublicRoute ? (
          // Public Marketing / Auth Layout
          <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
            <PublicNavbar />
            <EthicalBanner variant="topbar" />
            <main className="flex-1">{children}</main>
            <PublicFooter />
          </div>
        ) : (
          // Authenticated Workspace Layout
          <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
            <Sidebar
              isMobileOpen={isMobileNavOpen}
              onMobileClose={() => setIsMobileNavOpen(false)}
              isCollapsed={isSidebarCollapsed}
              onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            />

            <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
              <EthicalBanner variant="topbar" />
              <Topbar onMobileMenuToggle={() => setIsMobileNavOpen(true)} />
              <main className="flex-1 pb-16">{children}</main>
            </div>
          </div>
        )}
      </ToastProvider>
    </ThemeProvider>
  );
};
