import React from 'react';
import { ProvenanceRecord, SourceType } from '@/types';
import { BookOpen, FileText, Music, Image as ImageIcon, Film } from 'lucide-react';

interface Props {
  citations?: ProvenanceRecord[];
  status?: SourceType | string;
  variant?: string;
}

export const ProvenanceIndicator: React.FC<Props> = ({ citations, status, variant }) => {
  if (status) {
    const renderIcon = () => {
      switch (status) {
        case 'PHOTOGRAPH':
        case 'PHOTO':
        case 'ORIGINAL_PHOTO':
          return <ImageIcon className="w-3.5 h-3.5 text-blue-400" />;
        case 'AUDIO_RECORDING':
        case 'AUDIO':
        case 'ORIGINAL_AUDIO':
          return <Music className="w-3.5 h-3.5 text-cyan-400" />;
        case 'VIDEO':
        case 'ORIGINAL_VIDEO':
          return <Film className="w-3.5 h-3.5 text-purple-400" />;
        default:
          return <FileText className="w-3.5 h-3.5 text-amber-400" />;
      }
    };

    return (
      <span
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-slate-800/80 border-slate-700/60 text-slate-300"
        title={`Preserved Primary Source: ${status}`}
      >
        {renderIcon()}
        <span>{status.replace(/_/g, ' ')}</span>
      </span>
    );
  }

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-200/80 dark:border-slate-800/80">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
        <BookOpen className="w-3.5 h-3.5 text-indigo-500" />
        <span>Based on preserved evidence</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {citations.map((c, idx) => (
          <div
            key={idx}
            className="flex items-start gap-2 bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 rounded-md p-2 text-xs text-slate-600 dark:text-slate-300 max-w-md"
          >
            {c.source_type === 'PHOTOGRAPH' ? (
              <ImageIcon className="w-3.5 h-3.5 mt-0.5 text-blue-500 shrink-0" />
            ) : c.source_type === 'AUDIO_RECORDING' ? (
              <Music className="w-3.5 h-3.5 mt-0.5 text-emerald-500 shrink-0" />
            ) : (
              <FileText className="w-3.5 h-3.5 mt-0.5 text-amber-500 shrink-0" />
            )}
            <div>
              <div className="font-medium text-slate-900 dark:text-slate-100">
                {c.source_title}
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">
                {c.source_reference} &bull; {c.evidence_text}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
