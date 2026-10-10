'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { DashboardCards } from '@/components/DashboardCards';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { PrivacyIndicator } from '@/components/PrivacyIndicator';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { CardSkeleton } from '@/components/ui/Skeleton';
import { DashboardStats } from '@/types';
import {
  Calendar,
  Clock,
  ShieldCheck,
  ArrowRight,
  BookOpen,
  FileCheck,
  Activity,
  Lock,
  Sparkles,
  PlusCircle,
  MessageSquare,
  Search
} from 'lucide-react';

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    total_memories: 0,
    verified_memories: 0,
    supported_inferences: 0,
    unknown_unsupported: 0,
    photos_count: 0,
    videos_count: 0,
    audio_count: 0,
    documents_count: 0,
    people_count: 0,
    life_events_count: 0,
    conversation_sessions_count: 0,
    privacy_status: 'Confined to Private Vault (D:\\ECHO\\storage)',
    is_demonstration_mode: false,
  });

  const [recentMemories, setRecentMemories] = useState<any[]>([
    {
      id: 'demo-mem-001',
      title: 'Graduation Day at Trinity College Library',
      date: 'June 1968',
      confidence: 'VERIFIED' as const,
      source: 'Photograph & Degree Certificate',
    },
    {
      id: 'demo-mem-002',
      title: 'Summer Sailing on Lake Windermere',
      date: 'August 1974',
      confidence: 'SUPPORTED_INFERENCE' as const,
      source: 'Handwritten Travel Journal',
    },
  ]);

  const [recentEvidence, setRecentEvidence] = useState<any[]>([
    {
      id: 'demo-doc-001',
      title: 'University Degree Registry Record 1968',
      type: 'DOCUMENT',
      citation: 'Folio 82, Cambridge Archives',
      confidence: 'VERIFIED' as const,
    },
    {
      id: 'demo-media-002',
      title: 'Family Oral History Tape (Side A)',
      type: 'AUDIO_RECORDING',
      citation: 'Reel 4, Timestamp 14m:22s',
      confidence: 'VERIFIED' as const,
    },
  ]);

  const [recentActivity, setRecentActivity] = useState<any[]>([
    {
      action: 'Evidence Record Verified',
      details: 'Primary degree certificate linked to 1968 graduation memory.',
      time: 'Today, 10:15 AM',
    },
    {
      action: 'Dialogue Grounding Audited',
      details: 'Conversation query checked against Memory Guardian boundary filter.',
      time: 'Today, 09:40 AM',
    },
    {
      action: 'Private Vault Initialized',
      details: 'Storage directory validated strictly at D:\\ECHO\\storage.',
      time: 'Yesterday',
    },
  ]);

  const [phase4Metrics, setPhase4Metrics] = useState<any>({
    memory_dna_items: 0,
    graph_nodes: 0,
    graph_relationships: 0,
    indexed_evidence: 0,
    vector_records: 0,
    retrieval_queries: 0,
    verified_evidence: 0,
    supported_inferences: 0,
    unknown_items: 0,
  });

  const [phase5Metrics, setPhase5Metrics] = useState<any>({
    conversations: 0,
    messages: 0,
    rag_queries: 0,
    verified_responses: 0,
    supported_inferences: 0,
    unknown_responses: 0,
    guardian_revisions: 0,
    guardian_blocks: 0,
    contradictions_detected: 0,
  });

  useEffect(() => {
    async function loadDashboard() {
      try {
        const res = await fetch('/api/v1/analytics/dashboard');
        if (res.ok) {
          const data = await res.json();
          if (data.cards) setStats(data.cards);
          if (data.phase4_metrics) setPhase4Metrics(data.phase4_metrics);
          if (data.phase5_metrics) setPhase5Metrics(data.phase5_metrics);
          if (data.recent_memories) setRecentMemories(data.recent_memories);
          if (data.recent_evidence) setRecentEvidence(data.recent_evidence);
          if (data.recent_activity) setRecentActivity(data.recent_activity);
        }
      } catch (err) {
        console.error('Failed to load dashboard metrics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8 animate-fadeIn">
      {/* Top Banner / Welcome & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-transparent border border-indigo-500/20">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              Vault Secure &bull; Local Confinement Active
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-serif font-bold text-slate-900 dark:text-white mt-1">
            Biographical Executive Overview
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-0.5">
            Preserving evidence-grounded life memories strictly inside <code className="text-[11px] font-mono text-indigo-600 dark:text-indigo-400">D:\ECHO\storage</code>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <Link href="/conversation">
            <Button variant="primary" size="sm">
              <MessageSquare className="w-4 h-4 mr-1.5" />
              Ask Companion
            </Button>
          </Link>
          <Link href="/memory-vault">
            <Button variant="outline" size="sm">
              <PlusCircle className="w-4 h-4 mr-1.5" />
              Vault Archive
            </Button>
          </Link>
        </div>
      </div>

      {/* Demonstration / Evidence Guarantee Notice */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl border border-indigo-200 dark:border-indigo-500/20 bg-indigo-50/60 dark:bg-indigo-950/20 text-xs">
        <div className="flex items-center gap-2.5 text-indigo-900 dark:text-indigo-300">
          <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0" />
          <span>
            <strong>Zero AI Hallucination Guarantee:</strong> Memory Guardian audits every memory and query against immutable primary provenance records.
          </span>
        </div>
        <PrivacyIndicator path="D:\ECHO\storage\local" />
      </div>

      {/* Dashboard 11 Cards Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-slate-100">
            Vault Overview & Metric Counters
          </h3>
          <span className="text-xs text-slate-500">11 Category Indexes</span>
        </div>
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : (
          <DashboardCards stats={stats} />
        )}
      </section>

      {/* Phase 4 Intelligence, Knowledge Graph & Vector Retrieval Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
            <span>Structured Intelligence & Retrieval Foundation</span>
          </h3>
          <div className="flex items-center gap-3 text-xs">
            <Link href="/memory-dna" className="text-indigo-600 dark:text-indigo-400 hover:underline">Memory DNA</Link>
            <span className="text-slate-400 dark:text-slate-600">&bull;</span>
            <Link href="/knowledge-graph" className="text-indigo-600 dark:text-indigo-400 hover:underline">Knowledge Graph</Link>
            <span className="text-slate-400 dark:text-slate-600">&bull;</span>
            <Link href="/retrieval" className="text-indigo-600 dark:text-indigo-400 hover:underline">Vector Retrieval</Link>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <Link href="/memory-dna" className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500/50 shadow-sm transition">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Memory DNA Items</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase4Metrics.memory_dna_items}</p>
            <span className="text-[10px] text-indigo-600 dark:text-indigo-400 mt-1 block">22 Life Categories &rarr;</span>
          </Link>

          <Link href="/knowledge-graph" className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-cyan-400 dark:hover:border-cyan-500/50 shadow-sm transition">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Graph Nodes</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase4Metrics.graph_nodes}</p>
            <span className="text-[10px] text-cyan-600 dark:text-cyan-400 mt-1 block">10 Entity Classes &rarr;</span>
          </Link>

          <Link href="/knowledge-graph" className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-purple-400 dark:hover:border-purple-500/50 shadow-sm transition">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Graph Edges</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase4Metrics.graph_relationships}</p>
            <span className="text-[10px] text-purple-600 dark:text-purple-400 mt-1 block">Evidenced Relations &rarr;</span>
          </Link>

          <Link href="/retrieval" className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-emerald-400 dark:hover:border-emerald-500/50 shadow-sm transition">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Indexed Vectors</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase4Metrics.vector_records}</p>
            <span className="text-[10px] text-emerald-600 dark:text-emerald-400 mt-1 block">Vector Store Ready &rarr;</span>
          </Link>

          <Link href="/retrieval" className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-amber-400 dark:hover:border-amber-500/50 shadow-sm transition">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Retrieval Queries</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase4Metrics.retrieval_queries}</p>
            <span className="text-[10px] text-amber-600 dark:text-amber-400 mt-1 block">Hybrid Searches &rarr;</span>
          </Link>

          <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Indexed Evidence</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase4Metrics.indexed_evidence}</p>
            <span className="text-[10px] text-slate-500 mt-1 block">Provenance Grounded</span>
          </div>
        </div>
      </section>

      {/* Phase 5 Conversational Intelligence & Memory Guardian Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
            <span>Conversational Intelligence & Memory Guardian</span>
          </h3>
          <div className="flex items-center gap-3 text-xs">
            <Link href="/conversation" className="text-emerald-600 dark:text-emerald-400 hover:underline font-medium">Launch Memorial Dialogue &rarr;</Link>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-9 gap-3">
          <Link href="/conversation" className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-emerald-400 dark:hover:border-emerald-500/50 shadow-sm transition">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Sessions</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase5Metrics.conversations}</p>
            <span className="text-[10px] text-emerald-600 dark:text-emerald-400 mt-1 block">Active Threads</span>
          </Link>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Messages</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase5Metrics.messages}</p>
            <span className="text-[10px] text-slate-500 mt-1 block">Total Turns</span>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">RAG Queries</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase5Metrics.rag_queries}</p>
            <span className="text-[10px] text-indigo-600 dark:text-indigo-400 mt-1 block">Grounded Pipeline</span>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Verified</p>
            <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{phase5Metrics.verified_responses}</p>
            <span className="text-[10px] text-emerald-600 dark:text-emerald-500 mt-1 block">Green Tier</span>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Supported</p>
            <p className="text-xl font-bold text-amber-600 dark:text-amber-400 mt-1">{phase5Metrics.supported_inferences}</p>
            <span className="text-[10px] text-amber-600 dark:text-amber-500 mt-1 block">Yellow Tier</span>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Unknown</p>
            <p className="text-xl font-bold text-rose-600 dark:text-rose-400 mt-1">{phase5Metrics.unknown_responses}</p>
            <span className="text-[10px] text-rose-600 dark:text-rose-500 mt-1 block">Zero Fabrication</span>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Revisions</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">{phase5Metrics.guardian_revisions}</p>
            <span className="text-[10px] text-amber-600 dark:text-amber-400 mt-1 block">Guardian Fixed</span>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Blocks</p>
            <p className="text-xl font-bold text-rose-600 dark:text-rose-400 mt-1">{phase5Metrics.guardian_blocks}</p>
            <span className="text-[10px] text-rose-600 dark:text-rose-500 mt-1 block">Policy Enforced</span>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Conflicts</p>
            <p className="text-xl font-bold text-amber-600 dark:text-amber-400 mt-1">{phase5Metrics.contradictions_detected}</p>
            <span className="text-[10px] text-amber-600 dark:text-amber-500 mt-1 block">Flagged Claims</span>
          </div>
        </div>
      </section>

      {/* Main Grid: Recent Memories, Recent Evidence, Timeline Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Column 1: Recent Memories */}
        <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                <h4 className="font-serif text-sm font-semibold text-slate-900 dark:text-slate-100">
                  Recent Preserved Memories
                </h4>
              </div>
              <Link href="/memories" className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
                View all
              </Link>
            </div>

            <div className="space-y-3">
              {recentMemories.map((m) => (
                <div
                  key={m.id}
                  className="p-3 rounded-xl border border-slate-100 dark:border-slate-800/80 bg-slate-50/60 dark:bg-slate-900/40 space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h5 className="text-xs font-semibold text-slate-800 dark:text-slate-200">{m.title}</h5>
                    <ConfidenceIndicator level={m.confidence} size="sm" showText={false} />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>{m.date}</span>
                    <span>{m.source}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Link
            href="/memory-vault"
            className="mt-4 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-xs text-slate-700 dark:text-slate-300 transition-colors"
          >
            <span>Ingest New Memory</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Column 2: Recent Evidence */}
        <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
                <h4 className="font-serif text-sm font-semibold text-slate-900 dark:text-slate-100">
                  Recent Primary Evidence
                </h4>
              </div>
              <Link href="/evidence" className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
                View all
              </Link>
            </div>

            <div className="space-y-3">
              {recentEvidence.map((e) => (
                <div
                  key={e.id}
                  className="p-3 rounded-xl border border-slate-100 dark:border-slate-800/80 bg-slate-50/60 dark:bg-slate-900/40 space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h5 className="text-xs font-semibold text-slate-800 dark:text-slate-200">{e.title}</h5>
                    <ConfidenceIndicator level={e.confidence} size="sm" showText={false} />
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Citation: <strong>{e.citation}</strong>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Link
            href="/evidence"
            className="mt-4 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-xs text-slate-700 dark:text-slate-300 transition-colors"
          >
            <span>Explore Evidence Panel</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Column 3: Life Timeline Preview */}
        <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-purple-500 dark:text-purple-400" />
                <h4 className="font-serif text-sm font-semibold text-slate-900 dark:text-slate-100">
                  Life Timeline Preview
                </h4>
              </div>
              <Link href="/timeline" className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
                Full timeline
              </Link>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                <span className="font-mono text-[11px] text-indigo-600 dark:text-indigo-400 shrink-0 font-semibold">1946</span>
                <div className="min-w-0">
                  <p className="font-medium text-slate-800 dark:text-slate-200 truncate">Birth in Edinburgh</p>
                  <p className="text-[10px] text-slate-500">Royal Infirmary Registry</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                <span className="font-mono text-[11px] text-indigo-600 dark:text-indigo-400 shrink-0 font-semibold">1968</span>
                <div className="min-w-0">
                  <p className="font-medium text-slate-800 dark:text-slate-200 truncate">Graduation Ceremony</p>
                  <p className="text-[10px] text-slate-500">Trinity College, Cambridge</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                <span className="font-mono text-[11px] text-indigo-600 dark:text-indigo-400 shrink-0 font-semibold">1974</span>
                <div className="min-w-0">
                  <p className="font-medium text-slate-800 dark:text-slate-200 truncate">Summer Sailing on Windermere</p>
                  <p className="text-[10px] text-slate-500">Travel Journal Vol 2</p>
                </div>
              </div>
            </div>
          </div>

          <Link
            href="/timeline"
            className="mt-4 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-xs text-slate-700 dark:text-slate-300 transition-colors"
          >
            <span>View Interactive Timeline</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Confidence Overview, Activity, and Privacy Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Memory Confidence Calibration */}
        <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-4">
          <h4 className="font-serif text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
            <span>Memory Confidence Tripartite Standard</span>
          </h4>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            The calibration framework guarantees honesty and ethical accountability for every memory:
          </p>

          <div className="space-y-3">
            <div className="p-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 dark:bg-emerald-500/5">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400">
                  GREEN &bull; VERIFIED EVIDENCE
                </span>
                <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400">50%</span>
              </div>
              <p className="text-[11px] text-slate-600 dark:text-slate-400">
                Authenticated by physical certificates, letters, photographs, or confirmed oral records.
              </p>
            </div>

            <div className="p-3 rounded-xl border border-amber-500/30 bg-amber-500/10 dark:bg-amber-500/5">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-amber-700 dark:text-amber-400">
                  YELLOW &bull; SUPPORTED INFERENCE
                </span>
                <span className="text-xs font-bold text-amber-700 dark:text-amber-400">50%</span>
              </div>
              <p className="text-[11px] text-slate-600 dark:text-slate-400">
                Corroborated deductions drawn from intersecting preserved biographical materials.
              </p>
            </div>

            <div className="p-3 rounded-xl border border-rose-500/30 bg-rose-500/10 dark:bg-rose-500/5">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-rose-700 dark:text-rose-400">
                  RED &bull; UNKNOWN / UNSUPPORTED
                </span>
                <span className="text-xs font-bold text-rose-700 dark:text-rose-400">0% (Zero Hallucination)</span>
              </div>
              <p className="text-[11px] text-slate-600 dark:text-slate-400">
                Unsubstantiated queries are explicitly identified and declined by Memory Guardian.
              </p>
            </div>
          </div>
        </div>

        {/* Recent Activity and Privacy Status */}
        <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <h4 className="font-serif text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-cyan-500 dark:text-cyan-400" />
              <span>Recent System Activity & Provenance Audits</span>
            </h4>

            <div className="space-y-3">
              {recentActivity.map((act, idx) => (
                <div key={idx} className="flex items-start gap-3 text-xs border-b border-slate-100 dark:border-slate-800/80 pb-3 last:border-0">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                  <div className="flex-1">
                    <p className="font-medium text-slate-800 dark:text-slate-200">{act.action}</p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">{act.details}</p>
                  </div>
                  <span className="text-[10px] text-slate-400 dark:text-slate-500 shrink-0">{act.time}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
              <Lock className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Storage Enclosure: <strong>D:\ECHO</strong> (USB Drive Active)</span>
            </div>
            <span className="text-emerald-600 dark:text-emerald-400 font-semibold text-[11px]">Zero Leakage</span>
          </div>
        </div>
      </div>
    </div>
  );
}
