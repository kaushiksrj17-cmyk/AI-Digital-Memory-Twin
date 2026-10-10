'use client';

import React from 'react';
import { RoomObject } from '@/types';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { ProvenanceIndicator } from '@/components/ProvenanceIndicator';
import { PrivacyIndicator } from '@/components/PrivacyIndicator';
import {
  X,
  Calendar,
  MapPin,
  Users,
  ShieldCheck,
  Tag,
  Dna,
  ExternalLink,
  Volume2,
  FileText,
  Image as ImageIcon,
  Sparkles,
} from 'lucide-react';
import Link from 'next/link';

interface MemoryObjectDetailsProps {
  object: RoomObject | null;
  onClose: () => void;
  onOpenEvidenceModal?: () => void;
}

export function MemoryObjectDetails({
  object,
  onClose,
  onOpenEvidenceModal,
}: MemoryObjectDetailsProps) {
  if (!object) return null;

  return (
    <div
      className="fixed inset-y-0 right-0 w-full sm:w-[440px] bg-slate-950/95 border-l border-slate-800 shadow-2xl z-50 flex flex-col backdrop-blur-xl animate-in slide-in-from-right duration-200"
      role="dialog"
      aria-labelledby="memory-details-title"
    >
      {/* Header */}
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: object.color_accent || '#6366f1' }}
          />
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            {object.object_type.replace('_', ' ')}
          </span>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition-colors"
          aria-label="Close details panel"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Title and Confidence */}
        <div className="space-y-2">
          <h2
            id="memory-details-title"
            className="font-serif text-xl font-bold text-slate-100 leading-snug"
          >
            {object.title}
          </h2>

          <div className="flex flex-wrap items-center gap-2 pt-1">
            <ConfidenceIndicator level={object.confidence} variant="badge" />
            <ProvenanceIndicator status={object.source_type} variant="badge" />
            <PrivacyIndicator level={object.privacy_level} />
          </div>
        </div>

        {/* Media Preview if Available */}
        {object.media_url ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-inner">
            {object.object_type === 'PHOTO_FRAME' ? (
              <div className="relative aspect-video bg-slate-950 flex items-center justify-center">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={object.media_url}
                  alt={object.title}
                  className="max-h-full max-w-full object-contain"
                  onError={(e) => {
                    // Fallback to placeholder box on failure
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />
              </div>
            ) : object.object_type === 'AUDIO_STATION' ? (
              <div className="p-4 space-y-3">
                <div className="flex items-center gap-2 text-cyan-400 text-xs font-medium">
                  <Volume2 className="w-4 h-4 animate-pulse" />
                  <span>Authorized Archival Audio Tape</span>
                </div>
                <audio controls className="w-full h-8" src={object.media_url}>
                  Your browser does not support audio playback.
                </audio>
              </div>
            ) : (
              <div className="p-4 flex items-center gap-3">
                <FileText className="w-6 h-6 text-amber-400" />
                <div className="text-xs">
                  <div className="font-semibold text-slate-200">Preserved Document</div>
                  <a
                    href={object.media_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-indigo-400 hover:underline flex items-center gap-1 mt-0.5"
                  >
                    <span>Download authorized copy</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            )}
          </div>
        ) : null}

        {/* Description / Archival Narrative */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-medium">Archival Description</span>
            <span className="text-[10px] text-emerald-400 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" />
              Evidence Grounded
            </span>
          </div>
          <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 text-xs text-slate-200 leading-relaxed whitespace-pre-line">
            {object.description || 'No detailed narrative recorded for this archive object.'}
          </div>
        </div>

        {/* Temporal & Spatial Provenance */}
        <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
          <div className="text-xs font-semibold text-slate-300">Preserved Metadata</div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <span className="text-[11px] text-slate-500 block">Date / Era</span>
              <span className="text-slate-200 flex items-center gap-1 mt-0.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                {object.date || 'Unknown'}
              </span>
            </div>
            <div>
              <span className="text-[11px] text-slate-500 block">Location</span>
              <span className="text-slate-200 flex items-center gap-1 mt-0.5">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                {object.location || 'Unknown'}
              </span>
            </div>
          </div>

          {object.people && object.people.length > 0 && (
            <div className="pt-2 border-t border-slate-800/60">
              <span className="text-[11px] text-slate-500 block mb-1">Associated People</span>
              <div className="flex flex-wrap gap-1.5">
                {object.people.map((p, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded-md bg-slate-800 text-[11px] text-slate-300 flex items-center gap-1"
                  >
                    <Users className="w-3 h-3 text-slate-400" />
                    {p}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Associated Memory DNA */}
        {object.associated_dna_keys && object.associated_dna_keys.length > 0 && (
          <div className="space-y-2">
            <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Dna className="w-3.5 h-3.5 text-indigo-400" />
              <span>Grounded Memory DNA Markers</span>
            </span>
            <div className="flex flex-wrap gap-1.5">
              {object.associated_dna_keys.map((key, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-lg bg-indigo-950/40 border border-indigo-500/30 text-[11px] text-indigo-300 flex items-center gap-1"
                >
                  <Tag className="w-3 h-3" />
                  {key}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Navigation */}
      <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between gap-3">
        {onOpenEvidenceModal && (
          <button
            onClick={onOpenEvidenceModal}
            className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-medium text-slate-300 transition-colors"
          >
            Inspect Provenance
          </button>
        )}

        {object.memory_id && (
          <Link
            href={`/memories`}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white flex items-center gap-1.5 shadow-lg shadow-indigo-600/20 transition-colors ml-auto"
          >
            <span>View in Memory Vault</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        )}
      </div>
    </div>
  );
}
