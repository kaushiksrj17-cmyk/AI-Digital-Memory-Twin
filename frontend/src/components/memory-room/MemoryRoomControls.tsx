'use client';

import React from 'react';
import { RoomTheme, MemoryCategory } from '@/types';
import {
  RotateCcw,
  Sun,
  LayoutGrid,
  Box,
  Sparkles,
  Sliders,
  Filter,
  Eye,
  Activity,
  Volume2,
  VolumeX,
} from 'lucide-react';

interface MemoryRoomControlsProps {
  theme: RoomTheme;
  onThemeChange: (theme: RoomTheme) => void;
  ambientLight: number;
  onAmbientLightChange: (light: number) => void;
  onResetCamera: () => void;
  is3DView: boolean;
  onToggleView: () => void;
  avatarEnabled: boolean;
  onToggleAvatar: () => void;
  onOpenAvatarSettings: () => void;
  reducedMotion: boolean;
  onToggleReducedMotion: () => void;
  selectedCategory: string;
  onCategoryChange: (cat: string) => void;
  audioEnabled: boolean;
  onToggleAudio: () => void;
}

export function MemoryRoomControls({
  theme,
  onThemeChange,
  ambientLight,
  onAmbientLightChange,
  onResetCamera,
  is3DView,
  onToggleView,
  avatarEnabled,
  onToggleAvatar,
  onOpenAvatarSettings,
  reducedMotion,
  onToggleReducedMotion,
  selectedCategory,
  onCategoryChange,
  audioEnabled,
  onToggleAudio,
}: MemoryRoomControlsProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800 backdrop-blur-md shadow-xl text-xs text-slate-300">
      {/* Left: View Mode Toggle and Camera Reset */}
      <div className="flex items-center gap-2">
        <button
          onClick={onToggleView}
          className={`px-3 py-1.5 rounded-xl border flex items-center gap-1.5 transition-all ${
            is3DView
              ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-600/20'
              : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'
          }`}
          title="Toggle between 3D Spatial Room and 2D Accessible List"
        >
          {is3DView ? <Box className="w-3.5 h-3.5" /> : <LayoutGrid className="w-3.5 h-3.5" />}
          <span>{is3DView ? '3D Room' : 'Accessible List'}</span>
        </button>

        {is3DView && (
          <button
            onClick={onResetCamera}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 flex items-center gap-1.5 transition-colors"
            title="Reset 3D Camera Position"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset View</span>
          </button>
        )}
      </div>

      {/* Center: Category Filter & Room Theme */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={selectedCategory}
            onChange={(e) => onCategoryChange(e.target.value)}
            className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
            aria-label="Filter memories in 3D room"
          >
            <option value="ALL">All Memory Categories</option>
            <option value="FAMILY">Family</option>
            <option value="CAREER">Career</option>
            <option value="CHILDHOOD">Childhood</option>
            <option value="EDUCATION">Education</option>
            <option value="TRAVEL">Travel</option>
            <option value="PERSONAL_STORY">Personal Story</option>
            <option value="ACHIEVEMENT">Achievement</option>
          </select>
        </div>

        {is3DView && (
          <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1">
            <Sliders className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={theme}
              onChange={(e) => onThemeChange(e.target.value as RoomTheme)}
              className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
              aria-label="Select room aesthetic theme"
            >
              <option value="ARCHIVAL_WARM">Archival Warm</option>
              <option value="STUDY_CLASSIC">Study Classic</option>
              <option value="GALLERY_MODERN">Gallery Modern</option>
              <option value="MINIMAL_SERENE">Minimal Serene</option>
            </select>
          </div>
        )}
      </div>

      {/* Right: Lighting, Audio, Avatar and Accessibility Toggles */}
      <div className="flex items-center gap-2">
        {is3DView && (
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-xl">
            <Sun className="w-3.5 h-3.5 text-amber-400" />
            <input
              type="range"
              min="0.4"
              max="1.6"
              step="0.1"
              value={ambientLight}
              onChange={(e) => onAmbientLightChange(parseFloat(e.target.value))}
              className="w-16 h-1 accent-indigo-500 cursor-pointer"
              title="Adjust Room Ambient Light"
            />
          </div>
        )}

        <button
          onClick={onToggleAudio}
          className={`p-1.5 rounded-xl border transition-colors ${
            audioEnabled
              ? 'bg-slate-800 border-slate-700 text-cyan-400'
              : 'bg-slate-950 border-slate-800 text-slate-500'
          }`}
          title={audioEnabled ? 'Mute Room Ambient Sound' : 'Enable Room Ambient Sound'}
        >
          {audioEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
        </button>

        <button
          onClick={onToggleReducedMotion}
          className={`px-2.5 py-1.5 rounded-xl border text-[11px] font-medium flex items-center gap-1 transition-colors ${
            reducedMotion
              ? 'bg-indigo-950/60 border-indigo-500/80 text-indigo-300'
              : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-300'
          }`}
          title="Toggle Reduced Motion"
        >
          <Activity className="w-3 h-3" />
          <span className="hidden lg:inline">{reducedMotion ? 'Reduced Motion' : 'Motion'}</span>
        </button>

        {/* Avatar Settings & Toggle */}
        <div className="flex items-center gap-1 bg-slate-950 border border-slate-800 rounded-xl p-0.5">
          <button
            onClick={onToggleAvatar}
            className={`px-2 py-1 rounded-lg text-[11px] font-medium flex items-center gap-1 transition-colors ${
              avatarEnabled
                ? 'bg-purple-950/60 text-purple-300 font-semibold'
                : 'text-slate-500 hover:text-slate-400'
            }`}
            title="Toggle Memorial Avatar Presence"
          >
            <Sparkles className="w-3 h-3 text-purple-400" />
            <span>Avatar</span>
          </button>
          <button
            onClick={onOpenAvatarSettings}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            title="Configure Memorial Avatar Settings"
          >
            <Sliders className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
}
