'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Archive,
  BookOpen,
  Calendar,
  Box,
  MessageSquare,
  Mic,
  Users,
  Network,
  FileCheck,
  Shield,
  Settings,
  GraduationCap,
  Sparkles,
  Heart,
  Cpu,
  Dna,
  Share2,
  Search,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  HardDrive,
  User,
  X
} from 'lucide-react';
import { AIGeneratedBadge } from './AIGeneratedBadge';

interface SidebarProps {
  isMobileOpen?: boolean;
  onMobileClose?: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isMobileOpen = false,
  onMobileClose = () => {},
  isCollapsed = false,
  onToggleCollapse = () => {},
}) => {
  const pathname = usePathname();

  const navGroups = [
    {
      group: 'Core Hub',
      items: [
        { label: 'Overview Dashboard', href: '/dashboard', icon: LayoutDashboard },
        { label: 'Memory Vault', href: '/memory-vault', icon: Archive },
        { label: 'Preserved Memories', href: '/memories', icon: BookOpen },
        { label: 'Evidence & Provenance', href: '/evidence', icon: FileCheck },
      ],
    },
    {
      group: 'Narrative & Intelligence',
      items: [
        { label: 'Life Timeline', href: '/timeline', icon: Calendar },
        { label: 'Memory DNA', href: '/memory-dna', icon: Dna },
        { label: 'Knowledge Graph', href: '/knowledge-graph', icon: Share2 },
        { label: 'People & Loved Ones', href: '/people', icon: Users },
        { label: 'Kinship Relationships', href: '/relationships', icon: Network },
      ],
    },
    {
      group: 'Interactive Presence',
      items: [
        { label: 'AI Memory Companion', href: '/conversation', icon: MessageSquare },
        { label: 'Voice Preservation Studio', href: '/voice', icon: Mic },
        { label: '3D Spatial Memory Room', href: '/memory-room', icon: Box },
        { label: 'Multimodal Processing', href: '/processing', icon: Cpu },
      ],
    },
    {
      group: 'Governance & Science',
      items: [
        { label: 'Family Space', href: '/family', icon: Heart },
        { label: 'Security & Privacy', href: '/security', icon: Shield },
        { label: 'Research Dashboard', href: '/research-dashboard', icon: BarChart3 },
        { label: 'Scientific Framework', href: '/research', icon: GraduationCap },
        { label: 'Settings', href: '/settings', icon: Settings },
      ],
    },
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-900 dark:bg-slate-950 text-slate-300 border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          {!isCollapsed && (
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="font-serif text-base font-bold tracking-wide text-white">ECHO</h1>
                <AIGeneratedBadge minimal />
              </div>
              <p className="text-[10px] text-slate-400 font-sans tracking-tight truncate">
                AI Digital Memory Twin
              </p>
            </div>
          )}
        </Link>

        {/* Mobile Close Button */}
        <button
          onClick={onMobileClose}
          className="md:hidden text-slate-400 hover:text-white p-1 rounded-lg"
          aria-label="Close navigation"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-5 custom-scrollbar">
        {navGroups.map((group) => (
          <div key={group.group} className="space-y-1">
            {!isCollapsed && (
              <h4 className="px-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                {group.group}
              </h4>
            )}
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onMobileClose}
                  title={isCollapsed ? item.label : undefined}
                  className={`flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all group ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                  } ${isCollapsed ? 'justify-center px-2' : ''}`}
                >
                  <Icon
                    className={`w-4 h-4 shrink-0 transition-transform group-hover:scale-110 ${
                      isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-200'
                    }`}
                  />
                  {!isCollapsed && <span className="truncate">{item.label}</span>}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer Storage Badge & Collapse Toggle */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/40 text-[11px] text-slate-500 space-y-2">
        {!isCollapsed && (
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-1.5 text-emerald-400 font-mono text-[10px]">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Storage: D:\ECHO</span>
            </div>
            <span className="text-[10px] text-slate-500">USB Sealed</span>
          </div>
        )}

        {/* Desktop Collapse Toggle */}
        <button
          onClick={onToggleCollapse}
          className="hidden md:flex w-full items-center justify-center gap-2 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 transition-colors text-[11px]"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4" />
              <span>Collapse Sidebar</span>
            </>
          )}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sticky Sidebar */}
      <aside
        className={`hidden md:block h-screen sticky top-0 shrink-0 transition-all duration-200 z-30 ${
          isCollapsed ? 'w-16' : 'w-64'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 md:hidden animate-in fade-in"
          onClick={onMobileClose}
        />
      )}

      {/* Mobile Slide-out Drawer */}
      <div
        className={`fixed inset-y-0 left-0 w-72 z-50 md:hidden transform transition-transform duration-200 ease-in-out ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </div>
    </>
  );
};
