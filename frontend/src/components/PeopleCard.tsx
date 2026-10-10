import React from 'react';
import { Person } from '@/types';
import { User, Heart, Shield } from 'lucide-react';

interface Props {
  person: Person;
}

export const PeopleCard: React.FC<Props> = ({ person }) => {
  return (
    <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-500 font-serif font-bold text-sm shrink-0">
          {person.full_name.charAt(0)}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between">
            <h4 className="font-serif font-semibold text-xs text-slate-900 dark:text-slate-100 truncate">
              {person.full_name}
            </h4>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-medium">
              {person.relationship_to_subject}
            </span>
          </div>
          {person.nickname && (
            <p className="text-[11px] text-slate-500">“{person.nickname}”</p>
          )}
          {person.biographical_note && (
            <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 line-clamp-2">
              {person.biographical_note}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
