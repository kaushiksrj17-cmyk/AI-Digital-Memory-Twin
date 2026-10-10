import React from 'react';
import { Memory } from '@/types';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { ProvenanceIndicator } from '@/components/ProvenanceIndicator';
import { AIGeneratedBadge } from '@/components/AIGeneratedBadge';
import {
  Calendar,
  MapPin,
  Tag,
  Lock,
  Users,
  ShieldCheck,
  FileCheck,
  AlertCircle,
  HelpCircle,
  Image as ImageIcon,
  Film,
  Music,
  FileText
} from 'lucide-react';

interface Props {
  memory: Memory;
  onSelect?: (memory: Memory) => void;
}

export const MemoryCard: React.FC<Props> = ({ memory, onSelect }) => {
  const isAIGenerated = memory.source_type === 'AI_GENERATED';

  const renderMediaIcon = () => {
    switch (memory.source_type) {
      case 'ORIGINAL_PHOTO':
      case 'PHOTOGRAPH':
        return <ImageIcon className="w-3.5 h-3.5 text-indigo-400" />;
      case 'ORIGINAL_VIDEO':
      case 'VIDEO':
        return <Film className="w-3.5 h-3.5 text-purple-400" />;
      case 'ORIGINAL_AUDIO':
      case 'AUDIO_RECORDING':
        return <Music className="w-3.5 h-3.5 text-cyan-400" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-amber-400" />;
    }
  };

  const renderVerificationBadge = () => {
    switch (memory.verification_status) {
      case 'VERIFIED':
      case 'VERIFIED_BY_DOCUMENT':
      case 'VERIFIED_BY_FAMILY':
        return (
          <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
            <FileCheck className="w-3 h-3" />
            <span>Verified Evidence</span>
          </span>
        );
      case 'REJECTED':
      case 'DISPUTED':
        return (
          <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 font-medium">
            <AlertCircle className="w-3 h-3" />
            <span>Rejected</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium">
            <HelpCircle className="w-3 h-3" />
            <span>Pending Review</span>
          </span>
        );
    }
  };

  const renderPrivacyBadge = () => {
    if (memory.privacy_level === 'PRIVATE') {
      return (
        <span className="flex items-center gap-1 text-[10px] text-slate-400">
          <Lock className="w-3 h-3 text-slate-500" />
          <span>Private</span>
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 text-[10px] text-indigo-400">
        <Users className="w-3 h-3 text-indigo-400" />
        <span>{memory.privacy_level}</span>
      </span>
    );
  };

  return (
    <div
      onClick={() => onSelect && onSelect(memory)}
      className={`p-5 rounded-2xl border transition-all cursor-pointer group bg-white dark:bg-slate-900/60 shadow-sm ${
        isAIGenerated
          ? 'border-indigo-500/30 hover:border-indigo-500'
          : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
      }`}
    >
      {/* Header Badges */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
        <div className="flex items-center gap-2">
          {renderVerificationBadge()}
          <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-semibold">
            {memory.category || 'OTHER'}
          </span>
          {renderPrivacyBadge()}
        </div>
        <ConfidenceIndicator level={memory.confidence} score={memory.confidence_score} size="sm" />
      </div>

      {/* AI Distinction Banner */}
      {isAIGenerated && (
        <div className="mb-2">
          <AIGeneratedBadge text="AI-Generated Representation — Preserved Evidence Required" />
        </div>
      )}

      {/* Title */}
      <h3 className="font-serif font-semibold text-slate-900 dark:text-slate-100 group-hover:text-indigo-400 transition-colors text-base mb-1.5 flex items-center gap-2">
        {renderMediaIcon()}
        <span>{memory.title}</span>
      </h3>

      {/* Narrative / Description */}
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-4 line-clamp-2">
        {memory.description || memory.narrative}
      </p>

      {/* Metadata Anchors */}
      <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800/60 pt-3">
        {(memory.date || memory.approximate_date) && (
          <div className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>{memory.date || memory.approximate_date}</span>
          </div>
        )}
        {(memory.location || memory.location_name) && (
          <div className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <span>{memory.location || memory.location_name}</span>
          </div>
        )}
        {memory.people && memory.people.length > 0 && (
          <div className="flex items-center gap-1">
            <Users className="w-3.5 h-3.5 text-slate-400" />
            <span>{memory.people.join(', ')}</span>
          </div>
        )}
        <div className="flex items-center gap-1 ml-auto">
          <Tag className="w-3 h-3 text-slate-400" />
          <span className="font-mono text-[10px]">{memory.source_type.replace('_', ' ')}</span>
        </div>
      </div>

      {/* Provenance Citations */}
      {memory.provenance_records && memory.provenance_records.length > 0 && (
        <div className="mt-2.5">
          <ProvenanceIndicator citations={memory.provenance_records} />
        </div>
      )}
    </div>
  );
};
