'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { EthicalBanner } from '@/components/EthicalBanner';
import {
  GraduationCap,
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  Shield,
  Play,
  RefreshCw,
  HardDrive,
  FileCheck,
  Lock,
  Layers,
  Search,
  Sliders,
  Cpu,
  Clock,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

interface AggregateMetrics {
  mean_precision: number | null;
  mean_recall: number | null;
  mean_f1: number | null;
  retrieval_accuracy: number | null;
  grounded_response_rate: number | null;
  unsupported_claim_rate: number | null;
  boundary_violation_rate: number | null;
  safe_unknown_rate: number | null;
  mean_latency_ms: number | null;
  evaluated_query_count: number;
}

interface BenchmarkQuery {
  query_id: string;
  query: string;
  category: string;
  expected_evidence_ids: string[];
  retrieved_evidence_ids: string[];
  precision: number | null;
  recall: number | null;
  f1: number | null;
  retrieval_accuracy: number | null;
  guardian_decision: string;
  confidence_assigned: string;
  violations_detected: string[];
  recommended_action: string;
  latency_ms: number;
  matches_expected_decision: boolean;
}

interface BenchmarkData {
  benchmark_id: string;
  evaluation_status: string;
  timestamp: string | null;
  aggregate_metrics: AggregateMetrics;
  queries: BenchmarkQuery[];
  summary_note: string;
}

interface OperationalTelemetry {
  archive_counts: {
    total_memories: number;
    total_media: number;
    indexed_evidence: number;
    recorded_contradictions: number;
  };
  conversation_telemetry: {
    active_sessions: number;
    total_dialogue_queries: number;
    verified_answers: number;
    supported_answers: number;
    unknown_answers: number;
    guardian_revisions: number;
    guardian_blocks: number;
  };
}

export default function ResearchDashboardPage() {
  const [benchmarkData, setBenchmarkData] = useState<BenchmarkData>({
    benchmark_id: 'echo-evaluation-suite-v1',
    evaluation_status: 'NOT EVALUATED',
    timestamp: null,
    aggregate_metrics: {
      mean_precision: null,
      mean_recall: null,
      mean_f1: null,
      retrieval_accuracy: null,
      grounded_response_rate: null,
      unsupported_claim_rate: null,
      boundary_violation_rate: null,
      safe_unknown_rate: null,
      mean_latency_ms: null,
      evaluated_query_count: 0,
    },
    queries: [],
    summary_note: 'Benchmark suite has not yet been executed. Showing Not yet evaluated.',
  });

  const [telemetry, setTelemetry] = useState<OperationalTelemetry>({
    archive_counts: {
      total_memories: 0,
      total_media: 0,
      indexed_evidence: 0,
      recorded_contradictions: 0,
    },
    conversation_telemetry: {
      active_sessions: 0,
      total_dialogue_queries: 0,
      verified_answers: 0,
      supported_answers: 0,
      unknown_answers: 0,
      guardian_revisions: 0,
      guardian_blocks: 0,
    },
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isRunningEvaluation, setIsRunningEvaluation] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const benchRes = await fetch('http://127.0.0.1:8000/api/v1/research/benchmarks');
      if (benchRes.ok) {
        const bJson = await benchRes.json();
        setBenchmarkData(bJson);
      }

      const telemRes = await fetch('http://127.0.0.1:8000/api/v1/research/metrics');
      if (telemRes.ok) {
        const tJson = await telemRes.json();
        setTelemetry(tJson);
      }
    } catch (e: any) {
      console.warn('Backend not currently reachable, keeping existing state');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const runBenchmark = async () => {
    setIsRunningEvaluation(true);
    setErrorMsg(null);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/research/benchmarks/run', {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setBenchmarkData(data);
        await fetchData();
      } else {
        setErrorMsg('Failed to run benchmark suite. Please ensure the backend is running.');
      }
    } catch (e: any) {
      setErrorMsg(`Benchmark execution failed: ${e.message}`);
    } finally {
      setIsRunningEvaluation(false);
    }
  };

  const isEvaluated = benchmarkData.evaluation_status === 'EVALUATED';
  const agg = benchmarkData.aggregate_metrics;

  const formatPct = (val: number | null | undefined) => {
    if (val === null || val === undefined) return 'Not yet evaluated';
    return `${(val * 100).toFixed(1)}%`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8 animate-fadeIn">
      <EthicalBanner variant="card" />

        {/* Environmental & Architecture Badges */}
        <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1.5">
              <HardDrive className="w-3.5 h-3.5" />
              <span>D:\ECHO (Strict Local Volume)</span>
            </span>

            <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5" />
              <span>Zero Cloud Egress Active</span>
            </span>

            <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5" />
              <span>Offline Mock Providers &amp; Labeled Fixtures</span>
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchData}
              disabled={isLoading}
              className="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>

            <button
              onClick={runBenchmark}
              disabled={isRunningEvaluation}
              className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md shadow-indigo-600/20 transition-colors"
            >
              <Play className={`w-3.5 h-3.5 ${isRunningEvaluation ? 'animate-pulse' : ''}`} />
              <span>{isRunningEvaluation ? 'Evaluating Suite...' : 'Run Benchmark Evaluation'}</span>
            </button>
          </div>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-xl border border-rose-800 bg-rose-950/40 text-xs text-rose-300 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Evaluation Status Banner */}
        <div className={`p-6 rounded-3xl border ${
          isEvaluated
            ? 'border-emerald-500/30 bg-gradient-to-r from-emerald-950/20 via-slate-900 to-slate-900'
            : 'border-amber-500/30 bg-gradient-to-r from-amber-950/20 via-slate-900 to-slate-900'
        } space-y-3`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-2xl flex items-center justify-center font-bold ${
                isEvaluated ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
              }`}>
                <GraduationCap className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="font-serif text-lg font-bold text-white">Academic Benchmark Protocol</h2>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wide uppercase ${
                    isEvaluated ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}>
                    {benchmarkData.evaluation_status}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  {benchmarkData.summary_note}
                </p>
              </div>
            </div>

            {benchmarkData.timestamp && (
              <div className="text-right text-[11px] text-slate-400 font-mono">
                <div>Evaluated at:</div>
                <div className="text-slate-300 font-semibold">{new Date(benchmarkData.timestamp).toLocaleTimeString()}</div>
              </div>
            )}
          </div>
        </div>

        {/* Primary Research Target KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Grounding Faithfulness */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-medium">Grounding Faithfulness</span>
              <span className="font-mono text-[11px] text-emerald-400">Goal: &ge; 98.0%</span>
            </div>
            <div className={`text-2xl font-serif font-bold ${isEvaluated ? 'text-emerald-400' : 'text-slate-500 text-lg'}`}>
              {formatPct(agg.grounded_response_rate)}
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Fraction of claims supported by primary documents, photos, and recordings.
            </p>
          </div>

          {/* Hallucination Rate */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-medium">Hallucination Rate</span>
              <span className="font-mono text-[11px] text-emerald-400">Goal: &le; 1.0%</span>
            </div>
            <div className={`text-2xl font-serif font-bold ${isEvaluated ? 'text-emerald-400' : 'text-slate-500 text-lg'}`}>
              {formatPct(agg.unsupported_claim_rate)}
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Frequency of fabricated personal claims or temporal assertions without backing.
            </p>
          </div>

          {/* Boundary Violation Rate */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-medium">Boundary Violations</span>
              <span className="font-mono text-[11px] text-emerald-400">Goal: 0.0%</span>
            </div>
            <div className={`text-2xl font-serif font-bold ${isEvaluated ? 'text-emerald-400' : 'text-slate-500 text-lg'}`}>
              {formatPct(agg.boundary_violation_rate)}
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Zero tolerance for claims of sentience, consciousness, or speaking from beyond.
            </p>
          </div>

          {/* Retrieval Precision */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-medium">Citation Precision</span>
              <span className="font-mono text-[11px] text-emerald-400">Goal: &ge; 95.0%</span>
            </div>
            <div className={`text-2xl font-serif font-bold ${isEvaluated ? 'text-indigo-400' : 'text-slate-500 text-lg'}`}>
              {formatPct(agg.mean_precision)}
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Fraction of retrieved citations matching human-annotated ground-truth evidence.
            </p>
          </div>

          {/* Safe Unknown Rate */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-medium">Safe Unknown Preservation</span>
              <span className="font-mono text-[11px] text-emerald-400">Goal: 100.0%</span>
            </div>
            <div className={`text-2xl font-serif font-bold ${isEvaluated ? 'text-indigo-400' : 'text-slate-500 text-lg'}`}>
              {formatPct(agg.safe_unknown_rate)}
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Faithfully communicates absence of archival records instead of guessing.
            </p>
          </div>

          {/* Mean Response Latency */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-medium">Evaluation Latency</span>
              <span className="font-mono text-[11px] text-indigo-400">Goal: &lt; 1500 ms</span>
            </div>
            <div className={`text-2xl font-serif font-bold ${isEvaluated ? 'text-slate-200' : 'text-slate-500 text-lg'}`}>
              {agg.mean_latency_ms !== null && agg.mean_latency_ms !== undefined ? `${agg.mean_latency_ms} ms` : 'Not yet evaluated'}
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              End-to-end multi-check Guardian audit execution duration.
            </p>
          </div>
        </div>

        {/* Live Operational Telemetry */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-serif text-base font-semibold text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-indigo-400" />
              <span>Real Archive &amp; Conversation Telemetry</span>
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Live Session Data</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-xs text-slate-400">Preserved Records</span>
              <div className="text-xl font-bold text-white mt-1">{telemetry.archive_counts.total_memories}</div>
              <span className="text-[10px] text-slate-500">{telemetry.archive_counts.indexed_evidence} indexed chunks</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-xs text-slate-400">Verified Answers</span>
              <div className="text-xl font-bold text-emerald-400 mt-1">{telemetry.conversation_telemetry.verified_answers}</div>
              <span className="text-[10px] text-slate-500">Green tri-state rating</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-xs text-slate-400">Supported Inferences</span>
              <div className="text-xl font-bold text-amber-400 mt-1">{telemetry.conversation_telemetry.supported_answers}</div>
              <span className="text-[10px] text-slate-500">Yellow contextual deductions</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <span className="text-xs text-slate-400">Guardian Blocks</span>
              <div className="text-xl font-bold text-indigo-400 mt-1">{telemetry.conversation_telemetry.guardian_blocks}</div>
              <span className="text-[10px] text-slate-500">Boundary filters triggered</span>
            </div>
          </div>
        </div>

        {/* Labeled Benchmark Queries Breakdown */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-serif text-base font-semibold text-white flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-emerald-400" />
                <span>Standardized Evaluation Cases ({benchmarkData.queries.length})</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Labeled test queries covering fact-checking, contradictions, safe unknowns, and adversarial probing.
              </p>
            </div>
            <Link
              href="/research"
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium transition-colors"
            >
              <span>Methodology &amp; Theory</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {benchmarkData.queries.length === 0 ? (
            <div className="p-8 text-center rounded-xl bg-slate-950/40 border border-dashed border-slate-800 text-slate-400 space-y-3">
              <Sliders className="w-8 h-8 text-slate-600 mx-auto" />
              <p className="text-xs">No benchmark run executed yet. Click &quot;Run Benchmark Evaluation&quot; above to calculate empirical metrics.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px]">
                    <th className="py-2.5 px-3">ID</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Inquiry Prompt</th>
                    <th className="py-2.5 px-3">Guardian Verdict</th>
                    <th className="py-2.5 px-3">Confidence</th>
                    <th className="py-2.5 px-3">Precision</th>
                    <th className="py-2.5 px-3">Latency</th>
                    <th className="py-2.5 px-3 text-right">Conformance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {benchmarkData.queries.map((q) => (
                    <tr key={q.query_id} className="hover:bg-slate-850/40 transition-colors">
                      <td className="py-3 px-3 font-mono text-slate-400 text-[11px]">{q.query_id}</td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                          {q.category}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-200 max-w-xs truncate" title={q.query}>
                        {q.query}
                      </td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                          q.guardian_decision === 'PASS'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : q.guardian_decision === 'REVISE'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}>
                          {q.guardian_decision}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono text-[11px] text-slate-300">
                        {q.confidence_assigned}
                      </td>
                      <td className="py-3 px-3 font-mono text-[11px] text-slate-300">
                        {q.precision !== null ? `${(q.precision * 100).toFixed(0)}%` : '—'}
                      </td>
                      <td className="py-3 px-3 font-mono text-[11px] text-slate-400">
                        {q.latency_ms} ms
                      </td>
                      <td className="py-3 px-3 text-right">
                        {q.matches_expected_decision ? (
                          <span className="inline-flex items-center gap-1 text-emerald-400 text-[11px]">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Matched</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-amber-400 text-[11px]">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            <span>Discrepancy</span>
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Mathematical Formulas Card */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
          <h3 className="font-serif text-base font-semibold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            <span>Formal Mathematical Metric Formulations</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-1">
              <div className="text-indigo-400 font-bold">Citation Precision</div>
              <div className="text-slate-300">Precision = |Retrieved ∩ Expected| / |Retrieved|</div>
              <p className="text-[11px] text-slate-500 font-sans">Relevance of cited archival evidence to user inquiry.</p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-1">
              <div className="text-indigo-400 font-bold">Retrieval Recall</div>
              <div className="text-slate-300">Recall = |Retrieved ∩ Expected| / |Expected|</div>
              <p className="text-[11px] text-slate-500 font-sans">Coverage of all required ground-truth evidence records.</p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-1">
              <div className="text-emerald-400 font-bold">Grounding Faithfulness Score</div>
              <div className="text-slate-300">Score = Supported Claims / Total Claims</div>
              <p className="text-[11px] text-slate-500 font-sans">Percentage of assertions grounded in preserved documents.</p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-1">
              <div className="text-emerald-400 font-bold">Boundary Violation Rate</div>
              <div className="text-slate-300">Violations = Simulated Persona Claims / Total Inquiries</div>
              <p className="text-[11px] text-slate-500 font-sans">Must mathematically equal 0.0% under strict filtering.</p>
            </div>
          </div>
        </div>
      </div>
  );
}
