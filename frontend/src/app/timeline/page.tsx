'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Calendar,
  Clock,
  MapPin,
  Users,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
  Search,
  Filter,
  ArrowUpDown,
  Plus,
  Box,
  FileText,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Eye,
  ChevronDown,
  Layers,
  History,
  RotateCcw
} from 'lucide-react';
import {
  TimelineEvent,
  TimelineResponse,
  DatePrecision,
  ConfidenceLevel,
  VerificationStatus,
  SourceType
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function TimelinePage() {
  const [timelineData, setTimelineData] = useState<TimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters state
  const [category, setCategory] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sourceType, setSourceType] = useState<string>('');
  const [reverseChronological, setReverseChronological] = useState<boolean>(false);
  const [includeAiSuggested, setIncludeAiSuggested] = useState<boolean>(true);
  const [disputedOnly, setDisputedOnly] = useState<boolean>(false);

  // Modals & Drawers state
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showDisputeModal, setShowDisputeModal] = useState<boolean>(false);
  const [disputeEventTarget, setDisputeEventTarget] = useState<TimelineEvent | null>(null);
  const [disputeReason, setDisputeReason] = useState<string>('');
  const [competingDate, setCompetingDate] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isGeneratingAi, setIsGeneratingAi] = useState<boolean>(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  // New Event Form State
  const [newEventTitle, setNewEventTitle] = useState('');
  const [newEventDesc, setNewEventDesc] = useState('');
  const [newEventCategory, setNewEventCategory] = useState('Childhood');
  const [newEventDate, setNewEventDate] = useState('1970-01-01');
  const [newEventPrecision, setNewEventPrecision] = useState<DatePrecision>('EXACT');
  const [newEventLocation, setNewEventLocation] = useState('');
  const [newEventPeople, setNewEventPeople] = useState('');

  const fetchTimeline = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('memorial_profile_id', 'demo-profile-001');
      if (category) params.append('category', category);
      if (searchQuery) params.append('search_query', searchQuery);
      if (sourceType) params.append('source_type', sourceType);
      params.append('reverse_chronological', reverseChronological.toString());
      params.append('include_ai_suggested', includeAiSuggested.toString());
      if (disputedOnly) params.append('verification_status', 'DISPUTED');

      const res = await fetch(`${API_BASE}/timeline/?${params.toString()}`);
      if (!res.ok) {
        throw new Error(`Failed to load timeline: ${res.statusText}`);
      }
      const data: TimelineResponse = await res.json();
      setTimelineData(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error communicating with backend timeline service');
    } finally {
      setLoading(false);
    }
  }, [category, searchQuery, sourceType, reverseChronological, includeAiSuggested, disputedOnly]);

  useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline]);

  // AI Suggestion Handler
  const handleGenerateAiSuggestions = async () => {
    setIsGeneratingAi(true);
    setFeedbackMessage(null);
    try {
      const res = await fetch(`${API_BASE}/timeline/suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          memorial_profile_id: 'demo-profile-001',
          max_suggestions: 3
        })
      });
      if (!res.ok) throw new Error('Failed to generate suggestions');
      const suggestions = await res.json();
      setFeedbackMessage(`Generated ${suggestions.length} candidate timeline event(s) validated by Memory Guardian.`);
      await fetchTimeline();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsGeneratingAi(false);
    }
  };

  // Event Verification Handler
  const handleVerifyEvent = async (eventId: string, newStatus: VerificationStatus) => {
    try {
      const res = await fetch(`${API_BASE}/timeline/${eventId}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-role': 'FAMILY_ADMIN'
        },
        body: JSON.stringify({
          verification_status: newStatus,
          verification_notes: 'Reviewed and certified against primary archival evidence.'
        })
      });
      if (!res.ok) throw new Error('Verification failed');
      setFeedbackMessage(`Event status updated to ${newStatus}.`);
      await fetchTimeline();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Submit Dispute Handler
  const handleSubmitDispute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!disputeEventTarget) return;
    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/timeline/${disputeEventTarget.id}/dispute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dispute_reason: disputeReason,
          competing_date: competingDate || undefined,
          notes: 'Submitted via Family Portal.'
        })
      });
      if (!res.ok) throw new Error('Dispute submission failed');
      setShowDisputeModal(false);
      setDisputeReason('');
      setCompetingDate('');
      setDisputeEventTarget(null);
      setFeedbackMessage('Dispute registered. Both source records preserved.');
      await fetchTimeline();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Submit New Event Handler
  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const peopleList = newEventPeople.split(',').map(p => p.trim()).filter(Boolean);
      const res = await fetch(`${API_BASE}/timeline/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-role': 'CONTRIBUTOR'
        },
        body: JSON.stringify({
          memorial_profile_id: 'demo-profile-001',
          title: newEventTitle,
          description: newEventDesc,
          category: newEventCategory,
          event_date: newEventDate,
          date_description: newEventDate,
          date_precision: newEventPrecision,
          location_name: newEventLocation || undefined,
          associated_people: peopleList,
          confidence: 'VERIFIED',
          verification_status: 'PENDING_REVIEW'
        })
      });
      if (!res.ok) throw new Error('Event creation failed');
      setShowCreateModal(false);
      setNewEventTitle('');
      setNewEventDesc('');
      setNewEventLocation('');
      setNewEventPeople('');
      setFeedbackMessage('Timeline event proposed for family review.');
      await fetchTimeline();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Date precision badge renderer
  const renderPrecisionBadge = (precision: DatePrecision) => {
    switch (precision) {
      case 'EXACT':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-2.5 h-2.5" />
            Exact Date
          </span>
        );
      case 'MONTH_YEAR':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Clock className="w-2.5 h-2.5" />
            Month & Year
          </span>
        );
      case 'YEAR_ONLY':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Calendar className="w-2.5 h-2.5" />
            Year Only
          </span>
        );
      case 'APPROXIMATE':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-2.5 h-2.5" />
            Approximate
          </span>
        );
      case 'UNKNOWN':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <HelpCircle className="w-2.5 h-2.5" />
            Undetermined Date
          </span>
        );
    }
  };

  // Confidence badge renderer
  const renderConfidenceBadge = (confidence: ConfidenceLevel) => {
    if (confidence === 'VERIFIED') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40">
          <ShieldCheck className="w-3 h-3 text-emerald-400" />
          GREEN VERIFIED
        </span>
      );
    }
    if (confidence === 'SUPPORTED_INFERENCE') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-950/80 text-amber-300 border border-amber-500/40">
          <Clock className="w-3 h-3 text-amber-400" />
          YELLOW SUPPORTED
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-950/80 text-rose-300 border border-rose-500/40">
        <AlertTriangle className="w-3 h-3 text-rose-400" />
        RED UNKNOWN
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 w-full space-y-6 animate-fadeIn">
      {/* Feedback Alert */}
        {feedbackMessage && (
          <div className="p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/40 text-indigo-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>{feedbackMessage}</span>
            </div>
            <button
              onClick={() => setFeedbackMessage(null)}
              className="text-slate-400 hover:text-white"
            >
              ✕
            </button>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-950/40 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-slate-400 hover:text-white"
            >
              ✕
            </button>
          </div>
        )}

        {/* Metric Cards Summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-slate-400">Total Documented Events</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold font-serif text-white">
                {timelineData?.total_events ?? 0}
              </span>
              <span className="text-[10px] text-emerald-400">Archival Grounded</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-slate-400">Verified Evidence</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold font-serif text-emerald-400">
                {timelineData?.events.filter(e => e.confidence === 'VERIFIED').length ?? 0}
              </span>
              <span className="text-[10px] text-slate-400">Primary Certifications</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-slate-400">Disputed Accounts</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold font-serif text-amber-400">
                {timelineData?.disputed_count ?? 0}
              </span>
              <span className="text-[10px] text-amber-500/80">Competing Records Retained</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-slate-400">Pending Family Review</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold font-serif text-sky-400">
                {timelineData?.unreviewed_count ?? 0}
              </span>
              <span className="text-[10px] text-slate-400">Awaiting Trustee Vote</span>
            </div>
          </div>
        </div>

        {/* Filter & Action Controls Toolbar */}
        <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-md flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
            {/* Search Input */}
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search event title, narrative, location, or people..."
                className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Category Filter */}
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Categories</option>
              <option value="Childhood">Childhood</option>
              <option value="Education">Education</option>
              <option value="Career">Career</option>
              <option value="Family">Family</option>
              <option value="Travel">Travel</option>
              <option value="Achievements">Achievements</option>
              <option value="Special events">Special Events</option>
              <option value="Hobbies">Hobbies & Interests</option>
              <option value="Personal stories">Personal Stories</option>
            </select>

            {/* Source Type Filter */}
            <select
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Sources</option>
              <option value="ORIGINAL_PHOTO">Photograph</option>
              <option value="DOCUMENT">Archival Document</option>
              <option value="ORIGINAL_AUDIO">Audio Recording</option>
              <option value="ORIGINAL_VIDEO">Video Reel</option>
              <option value="FAMILY_STORY">Family Story</option>
            </select>

            {/* Chronological Sort Direction Toggle */}
            <button
              onClick={() => setReverseChronological(!reverseChronological)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-medium transition-colors ${
                reverseChronological
                  ? 'border-indigo-500/50 bg-indigo-950/40 text-indigo-300'
                  : 'border-slate-700 bg-slate-800/80 text-slate-300 hover:text-white'
              }`}
            >
              <ArrowUpDown className="w-3.5 h-3.5" />
              <span>{reverseChronological ? 'Newest First' : 'Oldest First'}</span>
            </button>

            {/* Disputed Toggle */}
            <button
              onClick={() => setDisputedOnly(!disputedOnly)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-medium transition-colors ${
                disputedOnly
                  ? 'border-amber-500 bg-amber-950/40 text-amber-300'
                  : 'border-slate-700 bg-slate-800/80 text-slate-300 hover:text-white'
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Disputed Only</span>
            </button>
          </div>

          <div className="flex items-center gap-3">
            {/* AI Suggestion Generator Button */}
            <button
              onClick={handleGenerateAiSuggestions}
              disabled={isGeneratingAi}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-indigo-500/40 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 text-xs font-medium transition-colors disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isGeneratingAi ? 'Analyzing Evidence...' : 'Suggest AI Events'}</span>
            </button>

            {/* Propose Event Button */}
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Propose Event</span>
            </button>
          </div>
        </div>

        {/* Timeline Stream */}
        {loading ? (
          <div className="py-24 text-center space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin mx-auto" />
            <p className="text-xs text-slate-400">Loading chronological life journey...</p>
          </div>
        ) : !timelineData || timelineData.events.length === 0 ? (
          <div className="py-24 text-center space-y-4 rounded-2xl border border-slate-800 bg-slate-900/40 max-w-lg mx-auto p-8">
            <History className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="font-serif text-base font-semibold text-white">No Documented Events Found</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              No life journey events match the current filter criteria. Propose a new documented milestone or click
              &ldquo;Suggest AI Events&rdquo; to extract candidates from preserved memory records.
            </p>
            <button
              onClick={() => {
                setCategory('');
                setSearchQuery('');
                setSourceType('');
                setDisputedOnly(false);
              }}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800 text-xs text-slate-200 hover:bg-slate-700"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Filters</span>
            </button>
          </div>
        ) : (
          <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-indigo-500 before:via-indigo-800 before:to-slate-800">
            {timelineData.events.map((event) => {
              const displayYear = event.event_date
                ? new Date(event.event_date).getFullYear()
                : 'Undated';

              return (
                <div key={event.id} className="relative group">
                  {/* Timeline Anchor Node */}
                  <div className={`absolute -left-6 sm:-left-8 top-5 w-4 h-4 rounded-full border-2 transition-transform group-hover:scale-125 ${
                    event.is_disputed
                      ? 'border-amber-400 bg-amber-950'
                      : event.is_ai_suggested
                      ? 'border-sky-400 bg-sky-950'
                      : 'border-indigo-400 bg-slate-950'
                  }`} />

                  {/* Event Card Container */}
                  <div className={`p-6 rounded-2xl border transition-all ${
                    event.is_disputed
                      ? 'border-amber-500/40 bg-amber-950/20'
                      : event.is_ai_suggested
                      ? 'border-sky-500/40 bg-sky-950/20'
                      : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
                  } space-y-4`}>
                    {/* Header Row */}
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="px-2.5 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wider bg-slate-800 text-indigo-300 border border-slate-700">
                            {event.category}
                          </span>
                          {renderPrecisionBadge(event.date_precision)}
                          {renderConfidenceBadge(event.confidence)}

                          {event.is_ai_suggested && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-500/10 text-sky-300 border border-sky-500/30">
                              <Sparkles className="w-3 h-3 text-sky-400" />
                              AI Suggestion (Pending Review)
                            </span>
                          )}

                          {event.is_disputed && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30">
                              <AlertTriangle className="w-3 h-3 text-amber-400" />
                              Contested Archival Date
                            </span>
                          )}
                        </div>

                        <h3 className="font-serif text-lg font-bold text-white pt-1">
                          {event.title}
                        </h3>
                      </div>

                      {/* Date and Actions */}
                      <div className="text-right space-y-1">
                        <div className="font-mono text-sm font-semibold text-indigo-400 flex items-center justify-end gap-1.5">
                          <Calendar className="w-4 h-4 text-indigo-400" />
                          <span>{event.date_description || event.event_date || 'Date Undetermined'}</span>
                        </div>
                        <span className="text-[10px] text-slate-500">Epoch: {displayYear}</span>
                      </div>
                    </div>

                    {/* Narrative Description */}
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {event.description || 'No detailed narrative recorded for this documented milestone.'}
                    </p>

                    {/* Disputed Alert Box */}
                    {event.is_disputed && (
                      <div className="p-3 rounded-xl border border-amber-500/30 bg-amber-950/40 text-amber-200 text-xs space-y-1.5">
                        <div className="font-semibold flex items-center gap-1.5 text-amber-300">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>Archival Disagreement & Competing Accounts</span>
                        </div>
                        <p className="text-[11px] text-amber-200/90 leading-relaxed">
                          {event.dispute_notes || 'Multiple authenticated sources disagree on date or sequence. Both accounts are maintained intact.'}
                        </p>
                        {event.competing_evidence_ids.length > 0 && (
                          <div className="text-[10px] text-amber-400/80 font-mono">
                            Competing Evidence IDs: {event.competing_evidence_ids.join(', ')}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Meta Info Row: Location, People, Evidence */}
                    <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-4 text-xs">
                      <div className="flex flex-wrap items-center gap-4 text-slate-400">
                        {event.location_name && (
                          <div className="flex items-center gap-1 text-slate-300">
                            <MapPin className="w-3.5 h-3.5 text-rose-400" />
                            <span>{event.location_name}</span>
                          </div>
                        )}

                        {event.associated_people.length > 0 && (
                          <div className="flex items-center gap-1 text-slate-300">
                            <Users className="w-3.5 h-3.5 text-indigo-400" />
                            <span>{event.associated_people.join(', ')}</span>
                          </div>
                        )}

                        {event.evidence_ids.length > 0 && (
                          <div className="flex items-center gap-1 text-slate-400 font-mono text-[11px]">
                            <FileText className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Evidence: {event.evidence_ids.join(', ')}</span>
                          </div>
                        )}
                      </div>

                      {/* Interactive Buttons */}
                      <div className="flex items-center gap-2">
                        {/* 3D Memory Room Anchor Link */}
                        {event.memory_room_object_id && (
                          <Link
                            href={`/memory-room?focus=${event.memory_room_object_id}`}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-indigo-500/30 bg-indigo-950/40 hover:bg-indigo-900/60 text-indigo-300 text-xs transition-colors"
                          >
                            <Box className="w-3.5 h-3.5 text-indigo-400" />
                            <span>Inspect in 3D Room</span>
                          </Link>
                        )}

                        {/* Dispute Button */}
                        <button
                          onClick={() => {
                            setDisputeEventTarget(event);
                            setShowDisputeModal(true);
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-700 hover:border-amber-500/50 text-slate-300 hover:text-amber-300 text-xs transition-colors"
                        >
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>Flag Conflict</span>
                        </button>

                        {/* Review actions if AI Suggested or Pending Review */}
                        {event.verification_status === 'PENDING_REVIEW' && (
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => handleVerifyEvent(event.id, 'VERIFIED')}
                              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-colors"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Verify</span>
                            </button>
                            <button
                              onClick={() => handleVerifyEvent(event.id, 'REJECTED')}
                              className="inline-flex items-center gap-1 px-2 py-1 rounded-lg border border-rose-800/80 hover:bg-rose-950 text-rose-300 text-xs transition-colors"
                            >
                              <XCircle className="w-3.5 h-3.5" />
                              <span>Reject</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

      {/* Flag Dispute Modal */}
      {showDisputeModal && disputeEventTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="font-serif text-base font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Flag Archival Dispute: {disputeEventTarget.title}</span>
              </h3>
              <button
                onClick={() => setShowDisputeModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              In accordance with ECHO&apos;s evidentiary ethics, conflicting recollections or records will NOT overwrite existing accounts. Both perspectives will be documented side-by-side with citations.
            </p>

            <form onSubmit={handleSubmitDispute} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Reason for Dispute / Contradiction
                </label>
                <textarea
                  required
                  rows={3}
                  value={disputeReason}
                  onChange={(e) => setDisputeReason(e.target.value)}
                  placeholder="e.g. Handwritten photo album caption specifies July 1981, while archival letters state August 1982..."
                  className="w-full p-2.5 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Competing Proposed Date or Epoch (Optional)
                </label>
                <input
                  type="text"
                  value={competingDate}
                  onChange={(e) => setCompetingDate(e.target.value)}
                  placeholder="e.g. July 1981"
                  className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowDisputeModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-300 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {isSubmitting ? 'Recording...' : 'Register Conflict'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Propose Event Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-xl p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="font-serif text-base font-bold text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-indigo-400" />
                <span>Propose Documented Life Milestone</span>
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateEvent} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Event Title
                </label>
                <input
                  type="text"
                  required
                  value={newEventTitle}
                  onChange={(e) => setNewEventTitle(e.target.value)}
                  placeholder="e.g. Conferred Fellowship of Royal Society"
                  className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Category
                  </label>
                  <select
                    value={newEventCategory}
                    onChange={(e) => setNewEventCategory(e.target.value)}
                    className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="Childhood">Childhood</option>
                    <option value="Education">Education</option>
                    <option value="Career">Career</option>
                    <option value="Family">Family</option>
                    <option value="Travel">Travel</option>
                    <option value="Achievements">Achievements</option>
                    <option value="Special events">Special Events</option>
                    <option value="Hobbies">Hobbies & Interests</option>
                    <option value="Personal stories">Personal Stories</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Date Precision
                  </label>
                  <select
                    value={newEventPrecision}
                    onChange={(e) => setNewEventPrecision(e.target.value as DatePrecision)}
                    className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="EXACT">Exact (Full Day, Month, Year)</option>
                    <option value="MONTH_YEAR">Month and Year</option>
                    <option value="YEAR_ONLY">Year Only</option>
                    <option value="APPROXIMATE">Approximate (Circa)</option>
                    <option value="UNKNOWN">Date Undetermined</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Documented Date
                  </label>
                  <input
                    type="date"
                    value={newEventDate}
                    onChange={(e) => setNewEventDate(e.target.value)}
                    className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Location Name
                  </label>
                  <input
                    type="text"
                    value={newEventLocation}
                    onChange={(e) => setNewEventLocation(e.target.value)}
                    placeholder="e.g. Edinburgh, Scotland"
                    className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Associated People (Comma Separated)
                </label>
                <input
                  type="text"
                  value={newEventPeople}
                  onChange={(e) => setNewEventPeople(e.target.value)}
                  placeholder="e.g. Arthur Vance, Eleanor Vance"
                  className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Archival Narrative & Citation Notes
                </label>
                <textarea
                  rows={3}
                  value={newEventDesc}
                  onChange={(e) => setNewEventDesc(e.target.value)}
                  placeholder="Describe the milestone as substantiated by archival records..."
                  className="w-full p-2.5 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-300 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Proposal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
