'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Menu,
  Search,
  Plus,
  Sun,
  Moon,
  Bell,
  User,
  ShieldCheck,
  ChevronDown,
  Lock,
  LogOut,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { AIGeneratedBadge } from '@/components/AIGeneratedBadge';
import { useTheme } from '@/context/ThemeContext';
import { CommandPalette } from '@/components/CommandPalette';
import { QuickAddModal } from '@/components/QuickAddModal';

interface Props {
  title?: string;
  subtitle?: string;
  onMobileMenuToggle?: () => void;
}

const routeTitles: Record<string, { title: string; subtitle: string; category: string }> = {
  '/dashboard': {
    title: 'Memorial Command Dashboard',
    subtitle: 'Curated evidence-grounded overview of preserved biographical archives',
    category: 'Core Hub',
  },
  '/memory-vault': {
    title: 'Cryptographic Memory Vault',
    subtitle: 'Sovereign multimodal archive with cryptographic SHA-256 integrity digests',
    category: 'Core Hub',
  },
  '/memories': {
    title: 'Preserved Memory Units',
    subtitle: 'Structured memories indexed with tri-state confidence and provenance',
    category: 'Core Hub',
  },
  '/evidence': {
    title: 'Evidence & Provenance Explorer',
    subtitle: 'Archival sources, verified citations, and cryptographic file records',
    category: 'Core Hub',
  },
  '/processing': {
    title: 'Multimodal Ingestion Pipeline',
    subtitle: 'Real-time processing jobs for photos, documents, and oral histories',
    category: 'Interactive Presence',
  },
  '/conversation': {
    title: 'AI Memory Companion',
    subtitle: 'Evidence-grounded dialogue guarded by Memory Guardian against confabulation',
    category: 'Interactive Presence',
  },
  '/voice': {
    title: 'Voice Preservation Studio',
    subtitle: 'Consent-governed speech synthesis with immutable audio watermarking',
    category: 'Interactive Presence',
  },
  '/memory-room': {
    title: '3D Spatial Memory Room',
    subtitle: 'Three.js immersive reflection sanctuary with ambient memorial exhibits',
    category: 'Interactive Presence',
  },
  '/timeline': {
    title: 'Life Narrative Timeline',
    subtitle: 'Chronological progression preserving exact dates and evidentiary conflicts',
    category: 'Narrative & Intelligence',
  },
  '/relationships': {
    title: 'Kinship & Social Relationships',
    subtitle: 'Family tree and social connections with evidentiary edge verification',
    category: 'Narrative & Intelligence',
  },
  '/people': {
    title: 'Biographical Directory',
    subtitle: 'Preserved identities and loved ones linked to archival memories',
    category: 'Narrative & Intelligence',
  },
  '/knowledge-graph': {
    title: 'Semantic Knowledge Graph',
    subtitle: 'Interactive entity and event topology preserving conflicting claims',
    category: 'Narrative & Intelligence',
  },
  '/memory-dna': {
    title: 'Memory DNA Profiler',
    subtitle: 'Core traits, value systems, and thematic patterns extracted from evidence',
    category: 'Narrative & Intelligence',
  },
  '/family': {
    title: 'Family Collaboration Circle',
    subtitle: 'Multi-stakeholder workspace with role-based permissions and governance',
    category: 'Governance & Science',
  },
  '/family/contributions': {
    title: 'Family Contribution Review',
    subtitle: 'Community submission queue with mandatory owner verification',
    category: 'Governance & Science',
  },
  '/security': {
    title: 'Security & Privacy Center',
    subtitle: 'Ethical guardrail monitors, kinship consent ledgers, and audit logs',
    category: 'Governance & Science',
  },
  '/research': {
    title: 'Scientific Research Framework',
    subtitle: 'Methodology, ethical guidelines, and non-deceptive memory modeling',
    category: 'Governance & Science',
  },
  '/research-dashboard': {
    title: 'Research & Integrity Dashboard',
    subtitle: 'Empirical benchmark metrics, boundary scores, and contradiction audits',
    category: 'Governance & Science',
  },
  '/retrieval': {
    title: 'Hybrid Retrieval Diagnostics',
    subtitle: 'Vector embeddings and keyword search scores with ranking explanations',
    category: 'Core Hub',
  },
  '/settings': {
    title: 'Sanctuary Settings',
    subtitle: 'Manage local storage, appearance, privacy boundaries, and vault profile',
    category: 'Governance & Science',
  },
};

export const Topbar: React.FC<Props> = ({ title, subtitle, onMobileMenuToggle }) => {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isQuickAddOpen, setIsQuickAddOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);

  const routeMeta = routeTitles[pathname] || {
    title: 'Memorial Sanctuary',
    subtitle: 'Evidence-grounded digital memory twin',
    category: 'Workspace',
  };

  const displayTitle = title || routeMeta.title;
  const displaySubtitle = subtitle || routeMeta.subtitle;

  return (
    <>
      <header className="h-16 border-b border-slate-200 dark:border-slate-800/80 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20 transition-colors">
        {/* Left: Mobile hamburger & Titles */}
        <div className="flex items-center gap-3 min-w-0">
          {onMobileMenuToggle && (
            <button
              onClick={onMobileMenuToggle}
              className="md:hidden p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle mobile menu"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}

          <div className="min-w-0">
            <div className="flex items-center gap-2.5">
              <h2 className="text-sm sm:text-base font-semibold text-slate-900 dark:text-slate-100 truncate">
                {title || 'Memorial Sanctuary'}
              </h2>
              <div className="hidden sm:block">
                <AIGeneratedBadge minimal />
              </div>
            </div>
            {subtitle && (
              <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate hidden sm:block">
                {subtitle}
              </p>
            )}
          </div>
        </div>

        {/* Center: Global Search Trigger Button */}
        <div className="hidden lg:flex items-center flex-1 max-w-sm mx-6">
          <button
            onClick={() => setIsSearchOpen(true)}
            className="w-full flex items-center justify-between px-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 text-slate-400 hover:border-indigo-500/40 text-xs transition-colors shadow-inner"
          >
            <div className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <span>Search memories, evidence, people...</span>
            </div>
            <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-[10px] font-mono border border-slate-300 dark:border-slate-700">
              Ctrl+K
            </kbd>
          </button>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          {/* Mobile search trigger */}
          <button
            onClick={() => setIsSearchOpen(true)}
            className="lg:hidden p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Search"
            aria-label="Open global search"
          >
            <Search className="w-4 h-4" />
          </button>

          {/* Quick Add Memory Action */}
          <button
            onClick={() => setIsQuickAddOpen(true)}
            className="flex items-center gap-1.5 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl shadow-sm shadow-indigo-600/30 transition-all"
            title="Preserve a new memory in the vault"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Preserve Memory</span>
          </button>

          {/* Subject Badge */}
          <div className="hidden xl:flex items-center gap-2 bg-slate-100 dark:bg-slate-800/80 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-700/60 text-[11px] text-slate-600 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Vault: <strong>Eleanor Vance</strong> (Archival)</span>
          </div>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={theme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          {/* Notifications Popover */}
          <div className="relative">
            <button
              onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative"
              title="Recent audit events"
              aria-label="Notifications"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500" />
            </button>

            {isNotificationsOpen && (
              <div
                className="absolute right-0 mt-2 w-80 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl p-4 text-xs space-y-3 z-50 animate-in fade-in"
                onMouseLeave={() => setIsNotificationsOpen(false)}
              >
                <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                  <h4 className="font-semibold text-slate-900 dark:text-slate-100">Audit & Security Ledger</h4>
                  <span className="text-[10px] text-indigo-500 font-mono">Live Logs</span>
                </div>
                <div className="space-y-2 text-[11px]">
                  <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-0.5">
                    <p className="font-medium text-slate-800 dark:text-slate-200">Evidence Record Grounded</p>
                    <p className="text-slate-500 text-[10px]">Cambridge degree folio verified with SHA-256 digest</p>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-0.5">
                    <p className="font-medium text-slate-800 dark:text-slate-200">Memory Guardian Active</p>
                    <p className="text-slate-500 text-[10px]">18 boundary filters enforcing zero confabulation</p>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-0.5">
                    <p className="font-medium text-slate-800 dark:text-slate-200">Kinship Consent Ledger</p>
                    <p className="text-slate-500 text-[10px]">Memorial voice synthesis restricted to authorized kin</p>
                  </div>
                </div>
                <Link
                  href="/security"
                  onClick={() => setIsNotificationsOpen(false)}
                  className="block text-center text-[11px] text-indigo-600 dark:text-indigo-400 font-medium hover:underline pt-1"
                >
                  View Complete Audit Ledger &rarr;
                </Link>
              </div>
            )}
          </div>

          {/* User Profile Menu */}
          <div className="relative">
            <button
              onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
              className="flex items-center gap-2 pl-2 pr-2.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
              aria-label="User profile menu"
            >
              <div className="w-6 h-6 rounded-lg bg-indigo-600/20 text-indigo-500 dark:text-indigo-400 flex items-center justify-center font-bold text-xs">
                G
              </div>
              <span className="text-xs font-medium text-slate-700 dark:text-slate-300 hidden sm:inline">
                Guardian
              </span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {isProfileMenuOpen && (
              <div
                className="absolute right-0 mt-2 w-56 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl p-2 text-xs space-y-1 z-50 animate-in fade-in"
                onMouseLeave={() => setIsProfileMenuOpen(false)}
              >
                <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800 mb-1">
                  <p className="font-semibold text-slate-800 dark:text-slate-200">Memorial Guardian</p>
                  <p className="text-[10px] text-slate-500">guardian@echo-memorial.org</p>
                  <span className="inline-block mt-1 text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 font-mono font-medium">
                    ROLE: VAULT_OWNER
                  </span>
                </div>

                <Link
                  href="/dashboard"
                  onClick={() => setIsProfileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  <User className="w-3.5 h-3.5" />
                  <span>Dashboard</span>
                </Link>

                <Link
                  href="/settings"
                  onClick={() => setIsProfileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  <Lock className="w-3.5 h-3.5" />
                  <span>Vault Settings</span>
                </Link>

                <Link
                  href="/security"
                  onClick={() => setIsProfileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Security & Consent</span>
                </Link>

                <div className="pt-1 border-t border-slate-100 dark:border-slate-800 mt-1">
                  <Link
                    href="/login"
                    onClick={() => setIsProfileMenuOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Global Command Palette */}
      <CommandPalette isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />

      {/* Quick Add Memory Modal */}
      <QuickAddModal isOpen={isQuickAddOpen} onClose={() => setIsQuickAddOpen(false)} />
    </>
  );
};
