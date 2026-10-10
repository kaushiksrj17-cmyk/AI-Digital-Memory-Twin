'use client';

import React from 'react';
import Link from 'next/link';
import { EthicalBanner } from '@/components/EthicalBanner';
import { Button } from '@/components/ui/Button';
import {
  GraduationCap,
  BookOpen,
  CheckCircle2,
  Shield,
  Layers,
  BarChart3,
  HardDrive,
  ArrowRight
} from 'lucide-react';

export default function ResearchPage() {
  const researchObjectives = [
    'Preserving Heterogeneous Personal Memories across diverse modalities',
    'Processing and aligning photographs, recordings, letters, and certificates',
    'Connecting memories with people, events, and places in a knowledge graph',
    'Retrieving relevant evidence via hybrid vector-keyword semantic retrieval',
    'Generating evidence-grounded responses without parametric hallucinations',
    'Expressing confidence transparently (GREEN, YELLOW, RED)',
    'Showing source provenance citations with document folio numbers',
    'Detecting and suppressing unsupported claims through dual-pass guardian filters',
    'Protecting private personal data strictly on isolated local volumes (D:\\ECHO)',
    'Providing an ethical, non-deceptive memorial experience honoring authentic memory',
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8 animate-fadeIn">
      <EthicalBanner variant="card" />

      {/* Paper Header Card */}
      <div className="p-8 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-semibold">
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Research Paper Title</span>
          </div>

          <Link href="/research-dashboard">
            <Button variant="primary" size="sm">
              <BarChart3 className="w-3.5 h-3.5 mr-1.5" />
              <span>Open Empirical Benchmark Dashboard</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </Link>
        </div>

        <h2 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white leading-snug">
          Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation
        </h2>

        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed max-w-3xl">
          This research presents an architectural paradigm for digital memory preservation that repudiates consciousness simulation and persona reanimation in favor of evidence-anchored retrieval, verifiable confidence calibration, and strict storage isolation.
        </p>
      </div>

      {/* Ten Research Objectives */}
      <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-4">
        <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
          <span>Ten Core Research Objectives</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {researchObjectives.map((obj, i) => (
            <div key={i} className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-100 dark:border-slate-800 text-xs">
              <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold shrink-0">#{i + 1}</span>
              <span className="text-slate-700 dark:text-slate-300">{obj}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Evaluation Metrics */}
      <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-4">
        <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
          <span>Target Benchmark Metrics</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60">
            <span className="text-xs text-slate-500 dark:text-slate-400">Grounding Faithfulness</span>
            <div className="text-2xl font-serif font-bold text-emerald-600 dark:text-emerald-400 mt-1">&ge; 98.0%</div>
            <p className="text-[11px] text-slate-500 mt-1">Verified against primary evidence text</p>
          </div>

          <div className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60">
            <span className="text-xs text-slate-500 dark:text-slate-400">Hallucination Rate</span>
            <div className="text-2xl font-serif font-bold text-emerald-600 dark:text-emerald-400 mt-1">&le; 1.0%</div>
            <p className="text-[11px] text-slate-500 mt-1">Ungrounded factual claims suppressed</p>
          </div>

          <div className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60">
            <span className="text-xs text-slate-500 dark:text-slate-400">Boundary Violations</span>
            <div className="text-2xl font-serif font-bold text-emerald-600 dark:text-emerald-400 mt-1">0.0%</div>
            <p className="text-[11px] text-slate-500 mt-1">Zero consciousness simulation permitted</p>
          </div>
        </div>
      </div>
    </div>
  );
}
