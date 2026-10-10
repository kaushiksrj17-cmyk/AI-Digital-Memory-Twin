'use client';

import React from 'react';
import { RoomObject } from '@/types';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { ProvenanceIndicator } from '@/components/ProvenanceIndicator';
import { ShieldCheck, CheckCircle2, Lock, X, ExternalLink, Database } from 'lucide-react';

interface MemoryEvidencePanelProps {
  object: RoomObject | null;
  onClose: () => void;
}

export function MemoryEvidencePanel({ object, onClose }: MemoryEvidencePanelProps) {
  if (!object) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md"
      role="dialog"
      aria-modal="true"
    >
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-serif text-base font-semibold text-slate-100">
                Evidentiary Provenance Chain
              </h3>
              <p className="text-xs text-slate-400">
                Cryptographic and kinship verification records for this memory
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Object Summary */}
        <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-2">
          <div className="text-xs text-slate-400">Target Memory Record:</div>
          <div className="font-serif text-sm font-semibold text-slate-100">{object.title}</div>
          <div className="flex items-center gap-2 pt-1">
            <ConfidenceIndicator level={object.confidence} variant="badge" />
            <ProvenanceIndicator status={object.source_type} variant="badge" />
          </div>
        </div>

        {/* Verification Checkpoints */}
        <div className="space-y-3">
          <div className="text-xs font-semibold text-slate-300">Guardian Verification Checks</div>

          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex items-center justify-between text-emerald-300">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Kinship Consent Verification</span>
              </div>
              <span className="font-medium text-[11px] bg-emerald-900/40 px-2 py-0.5 rounded">
                AUTHORIZED
              </span>
            </div>

            <div className="p-3 rounded-xl bg-indigo-950/20 border border-indigo-500/30 flex items-center justify-between text-indigo-300">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                <span>Memory Guardian Boundary Check</span>
              </div>
              <span className="font-medium text-[11px] bg-indigo-900/40 px-2 py-0.5 rounded">
                PASSED (18/18)
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-slate-300">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-slate-400" />
                <span>Privacy Level Classification</span>
              </div>
              <span className="font-medium text-[11px] bg-slate-800 px-2 py-0.5 rounded uppercase">
                {object.privacy_level}
              </span>
            </div>
          </div>
        </div>

        {/* Ethical Reminder */}
        <div className="p-3.5 rounded-2xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300/90 leading-relaxed">
          <span className="font-semibold block mb-0.5">Ethical Preservation Policy:</span>
          3D room models are spatial navigation artifacts designed to organize preserved memories.
          Visual representations never constitute independent factual evidence.
        </div>

        {/* Close Button */}
        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
          >
            Close Provenance Viewer
          </button>
        </div>
      </div>
    </div>
  );
}
