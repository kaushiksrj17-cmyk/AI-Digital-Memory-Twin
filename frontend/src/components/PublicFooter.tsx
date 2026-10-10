'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles, ShieldCheck, Heart, HardDrive, ExternalLink } from 'lucide-react';
import { AIGeneratedBadge } from './AIGeneratedBadge';

export const PublicFooter: React.FC = () => {
  return (
    <footer className="border-t border-slate-200/80 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-950 text-slate-600 dark:text-slate-400 py-12 px-4 sm:px-6 lg:px-8 transition-colors">
      <div className="max-w-7xl mx-auto space-y-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Col 1: Brand & Tagline */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <span className="font-serif text-lg font-bold text-slate-900 dark:text-white">ECHO</span>
              <AIGeneratedBadge minimal />
            </div>
            <p className="font-serif italic text-xs text-slate-500 dark:text-slate-400">
              “Preserve the memories. Hear the voice. See the presence. Keep the story alive.”
            </p>
            <p className="text-[11px] leading-relaxed text-slate-500">
              Evidence-grounded digital memory twin, engineered for sovereign personal archival on{' '}
              <span className="font-mono text-indigo-500 dark:text-indigo-400">D:\ECHO</span>.
            </p>
          </div>

          {/* Col 2: Core Sanctuary */}
          <div className="space-y-2 text-xs">
            <h4 className="font-semibold text-slate-900 dark:text-slate-200">Memorial Sanctuary</h4>
            <ul className="space-y-1.5">
              <li>
                <Link href="/dashboard" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  Command Dashboard
                </Link>
              </li>
              <li>
                <Link href="/memory-vault" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  Archival Vault
                </Link>
              </li>
              <li>
                <Link href="/timeline" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  Life Narrative Timeline
                </Link>
              </li>
              <li>
                <Link href="/memory-room" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  3D Spatial Memory Room
                </Link>
              </li>
              <li>
                <Link href="/conversation" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  AI Dialogue Companion
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Ethics & Security */}
          <div className="space-y-2 text-xs">
            <h4 className="font-semibold text-slate-900 dark:text-slate-200">Ethics & Governance</h4>
            <ul className="space-y-1.5">
              <li>
                <Link href="/security" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  Memory Guardian & Privacy
                </Link>
              </li>
              <li>
                <Link href="/voice" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  Kinship Voice Consent
                </Link>
              </li>
              <li>
                <Link href="/family" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  Multi-Stakeholder Circle
                </Link>
              </li>
              <li>
                <Link href="/research-dashboard" className="hover:text-indigo-600 dark:hover:text-indigo-400">
                  Integrity Audit Ledger
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 4: Sovereign Storage */}
          <div className="space-y-3 text-xs">
            <h4 className="font-semibold text-slate-900 dark:text-slate-200">Sovereign Privacy</h4>
            <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[11px] space-y-1.5 shadow-sm">
              <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-mono text-[10px]">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>Local Offline Confinement</span>
              </div>
              <p className="text-slate-500 dark:text-slate-400 text-[10px]">
                All photos, voice tapes, and diary vectors remain sealed on your local volume. Non-deceptive AI.
              </p>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-200 dark:border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
          <p>© 2026 ECHO Research Project. Evidence-Grounded Digital Memory Preservation.</p>
          <div className="flex items-center gap-4">
            <Link href="/research" className="hover:text-indigo-600 dark:hover:text-indigo-400">
              Ethical Manifesto
            </Link>
            <span>&bull;</span>
            <Link href="/security" className="hover:text-indigo-600 dark:hover:text-indigo-400">
              Privacy Ledger
            </Link>
            <span>&bull;</span>
            <span className="font-mono text-indigo-500 dark:text-indigo-400">v1.0.0-phase1.foundation</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
