'use client';

import React from 'react';
import { Box, Sparkles, Loader2 } from 'lucide-react';

interface LoadingProps {
  message?: string;
}

export function MemoryRoomLoadingState({ message = 'Preparing 3D Archival Memory Room...' }: LoadingProps) {
  return (
    <div className="w-full h-[600px] rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900 via-indigo-950/30 to-slate-950 flex flex-col items-center justify-center p-8 text-center space-y-4 shadow-2xl">
      <div className="relative">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
          <Box className="w-8 h-8 animate-pulse" />
        </div>
        <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center">
          <Loader2 className="w-3 h-3 text-white animate-spin" />
        </div>
      </div>

      <div className="space-y-1">
        <h3 className="font-serif text-lg font-semibold text-slate-100">{message}</h3>
        <p className="text-xs text-slate-400 max-w-sm">
          Grounding spatial coordinates to verified memorial vault records and initializing respectful ambient lighting.
        </p>
      </div>

      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400">
        <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
        <span>Evidence-Grounded Multimodal AI</span>
      </div>
    </div>
  );
}
