import React from 'react';
import { Evidence } from '@/types';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { FileCheck, BookOpen, ExternalLink, ShieldCheck } from 'lucide-react';

interface Props {
  evidenceList: Evidence[];
}

export const EvidencePanel: React.FC<Props> = ({ evidenceList }) => {
  return (
    <div className="space-y-4">
      {evidenceList.map((e) => (
        <div
          key={e.id}
          className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm"
        >
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-emerald-500 shrink-0" />
              <h4 className="font-serif font-semibold text-slate-900 dark:text-slate-100 text-sm">
                {e.title}
              </h4>
            </div>
            <ConfidenceIndicator level={e.confidence} size="sm" />
          </div>

          <div className="bg-slate-50 dark:bg-slate-800/60 rounded-lg p-3 text-xs text-slate-700 dark:text-slate-200 font-mono leading-relaxed border border-slate-200/60 dark:border-slate-700/60 my-3">
            “{e.raw_content_excerpt}”
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-800/60">
            <div className="flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
              <span>Citation: <strong>{e.source_citation}</strong></span>
            </div>
            <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-medium text-slate-400">
              {e.verification_status}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
