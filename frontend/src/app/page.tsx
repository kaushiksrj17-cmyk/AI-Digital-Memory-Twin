'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  BookOpen,
  MessageSquare,
  Box,
  GraduationCap,
  Shield,
  HardDrive,
  Heart,
  ArrowRight,
  ShieldCheck,
  Lock,
  Calendar,
  Mic,
  Dna,
  Share2,
  FileCheck,
  ChevronDown,
  CheckCircle2,
  AlertCircle,
  Archive
} from 'lucide-react';
import { AIGeneratedBadge } from '@/components/AIGeneratedBadge';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'vault' | 'companion' | 'timeline' | 'room'>('vault');
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const toggleFaq = (idx: number) => {
    setOpenFaq(openFaq === idx ? null : idx);
  };

  const faqs = [
    {
      q: 'Does ECHO attempt to recreate human consciousness or identity?',
      a: 'No. ECHO explicitly rejects and blocks any simulation of consciousness, sentience, or resurrection. It is an evidence-grounded archival twin: every response is strictly derived from preserved letters, oral histories, photographs, and family records with visible source citations.',
    },
    {
      q: 'Where are my photographs, audio recordings, and memories stored?',
      a: 'All files, vector embeddings, and personal data are strictly confined to private, sovereign storage on your host machine (D:\\ECHO\\storage). Nothing is uploaded to public AI training clouds or shared with third parties.',
    },
    {
      q: 'How does the Memory Guardian prevent AI confabulation (hallucination)?',
      a: 'ECHO enforces an 18-point verification pipeline. When asked about events with no archival evidence, the system refuses to guess and delivers an honest, safe unknown response: "I do not have enough information in the preserved archive to answer that question."',
    },
    {
      q: 'How is memorial voice cloning governed?',
      a: 'Memorial speech synthesis requires explicit, verified legal kinship consent. If consent is ever revoked by the family guardian, voice synthesis capabilities are immediately terminated with zero latency. Every synthesized audio file embeds an immutable digital watermark.',
    },
  ];

  return (
    <div className="space-y-24 py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* 1. Hero Section */}
      <section className="relative text-center pt-8 pb-12 sm:pt-16 sm:pb-20 overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-500/10 dark:bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800/60 text-indigo-700 dark:text-indigo-300 text-xs font-medium shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
            <span>Evidence-Grounded Memorial Preservation &bull; Research Grade</span>
          </div>

          <h1 className="font-serif text-4xl sm:text-6xl font-bold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
            Keep the stories that make us who we are.
          </h1>

          <p className="text-base sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto font-sans leading-relaxed">
            Preserve meaningful memories in a private, organized, evidence-grounded digital archive — designed to help families revisit the stories, voices, and moments that matter.
          </p>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-3 sm:gap-4">
            <Link href="/dashboard">
              <Button size="lg" variant="primary" iconRight={<ArrowRight className="w-4 h-4" />}>
                Enter Memorial Sanctuary
              </Button>
            </Link>
            <Link href="/conversation">
              <Button size="lg" variant="outline" iconLeft={<MessageSquare className="w-4 h-4 text-indigo-500" />}>
                Test AI Companion
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="ghost" iconLeft={<Lock className="w-4 h-4 text-slate-400" />}>
                Guardian Sign In
              </Button>
            </Link>
          </div>

          <div className="pt-6 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Zero Confabulation Guarantee</span>
            </div>
            <div className="flex items-center gap-1.5">
              <HardDrive className="w-4 h-4 text-indigo-500" />
              <span>Sovereign Storage: D:\ECHO</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Heart className="w-4 h-4 text-rose-500" />
              <span>Strict Kinship Consent</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Interactive Feature Previews */}
      <section id="features" className="space-y-8">
        <div className="text-center space-y-2 max-w-2xl mx-auto">
          <h2 className="font-serif text-2xl sm:text-4xl font-bold text-slate-900 dark:text-white">
            Four Pillars of Digital Memory Preservation
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400">
            Explore the core interactive environments that bring preserved archival records to life.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-2 p-1.5 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 max-w-2xl mx-auto">
          <button
            onClick={() => setActiveTab('vault')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              activeTab === 'vault'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200 dark:border-slate-700'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Archive className="w-3.5 h-3.5" />
            <span>Memory Vault</span>
          </button>
          <button
            onClick={() => setActiveTab('companion')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              activeTab === 'companion'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200 dark:border-slate-700'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>AI Companion</span>
          </button>
          <button
            onClick={() => setActiveTab('timeline')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              activeTab === 'timeline'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200 dark:border-slate-700'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Life Timeline</span>
          </button>
          <button
            onClick={() => setActiveTab('room')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              activeTab === 'room'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200 dark:border-slate-700'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Box className="w-3.5 h-3.5" />
            <span>3D Memory Room</span>
          </button>
        </div>

        {/* Tab Content Display */}
        <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-6 sm:p-10 shadow-lg">
          {activeTab === 'vault' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div className="space-y-4">
                <Badge variant="indigo">Cryptographic Archival Vault</Badge>
                <h3 className="font-serif text-2xl font-bold text-slate-900 dark:text-white">
                  Ingest, organize, and verify lifetime artifacts
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  Every photograph, handwritten letter, audio tape, and birth registry is indexed with an immutable SHA-256 cryptographic digest. Provenance chains ensure that every digital representation maps back to tangible family evidence.
                </p>
                <div className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Multimodal format support: JPEG, PNG, MP3, WAV, PDF, DOCX, TXT</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Optical character recognition (OCR) & speech transcription</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Zero cloud leak: all bytes remain sealed on local host</span>
                  </div>
                </div>
                <div className="pt-2">
                  <Link href="/memory-vault">
                    <Button variant="primary" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                      Explore Memory Vault
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Visual Card Mockup */}
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-3 font-sans">
                <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
                  <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">Vault Asset: graduation_1968.jpg</span>
                  <Badge variant="verified" size="sm" dot>VERIFIED SHA-256</Badge>
                </div>
                <div className="h-32 rounded-xl bg-gradient-to-br from-indigo-950/40 to-slate-900 flex items-center justify-center border border-slate-200 dark:border-slate-800 text-slate-400 text-xs">
                  [ Archival Photograph Preview &bull; Cambridge University 1968 ]
                </div>
                <div className="text-[11px] text-slate-500 space-y-1 font-mono">
                  <p>Hash: 7a8f9c2d1b...e4a90</p>
                  <p>Source: Physical Photo Album &bull; Verified by Family Guardian</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'companion' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div className="space-y-4">
                <Badge variant="indigo">Evidence-Grounded RAG Dialogue</Badge>
                <h3 className="font-serif text-2xl font-bold text-slate-900 dark:text-white">
                  Conversations grounded strictly in preserved evidence
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  Ask questions about family history, career achievements, or cherished anecdotes. The AI companion quotes verbatim archival records, displays citation badges, and honestly declines questions where no evidence exists.
                </p>
                <div className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Tri-state confidence: Green (Verified), Yellow (Inference), Red (Unknown)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Memory Guardian 18-point boundary filter blocks confabulation</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Transparent provenance badges for every factual claim</span>
                  </div>
                </div>
                <div className="pt-2">
                  <Link href="/conversation">
                    <Button variant="primary" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                      Open Conversation Studio
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Chat snippet mockup */}
              <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-3 font-sans text-xs">
                <div className="p-3 rounded-xl bg-slate-200/60 dark:bg-slate-800 text-slate-800 dark:text-slate-200 max-w-xs">
                  &ldquo;Where did Eleanor spend the summer of 1974?&rdquo;
                </div>
                <div className="p-3.5 rounded-xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200/60 dark:border-indigo-800/60 text-slate-800 dark:text-slate-200 space-y-2">
                  <p>
                    &ldquo;According to her handwritten travel journal, Eleanor spent August 1974 sailing on Lake Windermere with her brother Thomas.&rdquo;
                  </p>
                  <div className="flex items-center gap-2 pt-1 border-t border-indigo-200/40 dark:border-indigo-800/40 text-[10px]">
                    <Badge variant="verified" size="sm" dot>VERIFIED</Badge>
                    <span className="text-slate-500">Source: Folio 14, 1974 Diary</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'timeline' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div className="space-y-4">
                <Badge variant="amber">Chronological Biography</Badge>
                <h3 className="font-serif text-2xl font-bold text-slate-900 dark:text-white">
                  A structured chronological tapestry of a life lived
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  Navigate milestone events, journeys, career chapters, and family moments across decades. Conflicting dates from disparate records are preserved transparently with dispute flags rather than silently smoothed over.
                </p>
                <div className="pt-2">
                  <Link href="/timeline">
                    <Button variant="primary" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                      Explore Life Timeline
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                  <div>
                    <span className="text-[10px] font-mono text-indigo-500 dark:text-indigo-400">June 1968</span>
                    <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-100">Graduation from Trinity College</h4>
                    <p className="text-[11px] text-slate-500">Awarded honors degree in English Literature.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                  <div>
                    <span className="text-[10px] font-mono text-amber-500 dark:text-amber-400">August 1974</span>
                    <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-100">Expedition to Lake Windermere</h4>
                    <p className="text-[11px] text-slate-500">Handwritten journal logs first boat voyage.</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'room' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div className="space-y-4">
                <Badge variant="indigo">Three.js Spatial Sanctuary</Badge>
                <h3 className="font-serif text-2xl font-bold text-slate-900 dark:text-white">
                  A calm, 3D interactive sanctuary for reflection
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  Step into a spatial memory room rendered in WebGL. Ambient lighting, memorial framed portraits, archival book stands, and spatial audio create an immersive yet emotionally respectful space.
                </p>
                <div className="pt-2">
                  <Link href="/memory-room">
                    <Button variant="primary" size="sm" iconRight={<ArrowRight className="w-3.5 h-3.5" />}>
                      Enter 3D Memory Room
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="h-48 rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-950 border border-slate-200 dark:border-slate-800 flex flex-col items-center justify-center p-6 text-center text-xs text-slate-300 space-y-2">
                <Box className="w-8 h-8 text-indigo-400" />
                <p className="font-medium">Three.js 3D Spatial Canvas</p>
                <span className="text-[10px] text-slate-500">Interactive objects &bull; Ambient room lighting &bull; Reduced motion support</span>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* 3. Ethical AI & Non-Deception Manifesto */}
      <section id="ethics" className="p-8 sm:p-12 rounded-3xl border border-slate-200 dark:border-slate-800 bg-gradient-to-br from-slate-100/80 via-white to-slate-50 dark:from-slate-900/60 dark:via-slate-950 dark:to-slate-900 space-y-6">
        <div className="max-w-3xl space-y-3">
          <Badge variant="amber">Ethical Manifesto & Non-Deceptive AI</Badge>
          <h2 className="font-serif text-2xl sm:text-4xl font-bold text-slate-900 dark:text-white">
            Rooted in respect. Guarded against confabulation.
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            ECHO was designed from the ground up to respect human grief and memory. We do not exploit emotion with false claims of digital resurrection.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-500">
              <Shield className="w-4 h-4" />
            </div>
            <h4 className="font-semibold text-xs sm:text-sm text-slate-800 dark:text-slate-100">
              No Sentience Claims
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              ECHO will never claim to be the actual deceased person, simulate consciousness, or claim to possess feelings or thoughts.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h4 className="font-semibold text-xs sm:text-sm text-slate-800 dark:text-slate-100">
              Honest Safe Unknowns
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              If an inquiry touches upon unrecorded events, the AI explicitly states that no evidence is preserved rather than confabulating.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-500">
              <Lock className="w-4 h-4" />
            </div>
            <h4 className="font-semibold text-xs sm:text-sm text-slate-800 dark:text-slate-100">
              Instant Kinship Revocation
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Family members retain perpetual sovereignty. Voice synthesis and media access can be revoked instantly at any time.
            </p>
          </div>
        </div>
      </section>

      {/* 4. How It Works (4 Steps) */}
      <section id="how-it-works" className="space-y-8">
        <div className="text-center space-y-2 max-w-2xl mx-auto">
          <Badge variant="indigo">Preservation Pipeline</Badge>
          <h2 className="font-serif text-2xl sm:text-4xl font-bold text-slate-900 dark:text-white">
            How ECHO Preserves Your Heritage
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/10 text-indigo-500 flex items-center justify-center font-bold text-xs">
              01
            </div>
            <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-white">Ingest Records</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Upload photos, letters, diaries, oral recordings, and legal documents. Checksums ensure absolute data integrity.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/10 text-indigo-500 flex items-center justify-center font-bold text-xs">
              02
            </div>
            <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-white">Structure & Graph</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              AI maps events to a chronological timeline, extracts key relationships, and indexes Memory DNA value traits.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/10 text-indigo-500 flex items-center justify-center font-bold text-xs">
              03
            </div>
            <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-white">Guardian Audit</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Every factual assertion undergoes an 18-point verification filter to prevent distortion, anachronism, or confabulation.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/10 text-indigo-500 flex items-center justify-center font-bold text-xs">
              04
            </div>
            <h3 className="font-serif text-base font-semibold text-slate-900 dark:text-white">Revisit & Share</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Engage in evidence-grounded dialogue, listen to authorized voice clips, or invite family members to contribute.
            </p>
          </div>
        </div>
      </section>

      {/* 5. Frequently Asked Questions */}
      <section id="faq" className="space-y-8 max-w-3xl mx-auto">
        <div className="text-center space-y-2">
          <Badge variant="neutral">Clear Answers</Badge>
          <h2 className="font-serif text-2xl sm:text-4xl font-bold text-slate-900 dark:text-white">
            Frequently Asked Questions
          </h2>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/70 overflow-hidden"
            >
              <button
                onClick={() => toggleFaq(idx)}
                className="w-full flex items-center justify-between p-4 sm:p-5 text-left text-xs sm:text-sm font-semibold text-slate-900 dark:text-slate-100 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              >
                <span>{faq.q}</span>
                <ChevronDown
                  className={`w-4 h-4 text-slate-400 transition-transform ${
                    openFaq === idx ? 'rotate-180 text-indigo-500' : ''
                  }`}
                />
              </button>
              {openFaq === idx && (
                <div className="px-4 pb-5 sm:px-5 text-xs text-slate-600 dark:text-slate-400 leading-relaxed border-t border-slate-100 dark:border-slate-800/60 pt-3">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 6. Bottom Call to Action */}
      <section className="rounded-3xl bg-gradient-to-br from-indigo-900 via-indigo-950 to-slate-950 border border-indigo-800/40 p-8 sm:p-14 text-center text-white space-y-6 relative overflow-hidden shadow-2xl">
        <div className="relative z-10 max-w-2xl mx-auto space-y-4">
          <h2 className="font-serif text-3xl sm:text-5xl font-bold tracking-tight">
            Begin Preserving Your Family Legacy Today
          </h2>
          <p className="text-xs sm:text-sm text-indigo-200 leading-relaxed">
            Open the private sanctuary, ingest your first archival document, and experience evidence-grounded preservation.
          </p>
          <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
            <Link href="/dashboard">
              <Button size="lg" variant="primary" iconRight={<ArrowRight className="w-4 h-4" />}>
                Enter Sanctuary
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="secondary" iconLeft={<Lock className="w-4 h-4" />}>
                Guardian Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
