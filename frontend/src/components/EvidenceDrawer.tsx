'use client';

import React from 'react';
import { ResponseSource } from '@/types';
import { X, FileText, Camera, Volume2, Video, BookOpen, ShieldCheck, ExternalLink } from 'lucide-react';

interface Props {
  source: ResponseSource | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<Props> = ({ source, onClose }) => {
  if (!source) return null;

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'ORIGINAL_PHOTO':
      case 'PHOTOGRAPH':
        return <Camera className="w-4 h-4 text-emerald-400" />;
      case 'ORIGINAL_AUDIO':
      case 'AUDIO_RECORDING':
        return <Volume2 className="w-4 h-4 text-cyan-400" />;
      case 'ORIGINAL_VIDEO':
      case 'VIDEO':
        return <Video className="w-4 h-4 text-purple-400" />;
      case 'FAMILY_STORY':
        return <BookOpen className="w-4 h-4 text-amber-400" />;
      default:
        return <FileText className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-96 max-w-full bg-slate-900/95 backdrop-blur-md border-l border-slate-800 shadow-2xl z-50 flex flex-col p-6 animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          {getSourceIcon(source.source_type)}
          <h3 className="font-semibold text-sm text-slate-100 truncate">{source.source_title}</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content Body */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 text-xs">
        {/* Source Metadata Badges */}
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-mono text-[10px]">
            {source.source_type}
          </span>
          <span
            className={`px-2 py-0.5 rounded-full border text-[10px] font-mono ${
              source.confidence === 'VERIFIED'
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : source.confidence === 'SUPPORTED_INFERENCE'
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
            }`}
          >
            {source.confidence}
          </span>
          <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 text-[10px]">
            {source.provenance_status}
          </span>
        </div>

        {/* Primary Preserved vs AI Status */}
        <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/60">
          <div className="flex items-center gap-2 text-[11px] font-medium text-emerald-400 mb-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Authenticated Archival Provenance</span>
          </div>
          <p className="text-[11px] text-slate-400">
            {source.citation_label || 'Directly observed from authentic primary record in personal vault.'}
          </p>
        </div>

        {/* Excerpt Text */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">
            Preserved Evidence Text
          </label>
          <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-slate-200 leading-relaxed font-serif italic text-xs">
            &ldquo;{source.evidence_text}&rdquo;
          </div>
        </div>

        {/* IDs and Traceability */}
        <div className="space-y-2 p-3 rounded-xl bg-slate-800/30 border border-slate-800 text-[11px]">
          <div className="flex justify-between text-slate-400">
            <span>Evidence ID:</span>
            <span className="font-mono text-slate-300">{source.evidence_id || 'ev-archival-001'}</span>
          </div>
          {source.memory_id && (
            <div className="flex justify-between text-slate-400">
              <span>Memory ID:</span>
              <span className="font-mono text-slate-300">{source.memory_id}</span>
            </div>
          )}
          {source.media_id && (
            <div className="flex justify-between text-slate-400">
              <span>Media ID:</span>
              <span className="font-mono text-slate-300">{source.media_id}</span>
            </div>
          )}
          <div className="flex justify-between text-slate-400">
            <span>Storage Enclosure:</span>
            <span className="text-slate-300">Local Vault (Encrypted)</span>
          </div>
        </div>
      </div>

      {/* Footer Navigation */}
      <div className="pt-4 border-t border-slate-800 flex gap-2">
        <a
          href="/memories"
          className="flex-1 py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-center text-xs font-medium transition-colors flex items-center justify-center gap-1.5"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          <span>View Memory</span>
        </a>
        <a
          href="/evidence"
          className="flex-1 py-2 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-center text-xs font-medium transition-colors flex items-center justify-center gap-1.5"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          <span>View Evidence</span>
        </a>
      </div>
    </div>
  );
};
