import React from 'react';
import { LifeEvent } from '@/types';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { Calendar, MapPin, Milestone } from 'lucide-react';

interface Props {
  events: LifeEvent[];
}

export const TimelineComponent: React.FC<Props> = ({ events }) => {
  return (
    <div className="relative border-l-2 border-indigo-500/20 dark:border-indigo-500/30 ml-4 space-y-8 py-2">
      {events.map((e, idx) => (
        <div key={e.id || idx} className="relative pl-6 group">
          {/* Timeline Dot */}
          <div className="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-white dark:bg-slate-900 border-2 border-indigo-500 group-hover:scale-125 transition-transform" />

          {/* Event Card */}
          <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between gap-3 mb-1.5">
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                {e.event_category}
              </span>
              <ConfidenceIndicator level={e.confidence} size="sm" />
            </div>

            <h4 className="font-serif font-semibold text-slate-900 dark:text-slate-100 text-sm">
              {e.title}
            </h4>

            {e.narrative && (
              <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
                {e.narrative}
              </p>
            )}

            <div className="mt-3 flex items-center gap-4 text-[11px] text-slate-500 border-t border-slate-100 dark:border-slate-800/60 pt-2">
              <div className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>{e.date_description || e.event_date}</span>
              </div>
              {e.location_name && (
                <div className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  <span>{e.location_name}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
