'use client';

import React from 'react';
import { RoomObject } from '@/types';
import { Calendar, ChevronRight, Clock, Star } from 'lucide-react';

interface MemoryTimelinePanelProps {
  objects: RoomObject[];
  selectedObject: RoomObject | null;
  onSelectObject: (obj: RoomObject) => void;
}

export function MemoryTimelinePanel({
  objects,
  selectedObject,
  onSelectObject,
}: MemoryTimelinePanelProps) {
  // Sort objects by date string when available
  const timelineObjects = objects
    .filter((o) => o.date || o.object_type === 'TIMELINE_WALL')
    .sort((a, b) => {
      const dateA = a.date || '';
      const dateB = b.date || '';
      return dateA.localeCompare(dateB);
    });

  if (timelineObjects.length === 0) return null;

  return (
    <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 backdrop-blur-md space-y-3">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-slate-300 font-semibold">
          <Calendar className="w-4 h-4 text-indigo-400" />
          <span>Chronological Archival Milestones</span>
        </div>
        <span className="text-[11px] text-slate-500">
          {timelineObjects.length} dated markers
        </span>
      </div>

      {/* Horizontal Scrollable Timeline */}
      <div className="flex items-center gap-3 overflow-x-auto pb-2 pt-1 scrollbar-thin scrollbar-thumb-slate-800">
        {timelineObjects.map((item, idx) => {
          const isSelected = selectedObject?.object_id === item.object_id;
          return (
            <button
              key={item.object_id}
              onClick={() => onSelectObject(item)}
              className={`shrink-0 px-3.5 py-2 rounded-xl border text-left transition-all ${
                isSelected
                  ? 'bg-indigo-600 border-indigo-400 text-white shadow-lg shadow-indigo-600/30 scale-105'
                  : 'bg-slate-950/80 hover:bg-slate-800/80 border-slate-800 text-slate-300'
              }`}
            >
              <div className="flex items-center gap-1.5 text-[10px] font-semibold opacity-80 mb-0.5">
                <Clock className="w-3 h-3" />
                <span>{item.date || 'Era Milestone'}</span>
              </div>
              <div className="text-xs font-serif font-medium line-clamp-1 max-w-[140px]">
                {item.title}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
