import React from 'react';
import { Sparkles } from 'lucide-react';

interface Props {
  minimal?: boolean;
  label?: string;
  text?: string;
}

export const AIGeneratedBadge: React.FC<Props> = ({ minimal = false, label, text }) => {
  const displayText = label || text || (minimal ? 'AI Representation' : 'AI Memorial Twin • Evidence-Grounded Representation');

  if (minimal) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
        <Sparkles className="w-3 h-3" />
        {displayText}
      </span>
    );
  }

  return (
    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20">
      <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
      <span>{displayText}</span>
    </div>
  );
};
