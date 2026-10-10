'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Search,
  LayoutDashboard,
  Archive,
  Calendar,
  Box,
  MessageSquare,
  Mic,
  Dna,
  Share2,
  Users,
  Shield,
  Settings,
  Sparkles,
  ArrowRight,
  BookOpen,
  FileCheck,
  X
} from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<Props> = ({ isOpen, onClose }) => {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const navigationCommands = [
    { label: 'Memorial Dashboard', path: '/dashboard', icon: LayoutDashboard, category: 'Navigation' },
    { label: 'Memory Vault', path: '/memory-vault', icon: Archive, category: 'Navigation' },
    { label: 'Preserved Memories', path: '/memories', icon: BookOpen, category: 'Navigation' },
    { label: 'Evidence & Provenance', path: '/evidence', icon: FileCheck, category: 'Navigation' },
    { label: 'Life Timeline', path: '/timeline', icon: Calendar, category: 'Navigation' },
    { label: '3D Memory Room', path: '/memory-room', icon: Box, category: 'Navigation' },
    { label: 'Interactive AI Dialogue', path: '/conversation', icon: MessageSquare, category: 'Navigation' },
    { label: 'Voice Preservation Studio', path: '/voice', icon: Mic, category: 'Navigation' },
    { label: 'Memory DNA', path: '/memory-dna', icon: Dna, category: 'Navigation' },
    { label: 'Knowledge Graph', path: '/knowledge-graph', icon: Share2, category: 'Navigation' },
    { label: 'Family Collaboration Space', path: '/family', icon: Users, category: 'Navigation' },
    { label: 'Security & Privacy Controls', path: '/security', icon: Shield, category: 'Navigation' },
    { label: 'Settings', path: '/settings', icon: Settings, category: 'Navigation' },
  ];

  const memoryCommands = [
    { label: 'Graduation Day at Trinity College (1968)', path: '/memories', icon: BookOpen, category: 'Archival Memory' },
    { label: 'Summer Sailing on Lake Windermere (1974)', path: '/memories', icon: BookOpen, category: 'Archival Memory' },
    { label: 'University Degree Registry Record 1968', path: '/evidence', icon: FileCheck, category: 'Evidence Document' },
    { label: 'Family Oral History Tape (Side A)', path: '/voice', icon: Mic, category: 'Audio Archive' },
  ];

  const allItems = [...navigationCommands, ...memoryCommands];

  const filtered = allItems.filter(
    (item) =>
      item.label.toLowerCase().includes(query.toLowerCase()) ||
      item.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          // Open triggered outside
        }
      }
      if (!isOpen) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev < filtered.length - 1 ? prev + 1 : 0));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : filtered.length - 1));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filtered[selectedIndex]) {
          router.push(filtered[selectedIndex].path);
          onClose();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filtered, router, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-xl rounded-2xl border border-slate-700/80 bg-slate-900/95 dark:bg-slate-900/95 text-slate-100 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Search Input Bar */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-slate-800">
          <Search className="w-4 h-4 text-slate-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Search memories, evidence, timeline, or jump to route..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none"
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="text-slate-400 hover:text-slate-200 text-xs"
            >
              Clear
            </button>
          )}
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700 rounded">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              No matching memories or routes found for <span className="text-white font-medium">&ldquo;{query}&rdquo;</span>
            </div>
          ) : (
            filtered.map((item, idx) => {
              const Icon = item.icon;
              const isSelected = idx === selectedIndex;
              return (
                <div
                  key={`${item.path}-${item.label}-${idx}`}
                  onClick={() => {
                    router.push(item.path);
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer text-xs transition-colors ${
                    isSelected
                      ? 'bg-indigo-600/25 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-300 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                        isSelected
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="truncate">
                      <p className="font-medium text-slate-200">{item.label}</p>
                      <p className="text-[10px] text-slate-500">{item.category}</p>
                    </div>
                  </div>
                  <ArrowRight
                    className={`w-3.5 h-3.5 shrink-0 ${
                      isSelected ? 'text-indigo-400' : 'text-slate-600'
                    }`}
                  />
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-4 py-2.5 border-t border-slate-800/80 bg-slate-950/60 flex items-center justify-between text-[11px] text-slate-500">
          <div className="flex items-center gap-3">
            <span>
              <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px]">↑</kbd>{' '}
              <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px]">↓</kbd> Navigate
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px]">↵</kbd> Select
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-indigo-400 font-mono text-[10px]">
            <Sparkles className="w-3 h-3" />
            <span>ECHO Grounded Search</span>
          </div>
        </div>
      </div>
    </div>
  );
};
