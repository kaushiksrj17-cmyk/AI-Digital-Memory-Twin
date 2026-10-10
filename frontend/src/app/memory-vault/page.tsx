'use client';

import React, { useState, useEffect } from 'react';
import { UploadInterface } from '@/components/UploadInterface';
import { MemoryCard } from '@/components/MemoryCard';
import { PrivacyIndicator } from '@/components/PrivacyIndicator';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { AIGeneratedBadge } from '@/components/AIGeneratedBadge';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { CardSkeleton } from '@/components/ui/Skeleton';
import {
  Memory,
  MemoryCategory,
  SourceType,
  VerificationStatus,
  PrivacyLevel,
  Evidence,
  EntityRecord,
  ExtractedEventRecord,
  ProcessingJob
} from '@/types';
import {
  Archive,
  HardDrive,
  Shield,
  FileCheck,
  Search,
  Filter,
  LayoutGrid,
  List as ListIcon,
  Plus,
  Download,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  X,
  FileText,
  Image as ImageIcon,
  Film,
  Music,
  Lock,
  Users,
  Copy,
  Calendar,
  MapPin,
  Tag,
  Share2,
  Cpu,
  Sparkles,
  HelpCircle,
  Layers,
  Activity,
  RotateCcw
} from 'lucide-react';

export default function MemoryVaultPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null);

  // Phase 3 Deep Memory Evidence State
  const [detailTab, setDetailTab] = useState<'overview' | 'evidence' | 'entities' | 'modality' | 'history'>('overview');
  const [memoryEvidence, setMemoryEvidence] = useState<Evidence[]>([]);
  const [memoryEntities, setMemoryEntities] = useState<EntityRecord[]>([]);
  const [memoryEvents, setMemoryEvents] = useState<ExtractedEventRecord[]>([]);
  const [memoryJob, setMemoryJob] = useState<ProcessingJob | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  
  // View mode: Grid vs List
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Filters and Search
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedMediaType, setSelectedMediaType] = useState<string>('ALL');
  const [selectedVerification, setSelectedVerification] = useState<string>('ALL');
  const [selectedPrivacy, setSelectedPrivacy] = useState<string>('ALL');
  const [includeArchived, setIncludeArchived] = useState(false);
  const [sortBy, setSortBy] = useState<'date' | 'title' | 'created'>('created');

  // Load memories from backend
  const fetchMemories = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (includeArchived) params.append('include_archived', 'true');
      if (searchQuery) params.append('search', searchQuery);
      if (selectedCategory !== 'ALL') params.append('category', selectedCategory);
      if (selectedVerification !== 'ALL') params.append('verification_status', selectedVerification);
      if (selectedPrivacy !== 'ALL') params.append('privacy_level', selectedPrivacy);

      const res = await fetch(`/api/v1/memories?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setMemories(data);
      } else {
        // Fallback demo state if server not connected
        setMemories([]);
      }
    } catch (err) {
      console.error('Failed to load memories:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, [includeArchived, selectedCategory, selectedVerification, selectedPrivacy]);

  // Phase 3: Fetch atomic evidence, entities, events and processing job when memory is selected
  useEffect(() => {
    if (!selectedMemory) {
      setMemoryEvidence([]);
      setMemoryEntities([]);
      setMemoryEvents([]);
      setMemoryJob(null);
      setDetailTab('overview');
      return;
    }

    const loadEvidenceAndTelemetry = async () => {
      setLoadingDetail(true);
      try {
        // 1. Evidence items
        const evRes = await fetch(`/api/v1/evidence?memory_id=${selectedMemory.id}`);
        if (evRes.ok) {
          const evData = await evRes.json();
          setMemoryEvidence(evData);
        }

        // 2. Entities
        const entRes = await fetch(`/api/v1/memories/${selectedMemory.id}/entities`);
        if (entRes.ok) {
          const entData = await entRes.json();
          setMemoryEntities(entData);
        }

        // 3. Events
        const evtRes = await fetch(`/api/v1/memories/${selectedMemory.id}/events`);
        if (evtRes.ok) {
          const evtData = await evtRes.json();
          setMemoryEvents(evtData);
        }

        // 4. Processing Job
        const mediaId = selectedMemory.storage_path?.split('/')?.pop()?.split('_')?.[0] || selectedMemory.id;
        const jobRes = await fetch(`/api/v1/processing/${mediaId}`);
        if (jobRes.ok) {
          const jobData = await jobRes.json();
          setMemoryJob(jobData);
        }
      } catch (err) {
        console.error('Failed to load memory evidence telemetry:', err);
      } finally {
        setLoadingDetail(false);
      }
    };

    loadEvidenceAndTelemetry();
  }, [selectedMemory]);

  // Handle Memory Verification
  const handleVerify = async (memoryId: string, newStatus: VerificationStatus) => {
    try {
      const res = await fetch(`/api/v1/memories/${memoryId}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ verification_status: newStatus }),
      });
      if (res.ok) {
        const updated = await res.json();
        setMemories((prev) => prev.map((m) => (m.id === memoryId ? updated : m)));
        if (selectedMemory?.id === memoryId) setSelectedMemory(updated);
      }
    } catch (err) {
      alert('Verification update failed');
    }
  };

  // Handle Archive
  const handleArchive = async (memoryId: string) => {
    try {
      const res = await fetch(`/api/v1/memories/${memoryId}/archive`, {
        method: 'POST',
      });
      if (res.ok) {
        const updated = await res.json();
        if (!includeArchived) {
          setMemories((prev) => prev.filter((m) => m.id !== memoryId));
        } else {
          setMemories((prev) => prev.map((m) => (m.id === memoryId ? updated : m)));
        }
        if (selectedMemory?.id === memoryId) setSelectedMemory(null);
      }
    } catch (err) {
      alert('Archive operation failed');
    }
  };

  // Handle Delete
  const handleDelete = async (memoryId: string) => {
    if (!confirm('Are you sure you want to delete this memory from the active vault?')) return;
    try {
      const res = await fetch(`/api/v1/memories/${memoryId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setMemories((prev) => prev.filter((m) => m.id !== memoryId));
        if (selectedMemory?.id === memoryId) setSelectedMemory(null);
      }
    } catch (err) {
      alert('Delete operation failed');
    }
  };

  // Handle Export
  const handleExport = async (memoryId: string) => {
    try {
      const res = await fetch(`/api/v1/memories/${memoryId}/export`, {
        method: 'POST',
      });
      if (res.ok) {
        const bundle = await res.json();
        const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ECHO_Memory_Export_${memoryId}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      alert('Export failed');
    }
  };

  // Filter and Search in-memory (client-side fast query)
  const filteredMemories = memories.filter((m) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch =
      !q ||
      m.title.toLowerCase().includes(q) ||
      (m.description && m.description.toLowerCase().includes(q)) ||
      (m.location && m.location.toLowerCase().includes(q)) ||
      (m.people && m.people.some((p) => p.toLowerCase().includes(q)));

    const matchesCategory = selectedCategory === 'ALL' || m.category === selectedCategory;
    const matchesVerification =
      selectedVerification === 'ALL' || m.verification_status === selectedVerification;
    const matchesPrivacy = selectedPrivacy === 'ALL' || m.privacy_level === selectedPrivacy;
    
    const matchesMediaType =
      selectedMediaType === 'ALL' ||
      (selectedMediaType === 'PHOTO' && (m.source_type === 'ORIGINAL_PHOTO' || m.source_type === 'PHOTOGRAPH')) ||
      (selectedMediaType === 'VIDEO' && (m.source_type === 'ORIGINAL_VIDEO' || m.source_type === 'VIDEO')) ||
      (selectedMediaType === 'AUDIO' && (m.source_type === 'ORIGINAL_AUDIO' || m.source_type === 'AUDIO_RECORDING')) ||
      (selectedMediaType === 'DOCUMENT' && (m.source_type === 'DOCUMENT' || m.source_type === 'LETTER' || m.source_type === 'DIARY'));

    return matchesSearch && matchesCategory && matchesVerification && matchesPrivacy && matchesMediaType;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6 animate-fadeIn">
      {/* Top Control Bar: Storage Info, Upload CTA, Archive Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Archive className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-800 dark:text-slate-100">
                Preserved Vault Storage Enclosure
              </p>
              <p className="text-[11px] text-slate-500 font-mono">
                D:\ECHO\storage\originals &bull; SHA-256 Tamper-Evident
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={includeArchived}
                onChange={(e) => setIncludeArchived(e.target.checked)}
                className="rounded text-indigo-600"
              />
              <span>Include Archived</span>
            </label>

            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs transition-colors shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Ingest Archival Media</span>
            </button>
          </div>
        </div>

        {/* Upload Drawer / Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <HardDrive className="w-5 h-5 text-indigo-400" />
                  <h3 className="font-serif text-base font-semibold text-slate-100">
                    Ingest Primary Evidence & Personal Archives
                  </h3>
                </div>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <UploadInterface
                onUploadSuccess={() => {
                  fetchMemories();
                  setShowUploadModal(false);
                }}
              />
            </div>
          </div>
        )}

        {/* Search & Filter Toolbar */}
        <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            {/* Search Input */}
            <div className="relative w-full sm:w-96">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title, description, person, or location..."
                className="w-full text-xs pl-9 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            {/* View Mode & Count */}
            <div className="flex items-center justify-between w-full sm:w-auto gap-4">
              <span className="text-xs text-slate-500 font-medium">
                {filteredMemories.length} Preserved Memories
              </span>

              <div className="flex items-center p-1 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-1.5 rounded-lg text-xs transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-white dark:bg-slate-700 text-indigo-400 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  title="Grid View"
                >
                  <LayoutGrid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-1.5 rounded-lg text-xs transition-colors ${
                    viewMode === 'list'
                      ? 'bg-white dark:bg-slate-700 text-indigo-400 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  title="List View"
                >
                  <ListIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Filter Dropdowns Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200"
            >
              <option value="ALL">All Categories</option>
              <option value="CHILDHOOD">Childhood</option>
              <option value="EDUCATION">Education</option>
              <option value="CAREER">Career</option>
              <option value="FAMILY">Family</option>
              <option value="FRIENDS">Friends</option>
              <option value="TRAVEL">Travel</option>
              <option value="HOBBIES">Hobbies</option>
              <option value="ACHIEVEMENTS">Achievements</option>
              <option value="SPECIAL_EVENTS">Special Events</option>
              <option value="PERSONAL_STORIES">Personal Stories</option>
              <option value="OTHER">Other</option>
            </select>

            {/* Media Type Filter */}
            <select
              value={selectedMediaType}
              onChange={(e) => setSelectedMediaType(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200"
            >
              <option value="ALL">All Media Types</option>
              <option value="PHOTO">Photographs</option>
              <option value="VIDEO">Videos</option>
              <option value="AUDIO">Audio Tapes</option>
              <option value="DOCUMENT">Documents & Letters</option>
            </select>

            {/* Verification Status Filter */}
            <select
              value={selectedVerification}
              onChange={(e) => setSelectedVerification(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200"
            >
              <option value="ALL">All Verification States</option>
              <option value="VERIFIED">Verified Evidence (Green)</option>
              <option value="PENDING_REVIEW">Pending Review (Amber)</option>
              <option value="REJECTED">Rejected (Red)</option>
            </select>

            {/* Privacy Tier Filter */}
            <select
              value={selectedPrivacy}
              onChange={(e) => setSelectedPrivacy(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200"
            >
              <option value="ALL">All Privacy Tiers</option>
              <option value="PRIVATE">Private Only</option>
              <option value="FAMILY">Family Circle</option>
              <option value="AUTHORIZED_USERS">Authorized Kin</option>
            </select>
          </div>
        </div>

        {/* Memories Display: Grid or List */}
        {filteredMemories.length > 0 ? (
          viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredMemories.map((m) => (
                <MemoryCard
                  key={m.id}
                  memory={m}
                  onSelect={(mem) => setSelectedMemory(mem)}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredMemories.map((m) => (
                <div
                  key={m.id}
                  onClick={() => setSelectedMemory(m)}
                  className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 hover:border-indigo-500/50 transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-slate-900 dark:text-slate-100 text-sm truncate">
                        {m.title}
                      </span>
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        {m.category}
                      </span>
                      {m.source_type === 'AI_GENERATED' && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-semibold">
                          AI-GENERATED
                        </span>
                      )}
                    </div>
                    <p className="text-slate-500 truncate">{m.description || m.narrative}</p>
                  </div>

                  <div className="flex items-center gap-4 shrink-0 text-slate-400">
                    <span>{m.date || m.approximate_date || 'Undated'}</span>
                    <ConfidenceIndicator level={m.confidence} size="sm" showText={false} />
                  </div>
                </div>
              ))}
            </div>
          )
        ) : loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="0 Preserved Memories in Vault"
            description="ECHO strictly adheres to archival provenance and does not synthesize ungrounded memories. Ingest primary photographs, letters, or audio recordings to populate your private digital vault."
            icon={Archive}
            actionLabel="Ingest First Archival Media"
            onAction={() => setShowUploadModal(true)}
          />
        )}

        {/* Detailed Memory Slide-out / Modal */}
        {selectedMemory && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-indigo-400 font-semibold">
                      {selectedMemory.category}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      ID: {selectedMemory.id}
                    </span>
                  </div>
                  <h3 className="font-serif text-lg font-semibold text-slate-100">
                    {selectedMemory.title}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedMemory(null)}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Navigation Tabs */}
              <div className="flex items-center gap-1 border-b border-slate-800 pb-2 text-xs overflow-x-auto">
                <button
                  onClick={() => setDetailTab('overview')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                    detailTab === 'overview'
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  Archival Overview
                </button>
                <button
                  onClick={() => setDetailTab('evidence')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                    detailTab === 'evidence'
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <FileCheck className="w-3.5 h-3.5" />
                  <span>Evidence ({memoryEvidence.length})</span>
                </button>
                <button
                  onClick={() => setDetailTab('entities')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                    detailTab === 'entities'
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <Users className="w-3.5 h-3.5" />
                  <span>Entities & Events ({memoryEntities.length + memoryEvents.length})</span>
                </button>
                <button
                  onClick={() => setDetailTab('history')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                    detailTab === 'history'
                      ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Processing Status</span>
                </button>
              </div>

              {/* Tab 1: Archival Overview */}
              {detailTab === 'overview' && (
                <div className="space-y-5">
                  {/* Distinction Banner: ORIGINAL PRESERVED CONTENT vs AI-GENERATED */}
                  {selectedMemory.source_type === 'AI_GENERATED' ? (
                    <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 space-y-1">
                      <div className="flex items-center gap-2 font-semibold">
                        <AIGeneratedBadge text="AI-GENERATED MEMORIAL CONTENT" />
                      </div>
                      <p className="text-[11px] text-slate-400">
                        This item is an AI-generated deduction or summary. It does not represent original words or consciousness of the deceased.
                      </p>
                    </div>
                  ) : (
                    <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
                      <span>
                        <strong>ORIGINAL PRESERVED EVIDENCE:</strong> Primary archival artifact preserved directly from family records.
                      </span>
                    </div>
                  )}

                  {/* Description / Story Narrative */}
                  <div className="space-y-1.5 text-xs">
                    <label className="font-semibold text-slate-300">Archival Narrative / Excerpt</label>
                    <p className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-200 leading-relaxed whitespace-pre-wrap">
                      {selectedMemory.description || selectedMemory.narrative}
                    </p>
                  </div>

                  {/* Spatiotemporal & Metadata Table */}
                  <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs">
                    <div>
                      <span className="text-slate-500 text-[11px]">Date Recorded:</span>
                      <p className="font-medium text-slate-200 mt-0.5">
                        {selectedMemory.date || selectedMemory.approximate_date || 'Undated'}
                      </p>
                      <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                        {selectedMemory.date ? 'USER-PROVIDED' : 'UNKNOWN'}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-500 text-[11px]">Location Anchor:</span>
                      <p className="font-medium text-slate-200 mt-0.5">
                        {selectedMemory.location || selectedMemory.location_name || 'Unspecified'}
                      </p>
                      <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                        {selectedMemory.location ? 'USER-PROVIDED' : 'UNKNOWN'}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-500 text-[11px]">People Mentioned:</span>
                      <p className="font-medium text-slate-200 mt-0.5">
                        {selectedMemory.people && selectedMemory.people.length > 0
                          ? selectedMemory.people.join(', ')
                          : 'None Tagged'}
                      </p>
                      <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                        {selectedMemory.people?.length ? 'USER-PROVIDED' : 'UNKNOWN'}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-500 text-[11px]">Privacy Level:</span>
                      <p className="font-medium text-slate-200 mt-0.5">{selectedMemory.privacy_level}</p>
                    </div>

                    <div>
                      <span className="text-slate-500 text-[11px]">Source Modality:</span>
                      <p className="font-medium text-slate-200 mt-0.5">{selectedMemory.source_type}</p>
                    </div>

                    <div>
                      <span className="text-slate-500 text-[11px]">Verification Status:</span>
                      <p className="font-medium text-slate-200 mt-0.5">{selectedMemory.verification_status}</p>
                    </div>
                  </div>

                  {/* Cryptographic Vault Storage Reference */}
                  <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-400 space-y-1">
                    <div className="flex items-center justify-between text-slate-300 font-sans font-semibold text-xs">
                      <div className="flex items-center gap-1.5">
                        <Shield className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Vault Cryptographic Fingerprint</span>
                      </div>
                      <span className="text-emerald-400 text-[10px]">Tamper-Proof</span>
                    </div>
                    <p className="truncate">
                      Storage Reference: <strong className="text-slate-200">{selectedMemory.storage_path || 'Direct Narrative Entry'}</strong>
                    </p>
                    {selectedMemory.checksum && (
                      <p className="truncate">
                        SHA-256 Digest: <strong className="text-slate-200">{selectedMemory.checksum}</strong>
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Tab 2: Extracted Evidence */}
              {detailTab === 'evidence' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Atomic Evidence Citations for Grounding:</span>
                    <span className="font-mono text-[11px]">{memoryEvidence.length} Found</span>
                  </div>

                  {memoryEvidence.length > 0 ? (
                    <div className="space-y-3">
                      {memoryEvidence.map((ev) => (
                        <div key={ev.id} className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-2 text-xs">
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-semibold text-slate-200">{ev.title}</span>
                            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-400">
                              {ev.evidence_type}
                            </span>
                          </div>

                          <p className="text-slate-400 text-[11px] leading-relaxed whitespace-pre-wrap">
                            {ev.content || 'Structured evidentiary artifact.'}
                          </p>

                          <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-[10px]">
                            <div className="flex items-center gap-2">
                              {ev.provenance_status === 'DIRECTLY_OBSERVED' && (
                                <span className="px-2 py-0.5 rounded font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                  ORIGINAL PRESERVED CONTENT
                                </span>
                              )}
                              {ev.provenance_status === 'USER_PROVIDED' && (
                                <span className="px-2 py-0.5 rounded font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                                  USER-PROVIDED
                                </span>
                              )}
                              {ev.provenance_status === 'AI_INFERRED' && (
                                <span className="px-2 py-0.5 rounded font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                                  AI-INFERRED
                                </span>
                              )}
                              {(!ev.provenance_status || ev.provenance_status === 'UNKNOWN') && (
                                <span className="px-2 py-0.5 rounded font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                                  UNKNOWN
                                </span>
                              )}
                              <span className="text-slate-500 font-mono">
                                Method: {ev.extraction_method || 'pipeline'}
                              </span>
                            </div>

                            <span className="text-slate-400 font-mono">
                              Ref: {ev.source_reference || 'Vault'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-8 text-center rounded-2xl border border-slate-800 bg-slate-950/30 text-xs text-slate-400">
                      No atomic evidence items extracted for this memory yet.
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: Entities & Events */}
              {detailTab === 'entities' && (
                <div className="space-y-5">
                  {/* Extracted Entities */}
                  <div className="space-y-2">
                    <span className="text-xs font-semibold text-slate-300 block">
                      Extracted Named Entities ({memoryEntities.length})
                    </span>
                    {memoryEntities.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {memoryEntities.map((ent) => (
                          <div key={ent.id} className="p-3 rounded-xl border border-slate-800 bg-slate-950/60 text-xs space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-slate-200">{ent.value}</span>
                              <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-800 text-indigo-400">
                                {ent.entity_type}
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-[10px] text-slate-500">
                              <span>Method: {ent.extraction_method}</span>
                              <span className="text-indigo-400 font-medium">AI-INFERRED</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/30 text-xs text-slate-500">
                        No named entities extracted yet.
                      </div>
                    )}
                  </div>

                  {/* Documented Events */}
                  <div className="space-y-2">
                    <span className="text-xs font-semibold text-slate-300 block">
                      Documented Life Milestones & Events ({memoryEvents.length})
                    </span>
                    {memoryEvents.length > 0 ? (
                      <div className="space-y-2">
                        {memoryEvents.map((evt) => (
                          <div key={evt.id} className="p-3.5 rounded-xl border border-slate-800 bg-slate-950/60 text-xs space-y-1.5">
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-slate-200">{evt.title}</span>
                              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                                {evt.event_type}
                              </span>
                            </div>
                            {evt.description && (
                              <p className="text-slate-400 text-[11px]">{evt.description}</p>
                            )}
                            <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1 border-t border-slate-800/80">
                              <span>Date: {evt.date || evt.approximate_date || 'Undated'}</span>
                              <span className="text-emerald-400 font-medium">DIRECTLY_OBSERVED</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/30 text-xs text-slate-500">
                        No life milestone events extracted yet.
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab 4: Processing Status & History */}
              {detailTab === 'history' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/70 space-y-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">Processing Orchestration Status</span>
                      {memoryJob ? (
                        <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                          memoryJob.processing_status === 'COMPLETED'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : memoryJob.processing_status === 'PROCESSING'
                            ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}>
                          {memoryJob.processing_status}
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          COMPLETED
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-[11px] pt-2 border-t border-slate-800">
                      <div>
                        <span className="text-slate-500">Processor Service:</span>
                        <p className="font-mono text-slate-200 mt-0.5">
                          {memoryJob?.processor || 'multimodal_pipeline'}
                        </p>
                      </div>

                      <div>
                        <span className="text-slate-500">Pipeline Version:</span>
                        <p className="font-mono text-slate-200 mt-0.5">
                          {memoryJob?.processing_version || 'v3.0.0'}
                        </p>
                      </div>

                      <div>
                        <span className="text-slate-500">Extraction Completed:</span>
                        <p className="font-mono text-slate-200 mt-0.5">
                          {memoryJob?.completed_at ? new Date(memoryJob.completed_at).toLocaleString() : 'Archived'}
                        </p>
                      </div>

                      <div>
                        <span className="text-slate-500">Retry Counter:</span>
                        <p className="font-mono text-slate-200 mt-0.5">
                          {memoryJob?.retry_count ?? 0}
                        </p>
                      </div>
                    </div>

                    {memoryJob?.metadata_json && (
                      <div className="pt-2 border-t border-slate-800 space-y-1">
                        <span className="text-slate-500 text-[10px] uppercase font-mono">Job Telemetry:</span>
                        <pre className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-300 overflow-x-auto">
                          {JSON.stringify(memoryJob.metadata_json, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Action Buttons: Verify, Archive, Export, Delete */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-800 text-xs">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleVerify(selectedMemory.id, 'VERIFIED')}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-medium transition-colors"
                  >
                    Verify Evidence
                  </button>
                  <button
                    onClick={() => handleVerify(selectedMemory.id, 'REJECTED')}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-rose-900/60 text-rose-400 font-medium transition-colors"
                  >
                    Reject Claim
                  </button>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleArchive(selectedMemory.id)}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition-colors flex items-center gap-1.5"
                  >
                    <Archive className="w-3.5 h-3.5" />
                    <span>Archive</span>
                  </button>

                  <button
                    onClick={() => handleExport(selectedMemory.id)}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition-colors flex items-center gap-1.5"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export</span>
                  </button>

                  <button
                    onClick={() => handleDelete(selectedMemory.id)}
                    className="px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/20 font-medium transition-colors flex items-center gap-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
    </div>
  );
}
