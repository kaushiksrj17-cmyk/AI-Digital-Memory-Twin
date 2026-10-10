'use client';

import React, { useState, useEffect } from 'react';
import {
  ProcessingJob,
  ProcessingAnalytics,
  ProcessingStatus
} from '@/types';
import {
  Cpu,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileText,
  Image as ImageIcon,
  Film,
  Music,
  Search,
  Filter,
  Eye,
  RotateCcw,
  ShieldAlert,
  Layers,
  Database,
  ArrowRight,
  Info
} from 'lucide-react';

export default function ProcessingPage() {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [analytics, setAnalytics] = useState<ProcessingAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [retryingId, setRetryingId] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<ProcessingJob | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchProcessingData = async () => {
    setLoading(true);
    try {
      // 1. Fetch processing jobs
      const jobsRes = await fetch('/api/v1/processing');
      if (jobsRes.ok) {
        const jobsData = await jobsRes.json();
        setJobs(jobsData);
      } else {
        setJobs([]);
      }

      // 2. Fetch processing analytics
      const analyticsRes = await fetch('/api/v1/analytics/processing');
      if (analyticsRes.ok) {
        const analyticsData = await analyticsRes.json();
        setAnalytics(analyticsData);
      }
    } catch (err) {
      console.error('Failed to load processing telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProcessingData();
    const interval = setInterval(fetchProcessingData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleRetry = async (mediaId: string) => {
    setRetryingId(mediaId);
    try {
      const res = await fetch(`/api/v1/processing/${mediaId}/retry`, {
        method: 'POST'
      });
      if (res.ok) {
        await fetchProcessingData();
      } else {
        alert('Retry attempt rejected by processing queue.');
      }
    } catch (err) {
      console.error('Retry request failed:', err);
    } finally {
      setRetryingId(null);
    }
  };

  const getStatusBadge = (status: ProcessingStatus) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            COMPLETED
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <RefreshCw className="w-3 h-3 animate-spin" />
            PROCESSING
          </span>
        );
      case 'PENDING':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3 h-3" />
            PENDING
          </span>
        );
      case 'REVIEW_REQUIRED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40">
            <ShieldAlert className="w-3 h-3" />
            REVIEW REQUIRED
          </span>
        );
      case 'FAILED':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3" />
            FAILED
          </span>
        );
    }
  };

  const getProcessorIcon = (processor: string) => {
    if (processor.includes('image')) return <ImageIcon className="w-4 h-4 text-sky-400" />;
    if (processor.includes('video')) return <Film className="w-4 h-4 text-purple-400" />;
    if (processor.includes('audio')) return <Music className="w-4 h-4 text-amber-400" />;
    return <FileText className="w-4 h-4 text-emerald-400" />;
  };

  const filteredJobs = jobs.filter((job) => {
    const matchesStatus = statusFilter === 'ALL' || job.processing_status === statusFilter;
    const matchesQuery =
      searchQuery === '' ||
      job.media_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (job.memory_id && job.memory_id.toLowerCase().includes(searchQuery.toLowerCase())) ||
      job.processor.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesQuery;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8 animate-fadeIn">
      {/* Research Pipeline Notice */}
        <div className="p-4 rounded-2xl border border-indigo-900/50 bg-indigo-950/20 flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs">
          <div className="flex items-start gap-3">
            <Layers className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-indigo-200">Asynchronous Evidentiary Pipeline (Phase 3 Active)</h4>
              <p className="text-slate-400 text-[11px] mt-0.5">
                Every multimedia asset uploaded to the vault undergoes deterministic metadata inspection, unconfigured-safe AI provider gating, and atomic provenance attribution before becoming accessible to future RAG or Memory DNA.
              </p>
            </div>
          </div>
          <button
            onClick={fetchProcessingData}
            disabled={loading}
            className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors flex items-center gap-2 self-start md:self-auto shrink-0"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Queue</span>
          </button>
        </div>

        {/* Analytics Telemetry Cards */}
        {analytics ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-sm font-semibold tracking-wide text-slate-300">
                PROCESSING TELEMETRY & INGESTION METRICS
              </h3>
              <span className="text-[11px] font-mono text-slate-500">
                Avg Latency: {analytics.average_latency_ms} ms &bull; Evidence Extracted: {analytics.total_evidence_items}
              </span>
            </div>

            {/* Core Job Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
              <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
                <span className="text-[10px] text-slate-400 uppercase font-mono">Total Memories</span>
                <p className="text-xl font-bold font-serif text-slate-100 mt-1">{analytics.total_memories}</p>
              </div>

              <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
                <span className="text-[10px] text-slate-400 uppercase font-mono">Total Media</span>
                <p className="text-xl font-bold font-serif text-slate-100 mt-1">{analytics.total_media}</p>
              </div>

              <div className="p-3.5 rounded-xl border border-amber-900/40 bg-amber-950/10">
                <span className="text-[10px] text-amber-400 uppercase font-mono">Pending</span>
                <p className="text-xl font-bold font-serif text-amber-300 mt-1">{analytics.pending_jobs}</p>
              </div>

              <div className="p-3.5 rounded-xl border border-indigo-900/40 bg-indigo-950/10">
                <span className="text-[10px] text-indigo-400 uppercase font-mono">Processing</span>
                <p className="text-xl font-bold font-serif text-indigo-300 mt-1">{analytics.processing_jobs}</p>
              </div>

              <div className="p-3.5 rounded-xl border border-emerald-900/40 bg-emerald-950/10">
                <span className="text-[10px] text-emerald-400 uppercase font-mono">Completed</span>
                <p className="text-xl font-bold font-serif text-emerald-300 mt-1">{analytics.completed_jobs}</p>
              </div>

              <div className="p-3.5 rounded-xl border border-rose-900/40 bg-rose-950/10">
                <span className="text-[10px] text-rose-400 uppercase font-mono">Failed</span>
                <p className="text-xl font-bold font-serif text-rose-300 mt-1">{analytics.failed_jobs}</p>
              </div>

              <div className="p-3.5 rounded-xl border border-amber-900/50 bg-amber-950/20">
                <span className="text-[10px] text-amber-300 uppercase font-mono">Review Required</span>
                <p className="text-xl font-bold font-serif text-amber-200 mt-1">{analytics.review_required_jobs}</p>
              </div>
            </div>

            {/* Modality Extraction Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div className="p-3 rounded-xl border border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ImageIcon className="w-4 h-4 text-sky-400" />
                  <span className="text-xs text-slate-300">Images</span>
                </div>
                <span className="font-mono text-sm font-semibold text-slate-200">
                  {analytics.images_processed_count}
                </span>
              </div>

              <div className="p-3 rounded-xl border border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Film className="w-4 h-4 text-purple-400" />
                  <span className="text-xs text-slate-300">Videos</span>
                </div>
                <span className="font-mono text-sm font-semibold text-slate-200">
                  {analytics.video_processed_count}
                </span>
              </div>

              <div className="p-3 rounded-xl border border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Music className="w-4 h-4 text-amber-400" />
                  <span className="text-xs text-slate-300">Audio/STT</span>
                </div>
                <span className="font-mono text-sm font-semibold text-slate-200">
                  {analytics.audio_transcribed_count}
                </span>
              </div>

              <div className="p-3 rounded-xl border border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs text-slate-300">Documents</span>
                </div>
                <span className="font-mono text-sm font-semibold text-slate-200">
                  {analytics.documents_processed_count}
                </span>
              </div>

              <div className="p-3 rounded-xl border border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-indigo-400" />
                  <span className="text-xs text-slate-300">OCR Executed</span>
                </div>
                <span className="font-mono text-sm font-semibold text-slate-200">
                  {analytics.ocr_processed_count}
                </span>
              </div>
            </div>
          </div>
        ) : null}

        {/* Filter and Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-4 rounded-2xl border border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-2 flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-500 shrink-0" />
            <input
              type="text"
              placeholder="Search by Media ID, Memory ID, or Processor..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-transparent text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-2 shrink-0 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400 text-[11px]">Filter Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none"
            >
              <option value="ALL">All Statuses ({jobs.length})</option>
              <option value="COMPLETED">Completed</option>
              <option value="PROCESSING">Processing</option>
              <option value="PENDING">Pending</option>
              <option value="FAILED">Failed</option>
              <option value="REVIEW_REQUIRED">Review Required</option>
            </select>
          </div>
        </div>

        {/* Queue Table */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/30 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 font-semibold text-slate-200">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span>Active Multimodal Processing Queue</span>
            </div>
            <span className="text-slate-400 font-mono text-[11px]">
              Showing {filteredJobs.length} of {jobs.length} jobs
            </span>
          </div>

          {filteredJobs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/70 text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                    <th className="py-3 px-4">Media & Memory</th>
                    <th className="py-3 px-4">Processor</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Version</th>
                    <th className="py-3 px-4">Started / Completed</th>
                    <th className="py-3 px-4">Retries</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {filteredJobs.map((job) => (
                    <tr key={job.id} className="hover:bg-slate-900/60 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="space-y-0.5">
                          <div className="font-mono font-medium text-slate-200 text-[11px]">
                            {job.media_id}
                          </div>
                          {job.memory_id ? (
                            <div className="text-[10px] text-indigo-400 font-mono">
                              Memory: {job.memory_id}
                            </div>
                          ) : (
                            <div className="text-[10px] text-slate-500">Standalone Ingestion</div>
                          )}
                        </div>
                      </td>

                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          {getProcessorIcon(job.processor)}
                          <span className="font-mono text-slate-300 text-[11px]">{job.processor}</span>
                        </div>
                      </td>

                      <td className="py-3.5 px-4">
                        {getStatusBadge(job.processing_status)}
                        {job.error_message && (
                          <p className="text-[10px] text-rose-400 mt-1 max-w-xs truncate" title={job.error_message}>
                            {job.error_message}
                          </p>
                        )}
                      </td>

                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                        {job.processing_version || 'v3.0.0'}
                      </td>

                      <td className="py-3.5 px-4 text-[11px] text-slate-400 space-y-0.5">
                        <div>
                          Start:{' '}
                          <span className="text-slate-300 font-mono">
                            {job.started_at ? new Date(job.started_at).toLocaleTimeString() : 'N/A'}
                          </span>
                        </div>
                        {job.completed_at && (
                          <div>
                            End:{' '}
                            <span className="text-slate-300 font-mono">
                              {new Date(job.completed_at).toLocaleTimeString()}
                            </span>
                          </div>
                        )}
                      </td>

                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                        {job.retry_count}
                      </td>

                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => setSelectedJob(job)}
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                            title="Inspect Job Metadata"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>

                          {(job.processing_status === 'FAILED' ||
                            job.processing_status === 'REVIEW_REQUIRED') && (
                            <button
                              onClick={() => handleRetry(job.media_id)}
                              disabled={retryingId === job.media_id}
                              className="px-2.5 py-1 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/30 text-[11px] font-medium transition-colors flex items-center gap-1"
                              title="Safe Idempotent Retry"
                            >
                              <RotateCcw className={`w-3 h-3 ${retryingId === job.media_id ? 'animate-spin' : ''}`} />
                              <span>Retry</span>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-12 text-center space-y-3">
              <CheckCircle2 className="w-8 h-8 text-slate-600 mx-auto" />
              <h4 className="font-serif text-sm font-semibold text-slate-300">
                Queue Empty / No Matching Jobs
              </h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                No active or historical processing operations match your query. Upload multimedia in the Memory Vault to initiate the Phase 3 evidence extraction pipeline.
              </p>
            </div>
          )}
        </div>

        {/* Inspect Modal */}
        {selectedJob && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-5">
              <div className="flex items-start justify-between border-b border-slate-800 pb-3">
                <div className="space-y-0.5">
                  <span className="text-[10px] font-mono uppercase text-indigo-400">Processing Job Inspector</span>
                  <h3 className="font-serif text-base font-semibold text-slate-100">
                    Media ID: {selectedJob.media_id}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedJob(null)}
                  className="p-1 text-slate-400 hover:text-slate-200"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div className="grid grid-cols-2 gap-2 p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px]">
                  <div>
                    <span className="text-slate-500">Status:</span>
                    <div className="mt-1">{getStatusBadge(selectedJob.processing_status)}</div>
                  </div>
                  <div>
                    <span className="text-slate-500">Processor:</span>
                    <p className="font-mono text-slate-200 mt-1">{selectedJob.processor}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Pipeline Version:</span>
                    <p className="font-mono text-slate-200 mt-1">{selectedJob.processing_version}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Retry Counter:</span>
                    <p className="font-mono text-slate-200 mt-1">{selectedJob.retry_count}</p>
                  </div>
                </div>

                {selectedJob.error_message && (
                  <div className="p-3 rounded-xl bg-rose-950/20 border border-rose-900/40 text-rose-300 space-y-1">
                    <span className="font-semibold text-[11px]">Error Diagnostic:</span>
                    <p className="font-mono text-[10px] leading-relaxed">{selectedJob.error_message}</p>
                  </div>
                )}

                {selectedJob.metadata_json && (
                  <div className="space-y-1">
                    <span className="text-slate-400 font-semibold text-[11px]">Derived Metadata & Telemetry:</span>
                    <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-300 overflow-x-auto max-h-48">
                      {JSON.stringify(selectedJob.metadata_json, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              <div className="flex justify-end pt-2 border-t border-slate-800">
                <button
                  onClick={() => setSelectedJob(null)}
                  className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium"
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
