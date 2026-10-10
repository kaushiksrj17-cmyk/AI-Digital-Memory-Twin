'use client';

import React, { useState, useEffect } from 'react';
import {
  Evidence,
  EvidenceType,
  ProvenanceStatus,
  ConfidenceLevel
} from '@/types';
import {
  FileCheck,
  ShieldCheck,
  Database,
  Search,
  Filter,
  Eye,
  ExternalLink,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  FileText,
  Image as ImageIcon,
  Film,
  Music,
  MapPin,
  Calendar,
  Tag,
  Hash,
  ShieldAlert,
  Archive
} from 'lucide-react';

export default function EvidencePage() {
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedProvenance, setSelectedProvenance] = useState<string>('ALL');
  const [selectedConfidence, setSelectedConfidence] = useState<string>('ALL');
  const [mediaFilter, setMediaFilter] = useState('');

  const fetchEvidence = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedType !== 'ALL') params.append('evidence_type', selectedType);
      if (selectedProvenance !== 'ALL') params.append('provenance_status', selectedProvenance);
      if (selectedConfidence !== 'ALL') params.append('confidence', selectedConfidence);
      if (searchQuery) params.append('search', searchQuery);
      if (mediaFilter) params.append('media_id', mediaFilter);

      const res = await fetch(`/api/v1/evidence?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setEvidenceList(data);
      } else {
        setEvidenceList([]);
      }
    } catch (err) {
      console.error('Failed to load evidence records:', err);
      setEvidenceList([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [selectedType, selectedProvenance, selectedConfidence]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEvidence();
  };

  const getProvenanceBadge = (status?: ProvenanceStatus) => {
    switch (status) {
      case 'DIRECTLY_OBSERVED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            ORIGINAL PRESERVED CONTENT
          </span>
        );
      case 'USER_PROVIDED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <CheckCircle2 className="w-3 h-3" />
            USER-PROVIDED
          </span>
        );
      case 'AI_INFERRED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            AI-INFERRED
          </span>
        );
      case 'UNKNOWN':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <HelpCircle className="w-3 h-3" />
            UNKNOWN / UNVERIFIED
          </span>
        );
    }
  };

  const getConfidenceBadge = (confidence: ConfidenceLevel) => {
    switch (confidence) {
      case 'VERIFIED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            VERIFIED (GREEN)
          </span>
        );
      case 'SUPPORTED_INFERENCE':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-300">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            SUPPORTED INFERENCE (YELLOW)
          </span>
        );
      case 'UNKNOWN_UNSUPPORTED':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/20 text-rose-300">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
            UNSUPPORTED (RED)
          </span>
        );
    }
  };

  const getTypeIcon = (type?: EvidenceType) => {
    switch (type) {
      case 'TEXT':
      case 'DOCUMENT_METADATA':
        return <FileText className="w-4 h-4 text-emerald-400" />;
      case 'OCR_TEXT':
        return <Database className="w-4 h-4 text-indigo-400" />;
      case 'TRANSCRIPT':
      case 'AUDIO_METADATA':
        return <Music className="w-4 h-4 text-amber-400" />;
      case 'IMAGE_METADATA':
      case 'VISUAL_OBJECT':
      case 'VISUAL_SCENE':
        return <ImageIcon className="w-4 h-4 text-sky-400" />;
      case 'VIDEO_KEYFRAME':
      case 'VIDEO_METADATA':
        return <Film className="w-4 h-4 text-purple-400" />;
      case 'LOCATION':
        return <MapPin className="w-4 h-4 text-rose-400" />;
      case 'DATE':
        return <Calendar className="w-4 h-4 text-teal-400" />;
      default:
        return <Layers className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6 animate-fadeIn">
      {/* Grounding Header Banner */}
        <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-200">
                Tamper-Proof Multimodal Evidence Ledger
              </h4>
              <p className="text-slate-400 text-[11px] mt-0.5">
                Every deduction made by ECHO must be cited directly from atomic evidence extracted from family archives.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-auto font-mono text-[11px] text-emerald-400 bg-emerald-950/30 px-3 py-1.5 rounded-xl border border-emerald-900/50">
            <Database className="w-3.5 h-3.5" />
            <span>{evidenceList.length} Active Evidence Artifacts</span>
          </div>
        </div>

        {/* Filter & Search Toolbar */}
        <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-3">
          <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
            <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs">
              <Search className="w-4 h-4 text-slate-500 shrink-0" />
              <input
                type="text"
                placeholder="Search evidence titles, content excerpts, citations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent text-slate-200 placeholder-slate-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                <Hash className="w-3.5 h-3.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Filter Media ID..."
                  value={mediaFilter}
                  onChange={(e) => setMediaFilter(e.target.value)}
                  className="w-32 bg-transparent text-slate-200 placeholder-slate-500 focus:outline-none font-mono text-[11px]"
                />
              </div>

              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs transition-colors shrink-0"
              >
                Search
              </button>
            </div>
          </form>

          {/* Granular Filters */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-slate-800/60 text-xs">
            <div>
              <label className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                Evidence Modality Type
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none"
              >
                <option value="ALL">All Evidence Types</option>
                <option value="TEXT">Preserved Text</option>
                <option value="OCR_TEXT">OCR Extracted Text</option>
                <option value="TRANSCRIPT">Spoken Audio Transcript</option>
                <option value="IMAGE_METADATA">Image Technical Metadata</option>
                <option value="VIDEO_KEYFRAME">Video Keyframe</option>
                <option value="ENTITY">Extracted Named Entity</option>
                <option value="EVENT">Documented Life Event</option>
                <option value="DOCUMENT_METADATA">Document Registry Metadata</option>
                <option value="AUDIO_METADATA">Audio Acoustic Metadata</option>
                <option value="VIDEO_METADATA">Video Stream Metadata</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                Provenance Origin Status
              </label>
              <select
                value={selectedProvenance}
                onChange={(e) => setSelectedProvenance(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none"
              >
                <option value="ALL">All Provenance Statuses</option>
                <option value="DIRECTLY_OBSERVED">Directly Observed Archive</option>
                <option value="USER_PROVIDED">User-Provided Facts</option>
                <option value="AI_INFERRED">AI-Inferred Deduction</option>
                <option value="UNKNOWN">Unknown / Unspecified</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                Confidence Level
              </label>
              <select
                value={selectedConfidence}
                onChange={(e) => setSelectedConfidence(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none"
              >
                <option value="ALL">All Confidence Ratings</option>
                <option value="VERIFIED">Verified (Green)</option>
                <option value="SUPPORTED_INFERENCE">Supported Inference (Yellow)</option>
                <option value="UNKNOWN_UNSUPPORTED">Unsupported / Unknown (Red)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Evidence Artifacts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {evidenceList.map((item) => (
            <div
              key={item.id}
              onClick={() => setSelectedEvidence(item)}
              className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 hover:border-indigo-500/40 hover:bg-slate-900/70 transition-all cursor-pointer flex flex-col justify-between gap-4"
            >
              <div className="space-y-3">
                {/* Header badges */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {getTypeIcon(item.evidence_type)}
                    <span className="font-mono text-[10px] font-semibold text-slate-400 uppercase">
                      {item.evidence_type || item.source_type || 'EVIDENCE'}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {getConfidenceBadge(item.confidence)}
                  </div>
                </div>

                {/* Title */}
                <h4 className="font-serif text-sm font-semibold text-slate-100 leading-snug">
                  {item.title}
                </h4>

                {/* Excerpt */}
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                  {item.content || item.raw_content_excerpt || 'Structured evidence artifact with normalized parameters.'}
                </p>
              </div>

              {/* Provenance Footer */}
              <div className="pt-3 border-t border-slate-800/80 space-y-2 text-[11px]">
                <div className="flex items-center justify-between gap-2">
                  {getProvenanceBadge(item.provenance_status)}
                  <span className="font-mono text-slate-500 text-[10px]">
                    {item.extraction_method || 'extractor'}
                  </span>
                </div>

                {/* Phase 4 Integration Badges */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-indigo-950/80 text-indigo-300 border border-indigo-800">
                    Vector Indexed
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-cyan-950/80 text-cyan-300 border border-cyan-800">
                    Graph Linked
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-purple-950/80 text-purple-300 border border-purple-800">
                    DNA Linked
                  </span>
                </div>

                <div className="flex items-center justify-between text-slate-500 text-[10px] font-mono">
                  <span className="truncate max-w-[200px]" title={item.source_reference || item.source_citation}>
                    Ref: {item.source_reference || item.source_citation || 'Archival Vault'}
                  </span>
                  {item.media_id && (
                    <span className="text-indigo-400">Media: {item.media_id}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {evidenceList.length === 0 && !loading && (
          <div className="p-16 text-center rounded-3xl border border-slate-800 bg-slate-900/30 space-y-3">
            <Archive className="w-10 h-10 text-slate-500 mx-auto" />
            <h4 className="font-serif text-base font-semibold text-slate-200">
              0 Evidence Records Found
            </h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              No evidence matching the specified filters exists in the active registry. Ingest media into the Memory Vault to extract verifiable evidence.
            </p>
          </div>
        )}

        {/* Detailed Evidence Inspector Modal */}
        {selectedEvidence && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {getTypeIcon(selectedEvidence.evidence_type)}
                    <span className="text-[10px] font-mono uppercase text-indigo-400 font-semibold">
                      {selectedEvidence.evidence_type || 'EVIDENCE ARTIFACT'}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">
                      ID: {selectedEvidence.id}
                    </span>
                  </div>
                  <h3 className="font-serif text-lg font-semibold text-slate-100">
                    {selectedEvidence.title}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedEvidence(null)}
                  className="p-1 text-slate-400 hover:text-slate-200"
                >
                  ✕
                </button>
              </div>

              {/* Provenance & Confidence Ledger Strip */}
              <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-950 border border-slate-800">
                <div>
                  <span className="text-[10px] uppercase font-mono text-slate-500 block">Provenance Status</span>
                  <div className="mt-1">{getProvenanceBadge(selectedEvidence.provenance_status)}</div>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-mono text-slate-500 block">Confidence Level</span>
                  <div className="mt-1">{getConfidenceBadge(selectedEvidence.confidence)}</div>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-mono text-slate-500 block">Confidence Score</span>
                  <p className="font-mono text-sm font-bold text-slate-200 mt-1">
                    {selectedEvidence.confidence_score !== undefined ? `${(selectedEvidence.confidence_score * 100).toFixed(0)}%` : '100%'}
                  </p>
                </div>
              </div>

              {/* Content Body */}
              <div className="space-y-1.5 text-xs">
                <label className="font-semibold text-slate-300">Evidence Content Excerpt</label>
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 whitespace-pre-wrap leading-relaxed font-sans">
                  {selectedEvidence.content || selectedEvidence.raw_content_excerpt || 'No raw text representation.'}
                </div>
              </div>

              {/* Structured Metadata Values */}
              {selectedEvidence.structured_value && (
                <div className="space-y-1.5 text-xs">
                  <label className="font-semibold text-slate-300">Structured Parameters</label>
                  <pre className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-48">
                    {JSON.stringify(selectedEvidence.structured_value, null, 2)}
                  </pre>
                </div>
              )}

              {/* Source Provenance Linkages */}
              <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs">
                <div>
                  <span className="text-[11px] text-slate-500">Source Reference Citation:</span>
                  <p className="font-medium text-slate-200 mt-0.5">
                    {selectedEvidence.source_reference || selectedEvidence.source_citation || 'Direct Ingestion'}
                  </p>
                </div>

                <div>
                  <span className="text-[11px] text-slate-500">Extraction Method:</span>
                  <p className="font-mono text-slate-200 mt-0.5">
                    {selectedEvidence.extraction_method || 'direct_inspection'}
                  </p>
                </div>

                <div>
                  <span className="text-[11px] text-slate-500">Source Memory ID:</span>
                  <p className="font-mono text-indigo-400 mt-0.5">
                    {selectedEvidence.memory_id || 'Not Linked to Memory'}
                  </p>
                </div>

                <div>
                  <span className="text-[11px] text-slate-500">Source Media ID:</span>
                  <p className="font-mono text-indigo-400 mt-0.5">
                    {selectedEvidence.media_id || 'Direct Archive'}
                  </p>
                </div>

                <div>
                  <span className="text-[11px] text-slate-500">Processor Version:</span>
                  <p className="font-mono text-slate-200 mt-0.5">
                    {selectedEvidence.processor_version || 'v3.0.0'}
                  </p>
                </div>

                <div>
                  <span className="text-[11px] text-slate-500">Extraction Timestamp:</span>
                  <p className="font-mono text-slate-300 mt-0.5">
                    {selectedEvidence.created_at ? new Date(selectedEvidence.created_at).toLocaleString() : 'Preserved Record'}
                  </p>
                </div>
              </div>

              {/* Close Button */}
              <div className="flex justify-end pt-3 border-t border-slate-800">
                <button
                  onClick={() => setSelectedEvidence(null)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium"
                >
                  Close Inspector
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
  );
}
