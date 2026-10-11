'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCcw,
  Clock,
  Sparkles,
  ArrowLeft,
  ShieldCheck,
  Plus,
  MessageSquare,
  Layers,
  FileCheck,
  User,
  History,
  Eye,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import {
  FamilyContribution,
  ContributionStatus,
  ContributionType,
  ConfidenceLevel,
  FamilyRole
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export default function ContributionsReviewPage() {
  const [contributions, setContributions] = useState<FamilyContribution[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  // Review Action Modal State
  const [selectedContribution, setSelectedContribution] = useState<FamilyContribution | null>(null);
  const [reviewDecision, setReviewDecision] = useState<ContributionStatus>('APPROVED');
  const [reviewNotes, setReviewNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Expanded card version history
  const [expandedHistoryId, setExpandedHistoryId] = useState<string | null>(null);

  // New Contribution Modal State
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newType, setNewType] = useState<ContributionType>('NEW_MEMORY');
  const [newNarrative, setNewNarrative] = useState('');
  const [newNotes, setNewNotes] = useState('');

  const fetchContributions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);

      const res = await fetch(`${API_BASE}/family/contributions?${params.toString()}`, {
        headers: { 'x-user-id': 'demo-user-001' }
      });
      if (!res.ok) throw new Error('Failed to load contributions queue');
      const data = await res.json();
      setContributions(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error communicating with backend review service');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchContributions();
  }, [fetchContributions]);

  // Handle Review Submission
  const handleExecuteReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedContribution) return;
    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/family/contributions/${selectedContribution.id}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': 'demo-user-001'
        },
        body: JSON.stringify({
          decision: reviewDecision,
          review_notes: reviewNotes
        })
      });
      if (!res.ok) {
        const errJson = await res.json();
        throw new Error(errJson.detail || 'Review action failed');
      }
      setSelectedContribution(null);
      setReviewNotes('');
      setFeedback(`Review committed: ${reviewDecision}.`);
      await fetchContributions();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Submit New Contribution
  const handleCreateContribution = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/family/contributions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': 'demo-user-003'
        },
        body: JSON.stringify({
          contribution_type: newType,
          title: newTitle,
          proposed_content: { narrative: newNarrative },
          contributor_notes: newNotes,
          supporting_evidence: [],
          confidence: 'SUPPORTED_INFERENCE',
          provenance: 'USER_PROVIDED'
        })
      });
      if (!res.ok) throw new Error('Failed to submit contribution');
      setShowSubmitModal(false);
      setNewTitle('');
      setNewNarrative('');
      setNewNotes('');
      setFeedback('Contribution successfully submitted for family guardian review.');
      await fetchContributions();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Status Badge Renderer
  const renderStatusBadge = (status: ContributionStatus) => {
    switch (status) {
      case 'APPROVED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" />
            Approved
          </span>
        );
      case 'DISPUTED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3 h-3" />
            Disputed Account
          </span>
        );
      case 'NEEDS_CHANGES':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-sky-500/10 text-sky-400 border border-sky-500/30">
            <Clock className="w-3 h-3" />
            Needs Changes
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <XCircle className="w-3 h-3" />
            Rejected
          </span>
        );
      case 'SUBMITTED':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
            <Clock className="w-3 h-3" />
            Pending Review
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 w-full space-y-6 animate-fadeIn">
      {/* Navigation & Controls */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link
            href="/family"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Family Workspace</span>
          </Link>

          <button
            onClick={() => setShowSubmitModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Submit Memory Contribution</span>
          </button>
        </div>

        {/* Feedback / Error Alerts */}
        {feedback && (
          <div className="p-4 rounded-xl border border-indigo-500/30 bg-indigo-950/40 text-indigo-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>{feedback}</span>
            </div>
            <button onClick={() => setFeedback(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {error && (
          <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-950/40 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Ethical Governance Notice */}
        <div className="p-4 rounded-2xl border border-indigo-500/30 bg-indigo-950/20 text-xs text-indigo-200/90 leading-relaxed flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
          <div>
            <strong>Independent Verification Safeguard:</strong> All submitted memories, metadata corrections,
            and alternate dates require independent review by an authorized family guardian. Contributors cannot
            approve their own submissions. Contested memories preserve competing perspectives side-by-side.
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 pb-2 border-b border-slate-800 text-xs">
          {[
            { label: 'All Contributions', val: '' },
            { label: 'Pending Review', val: 'SUBMITTED' },
            { label: 'Approved', val: 'APPROVED' },
            { label: 'Disputed', val: 'DISPUTED' },
            { label: 'Needs Changes', val: 'NEEDS_CHANGES' },
            { label: 'Rejected', val: 'REJECTED' }
          ].map((tab) => (
            <button
              key={tab.val}
              onClick={() => setStatusFilter(tab.val)}
              className={`px-3 py-1.5 rounded-xl border transition-colors ${
                statusFilter === tab.val
                  ? 'border-indigo-500 bg-indigo-600/20 text-indigo-300 font-semibold'
                  : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Contributions Stream */}
        {loading ? (
          <div className="py-24 text-center space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin mx-auto" />
            <p className="text-xs text-slate-400">Loading contribution review queue...</p>
          </div>
        ) : contributions.length === 0 ? (
          <div className="py-24 text-center space-y-3 rounded-2xl border border-slate-800 bg-slate-900/40 p-8">
            <FileCheck className="w-10 h-10 text-slate-600 mx-auto" />
            <h4 className="font-serif text-sm font-semibold text-white">No Contributions Found</h4>
            <p className="text-xs text-slate-400">There are no contributions matching the current filter state.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {contributions.map((contrib) => (
              <div
                key={contrib.id}
                className={`p-6 rounded-2xl border transition-all ${
                  contrib.status === 'DISPUTED'
                    ? 'border-amber-500/40 bg-amber-950/20'
                    : contrib.status === 'SUBMITTED'
                    ? 'border-indigo-500/40 bg-slate-900/80 shadow-lg shadow-indigo-950/30'
                    : 'border-slate-800 bg-slate-900/50'
                } space-y-4`}
              >
                {/* Header */}
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-semibold uppercase bg-slate-800 text-indigo-300 border border-slate-700">
                        {contrib.contribution_type.replace(/_/g, ' ')}
                      </span>
                      {renderStatusBadge(contrib.status)}
                      <span className="text-[11px] text-slate-400">
                        Version {contrib.version}
                      </span>
                    </div>

                    <h3 className="font-serif text-base font-bold text-white pt-1">
                      {contrib.title}
                    </h3>
                  </div>

                  <div className="text-right text-xs space-y-0.5">
                    <div className="text-slate-300 font-medium flex items-center justify-end gap-1">
                      <User className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{contrib.contributor_name}</span>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(contrib.submitted_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Diff Comparison (Original vs Proposed) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                  <div className="p-3 rounded-xl border border-slate-800 bg-slate-950/60 space-y-1.5 text-xs">
                    <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
                      Original Archival Record
                    </span>
                    <pre className="text-[11px] font-sans text-slate-400 whitespace-pre-wrap leading-relaxed overflow-x-auto">
                      {contrib.original_content
                        ? JSON.stringify(contrib.original_content, null, 2)
                        : '(New submission; no prior existing record)'}
                    </pre>
                  </div>

                  <div className="p-3 rounded-xl border border-indigo-500/30 bg-indigo-950/20 space-y-1.5 text-xs">
                    <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-wider">
                      Proposed Family Contribution
                    </span>
                    <pre className="text-[11px] font-sans text-indigo-200 whitespace-pre-wrap leading-relaxed overflow-x-auto">
                      {JSON.stringify(contrib.proposed_content, null, 2)}
                    </pre>
                  </div>
                </div>

                {/* Contributor Testimony & Notes */}
                {contrib.contributor_notes && (
                  <div className="p-3 rounded-xl border border-slate-800 bg-slate-800/40 text-xs text-slate-300 space-y-1">
                    <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1">
                      <MessageSquare className="w-3 h-3 text-indigo-400" />
                      <span>Contributor Testimony</span>
                    </span>
                    <p className="italic leading-relaxed">&ldquo;{contrib.contributor_notes}&rdquo;</p>
                  </div>
                )}

                {/* Review Details if already reviewed */}
                {contrib.review_decision && (
                  <div className="p-3 rounded-xl border border-slate-800 bg-slate-900 text-xs space-y-1">
                    <div className="flex items-center justify-between text-slate-400 text-[11px]">
                      <span>Reviewed by: <strong>{contrib.reviewer_name}</strong></span>
                      <span>Decision: <strong>{contrib.review_decision}</strong></span>
                    </div>
                    {contrib.review_notes && (
                      <p className="text-slate-300 text-xs pt-1 border-t border-slate-800">
                        {contrib.review_notes}
                      </p>
                    )}
                  </div>
                )}

                {/* Actions & Version History Toggle */}
                <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
                  <button
                    onClick={() =>
                      setExpandedHistoryId(expandedHistoryId === contrib.id ? null : contrib.id)
                    }
                    className="inline-flex items-center gap-1 text-slate-400 hover:text-white transition-colors"
                  >
                    <History className="w-3.5 h-3.5" />
                    <span>Version History ({contrib.version_history.length})</span>
                    {expandedHistoryId === contrib.id ? (
                      <ChevronUp className="w-3 h-3" />
                    ) : (
                      <ChevronDown className="w-3 h-3" />
                    )}
                  </button>

                  {contrib.status === 'SUBMITTED' && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setSelectedContribution(contrib);
                          setReviewDecision('APPROVED');
                        }}
                        className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-md shadow-emerald-600/20"
                      >
                        Review &amp; Decide
                      </button>
                    </div>
                  )}
                </div>

                {/* Expanded Version History Drawer */}
                {expandedHistoryId === contrib.id && (
                  <div className="p-4 rounded-xl border border-slate-800 bg-slate-950 text-xs space-y-2 animate-in fade-in">
                    <span className="text-[10px] font-mono text-slate-500 uppercase">
                      Audit Trail &amp; Revision Log
                    </span>
                    <div className="space-y-2">
                      {contrib.version_history.map((vh, idx) => (
                        <div
                          key={idx}
                          className="p-2 rounded-lg border border-slate-800 bg-slate-900/60 flex items-center justify-between text-[11px]"
                        >
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-indigo-400">v{vh.version}</span>
                            <span className="font-semibold text-white">{vh.action}</span>
                            {vh.reviewer && <span className="text-slate-400">by {vh.reviewer}</span>}
                            {vh.contributor && <span className="text-slate-400">by {vh.contributor}</span>}
                          </div>
                          <span className="text-slate-500 font-mono text-[10px]">
                            {new Date(vh.timestamp).toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

      {/* Review Decision Modal */}
      {selectedContribution && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="font-serif text-base font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Review Contribution: {selectedContribution.title}</span>
              </h3>
              <button onClick={() => setSelectedContribution(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleExecuteReview} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Review Decision
                </label>
                <select
                  value={reviewDecision}
                  onChange={(e) => setReviewDecision(e.target.value as ContributionStatus)}
                  className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500 font-medium"
                >
                  <option value="APPROVED">Approve and Commit to Archive</option>
                  <option value="NEEDS_CHANGES">Request Revisions from Contributor</option>
                  <option value="DISPUTED">Mark as Disputed (Preserve Both Accounts)</option>
                  <option value="REJECTED">Reject Contribution</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Review Notes &amp; Evidentiary Justification
                </label>
                <textarea
                  required
                  rows={3}
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="State the archival evidence or family consensus supporting this decision..."
                  className="w-full p-2.5 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedContribution(null)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-300 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {isSubmitting ? 'Recording...' : 'Commit Review Decision'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Submit Contribution Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="font-serif text-base font-bold text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-indigo-400" />
                <span>Submit Memory Contribution</span>
              </h3>
              <button onClick={() => setShowSubmitModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleCreateContribution} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Contribution Title
                </label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Summer holiday recollection at Lake Windermere"
                  className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Contribution Type
                </label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value as ContributionType)}
                  className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="NEW_MEMORY">New Memory Recollection</option>
                  <option value="METADATA_CORRECTION">Metadata Correction</option>
                  <option value="ALTERNATIVE_DATE_OR_FACT">Alternative Date or Disputed Fact</option>
                  <option value="SUPPORTING_DOCUMENT">Supporting Document / Citation</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Proposed Narrative or Details
                </label>
                <textarea
                  required
                  rows={4}
                  value={newNarrative}
                  onChange={(e) => setNewNarrative(e.target.value)}
                  placeholder="Write your recollection or detail the archival amendment..."
                  className="w-full p-2.5 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Personal Testimony Notes (Optional)
                </label>
                <input
                  type="text"
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  placeholder="e.g. Recounted by Aunt Eleanor during summer 2024 interview..."
                  className="w-full p-2 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowSubmitModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-300 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit to Queue'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
