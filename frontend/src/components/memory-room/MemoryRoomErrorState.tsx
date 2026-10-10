'use client';

import React from 'react';
import { AlertCircle, RotateCcw, ListFilter } from 'lucide-react';

interface ErrorProps {
  error: string;
  onRetry: () => void;
  onSwitchToList?: () => void;
}

export function MemoryRoomErrorState({ error, onRetry, onSwitchToList }: ErrorProps) {
  return (
    <div className="w-full h-[600px] rounded-3xl border border-red-900/30 bg-gradient-to-b from-slate-900 via-red-950/20 to-slate-950 flex flex-col items-center justify-center p-8 text-center space-y-5 shadow-2xl">
      <div className="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
        <AlertCircle className="w-7 h-7" />
      </div>

      <div className="space-y-1.5 max-w-md">
        <h3 className="font-serif text-lg font-semibold text-slate-100">
          Unable to Initialize 3D Memory Room
        </h3>
        <p className="text-xs text-slate-400">
          {error || 'An unexpected error occurred while loading spatial memory records.'}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onRetry}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Retry 3D Scene</span>
        </button>

        {onSwitchToList && (
          <button
            onClick={onSwitchToList}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-slate-200 flex items-center gap-2 transition-colors"
          >
            <ListFilter className="w-3.5 h-3.5 text-slate-400" />
            <span>Open Accessible 2D List</span>
          </button>
        )}
      </div>
    </div>
  );
}
