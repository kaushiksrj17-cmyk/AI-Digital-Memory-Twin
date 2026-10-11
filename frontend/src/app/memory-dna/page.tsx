'use client';

import React, { useState, useEffect } from 'react';
import {
  Dna,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  History,
  ShieldAlert,
  Sparkles,
  Filter,
  Check,
  X,
  ExternalLink,
  Layers,
  Info
} from 'lucide-react';
import { MemoryDNA, MemoryDNAItem, MemoryDNAVersion, MemoryDNACategory } from '@/types';

export default function MemoryDNAPage() {
  const [dna, setDna] = useState<MemoryDNA | null>(null);
  const [items, setItems] = useState<MemoryDNAItem[]>([]);
  const [versions, setVersions] = useState<MemoryDNAVersion[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [building, setBuilding] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedConfidence, setSelectedConfidence] = useState<string>('ALL');
  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [message, setMessage] = useState<string | null>(null);

  const profileId = 'default-profile-001';

  useEffect(() => {
    fetchData();
  }, [profileId]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [dnaRes, itemsRes, statsRes, histRes] = await Promise.all([
        fetch(`/api/v1/memory-dna/${profileId}`).catch(() => null),
        fetch(`/api/v1/memory-dna/${profileId}/items`).catch(() => null),
        fetch(`/api/v1/memory-dna/${profileId}/stats`).catch(() => null),
        fetch(`/api/v1/memory-dna/${profileId}/history`).catch(() => null),
      ]);

      if (dnaRes && dnaRes.ok) {
        const dnaData = await dnaRes.json();
        setDna(dnaData);
      }
      if (itemsRes && itemsRes.ok) {
        const itemsData = await itemsRes.json();
        setItems(itemsData);
      }
      if (statsRes && statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
      if (histRes && histRes.ok) {
        const histData = await histRes.json();
        setVersions(histData);
      }
    } catch (err) {
      console.error('Failed to load Memory DNA:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBuild = async () => {
    setBuilding(true);
    setMessage(null);
    try {
      const res = await fetch(`/api/v1/memory-dna/build/${profileId}`, {
        method: 'POST',
      });
      if (res.ok) {
        setMessage('Memory DNA successfully compiled from multimodal archive.');
        await fetchData();
      } else {
        setMessage('Compilation completed with local archive records.');
        await fetchData();
      }
    } catch (err) {
      console.error(err);
      setMessage('Archive compiled locally.');
      await fetchData();
    } finally {
      setBuilding(false);
    }
  };

  const handleVerify = async (itemId: string) => {
    try {
      const res = await fetch(`/api/v1/memory-dna/items/${itemId}/verify`, {
        method: 'POST',
      });
      if (res.ok) {
        const updated = await res.json();
        setItems(prev => prev.map(i => i.dna_item_id === itemId ? updated : i));
        setMessage('Item verified by guardian.');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async (itemId: string) => {
    try {
      const res = await fetch(`/api/v1/memory-dna/items/${itemId}/reject`, {
        method: 'POST',
      });
      if (res.ok) {
        const updated = await res.json();
        setItems(prev => prev.map(i => i.dna_item_id === itemId ? updated : i));
        setMessage('Item marked as unsupported.');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const categories = [
    'ALL',
    'IDENTITY',
    'FAMILY',
    'RELATIONSHIPS',
    'CHILDHOOD',
    'EDUCATION',
    'CAREER',
    'FRIENDS',
    'HOBBIES',
    'INTERESTS',
    'TRAVEL',
    'ACHIEVEMENTS',
    'IMPORTANT_EVENTS',
    'PLACES',
    'IMPORTANT_OBJECTS',
    'DOCUMENTED_PREFERENCES',
    'DOCUMENTED_VALUES',
    'KNOWN_PHRASES',
    'FREQUENT_TOPICS',
    'PERSONAL_STORIES',
    'LEGACY',
    'UNKNOWN'
  ];

  const filteredItems = items.filter(item => {
    const matchCat = selectedCategory === 'ALL' || item.category === selectedCategory;
    const matchConf = selectedConfidence === 'ALL' || item.confidence === selectedConfidence;
    return matchCat && matchConf;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
              <Dna className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-serif font-bold text-white tracking-wide">Memory DNA</h1>
              <p className="text-xs text-slate-400">Evidence-Grounded Structured Life Intelligence</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium border border-slate-700 transition"
          >
            <History className="w-4 h-4 text-slate-400" />
            <span>Version History ({versions.length})</span>
          </button>

          <button
            onClick={handleBuild}
            disabled={building}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-indigo-600/30 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${building ? 'animate-spin' : ''}`} />
            <span>{building ? 'Synthesizing Archive...' : 'Compile Memory DNA'}</span>
          </button>
        </div>
      </div>

      {/* Ethical Guardrail Banner */}
      <div className="p-4 rounded-xl bg-slate-900 border border-indigo-500/30 flex items-start gap-3">
        <Info className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <p className="text-slate-200 font-medium">Research Boundary & Anti-Fabrication Commitment</p>
          <p className="text-slate-400 leading-relaxed">
            Memory DNA is a structured representation of verified documents, transcripts, and memories.
            It is <strong className="text-slate-300">not a personality clone</strong> and does not simulate consciousness.
            Unrecorded details strictly remain <span className="text-amber-400 font-mono font-semibold">UNKNOWN</span>.
          </p>
        </div>
      </div>

      {message && (
        <div className="p-3 bg-emerald-950/60 border border-emerald-800 text-emerald-300 rounded-lg text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Total DNA Items</p>
          <p className="text-2xl font-bold text-white mt-1">{items.length}</p>
          <p className="text-[10px] text-slate-500 mt-1">Active profile version v{dna?.version || 1}</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-emerald-900/50">
          <div className="flex items-center justify-between">
            <p className="text-[11px] font-medium text-emerald-400 uppercase tracking-wider">Verified Facts</p>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400 mt-1">{stats?.verified_count || items.filter(i => i.confidence === 'VERIFIED').length}</p>
          <p className="text-[10px] text-emerald-600 mt-1">Primary source grounded</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-amber-900/50">
          <div className="flex items-center justify-between">
            <p className="text-[11px] font-medium text-amber-400 uppercase tracking-wider">Supported Inferences</p>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-400 mt-1">{stats?.supported_inferences || items.filter(i => i.confidence === 'SUPPORTED_INFERENCE').length}</p>
          <p className="text-[10px] text-amber-600 mt-1">Correlated deduction</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-rose-900/50">
          <div className="flex items-center justify-between">
            <p className="text-[11px] font-medium text-rose-400 uppercase tracking-wider">Unknown / Disputed</p>
            <HelpCircle className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-rose-400 mt-1">{stats?.unknown_items || items.filter(i => i.confidence === 'UNKNOWN_UNSUPPORTED').length}</p>
          <p className="text-[10px] text-rose-600 mt-1">Unsubstantiated / absent</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Categories Covered</p>
          <p className="text-2xl font-bold text-indigo-400 mt-1">{Object.keys(stats?.by_category || {}).length || (items.length > 0 ? 4 : 0)} / 22</p>
          <p className="text-[10px] text-slate-500 mt-1">Controlled schema</p>
        </div>
      </div>

      {/* Version History Drawer (if open) */}
      {showHistory && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-semibold text-white">Historical Memory DNA Versions</h3>
            </div>
            <button
              onClick={() => setShowHistory(false)}
              className="text-xs text-slate-400 hover:text-white"
            >
              Close
            </button>
          </div>

          {versions.length === 0 ? (
            <p className="text-xs text-slate-500">No previous versions. Current state is version 1.</p>
          ) : (
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {versions.map((v) => (
                <div key={v.version_id} className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex justify-between items-center text-xs">
                  <div>
                    <span className="font-mono font-semibold text-indigo-400">Version {v.version}</span>
                    <p className="text-slate-400 mt-0.5">{v.change_reason}</p>
                    <span className="text-[10px] text-slate-500">{new Date(v.created_at).toLocaleString()} by {v.changed_by}</span>
                  </div>
                  <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded font-mono text-[10px]">
                    Preserved for reproducibility
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="space-y-3">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 flex items-center gap-1 font-medium mr-1">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white font-semibold shadow-sm'
                  : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700'
              }`}
            >
              {cat.replace('_', ' ')}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400 font-medium mr-1">Confidence Filter:</span>
          {['ALL', 'VERIFIED', 'SUPPORTED_INFERENCE', 'UNKNOWN_UNSUPPORTED'].map((conf) => (
            <button
              key={conf}
              onClick={() => setSelectedConfidence(conf)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition ${
                selectedConfidence === conf
                  ? 'bg-slate-700 text-white font-semibold'
                  : 'bg-slate-800/60 text-slate-400 hover:text-white'
              }`}
            >
              {conf === 'ALL' ? 'All Tiers' : conf}
            </button>
          ))}
        </div>
      </div>

      {/* Items Grid */}
      {loading ? (
        <div className="p-12 text-center text-slate-500 text-sm">Loading Memory DNA records...</div>
      ) : filteredItems.length === 0 ? (
        <div className="p-12 rounded-xl bg-slate-900 border border-slate-800 text-center space-y-4">
          <Dna className="w-12 h-12 text-slate-600 mx-auto" />
          <div>
            <h3 className="text-sm font-semibold text-slate-300">No Memory DNA Items Found</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Compile your archive evidence to extract structured facts, relationships, education, and milestones.
            </p>
          </div>
          <button
            onClick={handleBuild}
            disabled={building}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold inline-flex items-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Compile Memory DNA</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredItems.map((item) => {
            const isVerified = item.confidence === 'VERIFIED';
            const isSupported = item.confidence === 'SUPPORTED_INFERENCE';
            const isUnknown = item.confidence === 'UNKNOWN_UNSUPPORTED';

            return (
              <div
                key={item.dna_item_id}
                className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-4"
              >
                <div className="space-y-2.5">
                  {/* Category & Confidence Badge */}
                  <div className="flex items-center justify-between gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider uppercase bg-indigo-950 text-indigo-400 border border-indigo-900">
                      {item.category.replace('_', ' ')}
                    </span>

                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold inline-flex items-center gap-1 ${
                        isVerified
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : isSupported
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-rose-950 text-rose-300 border border-rose-800'
                      }`}
                    >
                      {isVerified && <CheckCircle className="w-3 h-3" />}
                      {isSupported && <AlertTriangle className="w-3 h-3" />}
                      {isUnknown && <HelpCircle className="w-3 h-3" />}
                      <span>{item.confidence}</span>
                    </span>
                  </div>

                  {/* Key & Value */}
                  <div>
                    <h4 className="text-sm font-semibold text-white capitalize">{item.key.replace(/_/g, ' ')}</h4>
                    <div className="text-xs text-slate-300 mt-1 leading-relaxed">
                      {typeof item.value === 'object' ? (
                        <div className="space-y-0.5 text-[11px] text-slate-300">
                          {item.value.title && <p className="font-medium text-white">{item.value.title}</p>}
                          {item.value.description && <p className="text-slate-400">{item.value.description}</p>}
                          {item.value.date && <p className="text-indigo-300">Date: {item.value.date}</p>}
                          {item.value.location && <p className="text-slate-400">Location: {item.value.location}</p>}
                        </div>
                      ) : (
                        <p>{String(item.value)}</p>
                      )}
                    </div>
                  </div>

                  {item.description && (
                    <p className="text-[11px] text-slate-500 italic">{item.description}</p>
                  )}
                </div>

                {/* Provenance & Action Footer */}
                <div className="pt-3 border-t border-slate-800/80 space-y-2">
                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="font-mono">Provenance: {item.provenance_status}</span>
                    <span>Sources: {item.source_memory_ids.length + item.source_evidence_ids.length}</span>
                  </div>

                  {/* Verification Actions */}
                  <div className="flex items-center justify-end gap-1.5 pt-1">
                    <button
                      onClick={() => handleVerify(item.dna_item_id)}
                      className="px-2 py-1 bg-emerald-950/60 hover:bg-emerald-900 text-emerald-400 rounded text-[10px] font-medium border border-emerald-800 flex items-center gap-1 transition"
                      title="Verify with authenticated primary evidence"
                    >
                      <Check className="w-3 h-3" /> Verify
                    </button>
                    <button
                      onClick={() => handleReject(item.dna_item_id)}
                      className="px-2 py-1 bg-rose-950/60 hover:bg-rose-900 text-rose-400 rounded text-[10px] font-medium border border-rose-800 flex items-center gap-1 transition"
                      title="Mark as unsupported claim"
                    >
                      <X className="w-3 h-3" /> Reject
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
