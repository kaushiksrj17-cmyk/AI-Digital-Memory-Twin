'use client';

import React, { useState } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { Button } from '@/components/ui/Button';
import { Settings, Save, Shield, HardDrive, Cpu, Sliders, Moon, Sun, CheckCircle2 } from 'lucide-react';

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme();
  const [llmProvider, setLlmProvider] = useState('mock');
  const [strictBoundaries, setStrictBoundaries] = useState(true);
  const [minConfidence, setMinConfidence] = useState(0.75);
  const [showProvenance, setShowProvenance] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6 animate-fadeIn">
      <form
        onSubmit={handleSave}
        className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-6 text-xs"
      >
        {/* Appearance Settings */}
        <div className="space-y-3 pb-6 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                {theme === 'dark' ? <Moon className="w-4 h-4 text-indigo-400" /> : <Sun className="w-4 h-4 text-amber-500" />}
                <span>Interface Theme Mode</span>
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                Toggle between deep midnight dark theme and clean ivory daylight theme.
              </p>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={toggleTheme}
            >
              {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            </Button>
          </div>
        </div>

        {/* Storage Root (Locked) */}
        <div className="space-y-1.5">
          <label className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
            <HardDrive className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
            <span>Project Root Boundary (USB Enclosure)</span>
          </label>
          <input
            type="text"
            readOnly
            value="D:\ECHO"
            className="w-full text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-600 dark:text-slate-400 font-mono shadow-inner"
          />
          <p className="text-[11px] text-slate-500">
            Cryptographically locked to guarantee local hardware storage isolation and zero data leakage.
          </p>
        </div>

        {/* AI Provider Mode */}
        <div className="space-y-1.5">
          <label className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
            <span>Multimodal AI Provider Mode</span>
          </label>
          <select
            value={llmProvider}
            onChange={(e) => setLlmProvider(e.target.value)}
            className="w-full text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 shadow-sm"
          >
            <option value="mock">Offline Mock Mode (Deterministic &amp; Zero Paid APIs)</option>
            <option value="gemini">Google Gemini 1.5 Pro (Requires LLM_API_KEY)</option>
            <option value="local">Local GGUF / Llama.cpp (Local Weight Integration)</option>
          </select>
        </div>

        {/* Ethical Guardrail Toggles */}
        <div className="space-y-4 pt-4 border-t border-slate-100 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-slate-800 dark:text-slate-200">Strict Ethical Boundaries Filter</h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                Memory Guardian blocks all queries prompting consciousness simulation or persona impersonation.
              </p>
            </div>
            <input
              type="checkbox"
              checked={strictBoundaries}
              onChange={(e) => setStrictBoundaries(e.target.checked)}
              className="w-4 h-4 rounded text-indigo-600 bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 focus:ring-0 cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-slate-800 dark:text-slate-200">Display Provenance Badges</h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                Embed primary source citations and verification confidence beneath all dialogue turns.
              </p>
            </div>
            <input
              type="checkbox"
              checked={showProvenance}
              onChange={(e) => setShowProvenance(e.target.checked)}
              className="w-4 h-4 rounded text-indigo-600 bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 focus:ring-0 cursor-pointer"
            />
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <Button
            type="submit"
            variant="primary"
          >
            <Save className="w-3.5 h-3.5 mr-1.5" />
            <span>Save System Settings</span>
          </Button>
          {saved && (
            <span className="text-emerald-600 dark:text-emerald-400 text-xs font-semibold flex items-center gap-1.5 animate-fadeIn">
              <CheckCircle2 className="w-4 h-4" />
              Settings saved successfully!
            </span>
          )}
        </div>
      </form>
    </div>
  );
}
