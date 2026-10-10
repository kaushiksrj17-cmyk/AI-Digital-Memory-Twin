'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles, Sun, Moon, ArrowRight, ShieldCheck, Lock } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';
import { AIGeneratedBadge } from './AIGeneratedBadge';

export const PublicNavbar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-serif text-lg font-bold tracking-tight text-slate-900 dark:text-white">
                ECHO
              </span>
              <AIGeneratedBadge minimal />
            </div>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 font-sans tracking-tight hidden sm:block">
              AI Digital Memory Twin
            </p>
          </div>
        </Link>

        {/* Center Nav */}
        <nav className="hidden md:flex items-center gap-6 text-xs font-medium text-slate-600 dark:text-slate-300">
          <Link href="/#features" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            Preservation Vault
          </Link>
          <Link href="/#ethics" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            Ethical Manifesto
          </Link>
          <Link href="/#how-it-works" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            How It Works
          </Link>
          <Link href="/#faq" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            FAQ
          </Link>
          <Link href="/research" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            Research Lab
          </Link>
        </nav>

        {/* Right CTA */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
            title={theme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
            aria-label="Toggle visual theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          <Link
            href="/login"
            className="flex items-center gap-1.5 text-xs font-medium text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
          >
            <Lock className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </Link>

          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl shadow-sm shadow-indigo-600/30 transition-all"
          >
            <span>Open Sanctuary</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </header>
  );
};
