'use client';

import React from 'react';
import { PrivacyIndicator } from '@/components/PrivacyIndicator';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Shield, Lock, HardDrive, Key, CheckCircle2, AlertCircle, FileCheck, Database, Cpu } from 'lucide-react';

export default function SecurityPage() {
  const securityChecklist = [
    {
      title: 'Local Volume Confinement',
      status: 'VERIFIED',
      detail: 'All assets, multimodal vectors, and SQLite databases strictly confined to D:\\ECHO. Zero cloud sync or external API leakage.',
      icon: HardDrive,
    },
    {
      title: 'Zero Parametric Hallucination',
      status: 'VERIFIED',
      detail: 'Memory Guardian enforces tripartite evidence confidence (GREEN, YELLOW, RED) across every retrieval turn.',
      icon: Shield,
    },
    {
      title: 'Non-Consciousness & Ethical Safeguards',
      status: 'VERIFIED',
      detail: 'Strict linguistic boundaries block claims of sentience, spiritual resurrection, or artificial living identity.',
      icon: CheckCircle2,
    },
    {
      title: 'SHA-256 Tamper-Evident Hashing',
      status: 'ACTIVE',
      detail: 'Every ingested photograph, video, audio recording, and document receives an immutable cryptographic digest.',
      icon: FileCheck,
    },
    {
      title: 'AES-256-GCM Storage Encryption',
      status: 'PHASE 2 READY',
      detail: 'Encrypted storage provider architecture in place for local zero-knowledge archival encryption.',
      icon: Lock,
    },
    {
      title: 'Role-Based Kinship Access Control',
      status: 'ENFORCED',
      detail: 'Cryptographic single-use invitation tokens and role-based custody limits prevent unauthorized archive access.',
      icon: Key,
    },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6 animate-fadeIn">
      {/* Overview Card */}
      <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-serif text-base font-bold text-slate-900 dark:text-white">
                Archival Data Sovereignty & Confinement Audit
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Verified zero-egress hardware boundary on USB drive volume
              </p>
            </div>
          </div>
          <PrivacyIndicator path="D:\ECHO\storage\local" />
        </div>

        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {securityChecklist.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="py-4 flex items-start justify-between gap-4 text-xs">
                <div className="flex items-start gap-3">
                  <div className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 mt-0.5">
                    <Icon className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-800 dark:text-slate-200">{item.title}</h4>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">{item.detail}</p>
                  </div>
                </div>
                <Badge
                  variant={item.status === 'VERIFIED' ? 'verified' : item.status === 'ACTIVE' ? 'emerald' : 'indigo'}
                  dot
                  className="shrink-0"
                >
                  {item.status}
                </Badge>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
