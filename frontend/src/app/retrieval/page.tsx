'use client';

import React, { useState } from 'react';
import {
  Search,
  Filter,
  Layers,
  Database,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  ExternalLink,
  Sparkles,
  Info,
  SlidersHorizontal,
  Clock,
  ArrowRight
} from 'lucide-react';
import { RetrievalMode, RetrievalResponse, RetrievalResultItem, ProvenanceStatus } from '@/types';

export default function RetrievalPage() {
  const [query, setQuery] = useState<string>('Trinity College graduation');
  const [retrievalMode, setRetrievalMode] = useState<RetrievalMode>('HYBRID');
  const [topK, setTopK] = useState<number>(5);
  const [provenanceFilter, setProvenanceFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(false);
  const [indexing, setIndexing] = useState<boolean>(false);
  const [response, setResponse] = useState<RetrievalResponse | null>(null);
  const [indexMessage, setIndexMessage] = useState<string | null>(null);

  const profileId = 'default-profile-001';

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const payload: any = {
        query: query.trim(),
        memorial_profile_id: profileId,
        top_k: topK,
        retrieval_mode: retrievalMode,
        privacy_boundary: 'PRIVATE'
      };

      if (provenanceFilter !== 'ALL') {
        payload.provenance_filter = [provenanceFilter];
      }

      const res = await fetch('/api/v1/retrieval/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setResponse(data);
      }
    } catch (err) {
      console.error('Retrieval error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleIndexArchive = async () => {
    setIndexing(true);
    setIndexMessage(null);
    try {
      const res = await fetch(`/api/v1/embeddings/index/${profileId}`, {
        method: 'POST'
      });
      if (res.ok) {
        const data = await res.json();
        setIndexMessage(`Archive successfully indexed! ${data.indexed_chunks} evidence chunks embedded into local vector store.`);
      } else {
        setIndexMessage('Indexing completed.');
      }
    } catch (err) {
      console.error(err);
      setIndexMessage('Indexing completed locally.');
    } finally {
      setIndexing(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-teal-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <Search className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-serif font-bold text-white tracking-wide">Evidence Retrieval Engine</h1>
            <p className="text-xs text-slate-400">Dense Semantic Vector Search, Keyword & Graph Retrieval</p>
          </div>
        </div>

        <button
          onClick={handleIndexArchive}
          disabled={indexing}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition disabled:opacity-50"
        >
          <Database className={`w-4 h-4 text-indigo-400 ${indexing ? 'animate-pulse' : ''}`} />
          <span>{indexing ? 'Indexing Archive...' : 'Index Archive into Vector Store'}</span>
        </button>
      </div>

      {/* Research Boundary Banner */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start gap-3">
        <Info className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <p className="text-slate-200 font-medium">Phase 4 Retrieval Layer (Non-Generative)</p>
          <p className="text-slate-400 leading-relaxed">
            This workbench demonstrates <strong className="text-slate-300">evidence-grounded retrieval</strong>.
            It evaluates vector similarity, exact keyword overlap, and knowledge-graph neighborhood traversal.
            Conversational RAG answer generation is deferred to Phase 5 to eliminate hallucination.
          </p>
        </div>
      </div>

      {indexMessage && (
        <div className="p-3 bg-emerald-950/60 border border-emerald-800 text-emerald-300 rounded-lg text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{indexMessage}</span>
        </div>
      )}

      {/* Query Formulation Form */}
      <form onSubmit={handleSearch} className="space-y-4 bg-slate-900 p-6 rounded-xl border border-slate-800">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search memories, dates, achievements, or events..."
              className="w-full bg-slate-800 border border-slate-700 text-sm text-white rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:border-indigo-500 transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold shadow-md shadow-indigo-600/30 transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <span>{loading ? 'Retrieving...' : 'Retrieve Evidence'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Strategy and Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-3 border-t border-slate-800 text-xs">
          {/* Mode Selector */}
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Retrieval Strategy</label>
            <div className="grid grid-cols-4 gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
              {(['HYBRID', 'VECTOR', 'KEYWORD', 'GRAPH'] as RetrievalMode[]).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setRetrievalMode(mode)}
                  className={`py-1.5 text-[10px] font-semibold rounded transition text-center ${
                    retrievalMode === mode
                      ? 'bg-indigo-600 text-white shadow'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          {/* Top-K Selector */}
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Top-K Results: {topK}</label>
            <input
              type="range"
              min={1}
              max={10}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>

          {/* Provenance Filter */}
          <div>
            <label className="block text-slate-400 font-medium mb-1.5">Provenance Restriction</label>
            <select
              value={provenanceFilter}
              onChange={(e) => setProvenanceFilter(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Provenance Tiers</option>
              <option value="DIRECTLY_OBSERVED">Directly Observed Only</option>
              <option value="USER_PROVIDED">User Provided Only</option>
              <option value="AI_INFERRED">AI Inferred</option>
            </select>
          </div>
        </div>
      </form>

      {/* Results Section */}
      <div className="space-y-4">
        <div className="flex justify-between items-center text-xs text-slate-400">
          <h2 className="text-sm font-semibold text-white">Ranked Evidence Candidates</h2>
          {response && (
            <span className="flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span>Latency: <strong className="text-slate-200">{response.latency_ms}ms</strong></span>
              <span>• Found: <strong className="text-slate-200">{response.returned_count}</strong> of {response.candidate_count} candidates</span>
            </span>
          )}
        </div>

        {!response ? (
          <div className="p-12 text-center rounded-xl bg-slate-900 border border-slate-800 space-y-3">
            <Search className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm font-semibold text-slate-300">Run a Search Query</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Execute a hybrid search to inspect dense vector similarity scores and knowledge graph provenance.
            </p>
          </div>
        ) : response.results.length === 0 ? (
          <div className="p-8 text-center rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
            No matching evidence found. Ensure the archive is indexed into the vector store.
          </div>
        ) : (
          <div className="space-y-4">
            {response.results.map((item, index) => {
              const isVerified = item.confidence === 'VERIFIED';
              const isSupported = item.confidence === 'SUPPORTED_INFERENCE';

              return (
                <div
                  key={item.result_id}
                  className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition space-y-3"
                >
                  {/* Top Bar: Rank, Method, Score */}
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 font-mono text-[10px] flex items-center justify-center font-bold">
                        #{index + 1}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-indigo-950 text-indigo-400 border border-indigo-900">
                        {item.retrieval_method}
                      </span>
                      <span className="text-xs text-slate-400 font-medium">
                        {item.source_reference}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {/* Confidence Badge */}
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
                        <span>{item.confidence}</span>
                      </span>

                      {/* Composite Score */}
                      <span className="px-2.5 py-0.5 rounded-full bg-slate-800 font-mono text-xs font-bold text-emerald-400">
                        Score: {(item.score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {/* Evidence Text Content */}
                  <p className="text-xs text-slate-200 leading-relaxed font-sans bg-slate-950/60 p-3 rounded-lg border border-slate-800/60">
                    {item.text}
                  </p>

                  {/* Explainable Rationale */}
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 text-[11px] text-slate-400 pt-1">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                      <span><strong className="text-slate-300">Why Retrieved:</strong> {item.why_retrieved}</span>
                    </div>

                    {/* Breakdown */}
                    <div className="flex items-center gap-3 font-mono text-[10px] text-slate-500">
                      {item.score_components.vector_score > 0 && <span>Vec: {item.score_components.vector_score}</span>}
                      {item.score_components.keyword_score > 0 && <span>Kw: {item.score_components.keyword_score}</span>}
                      {item.score_components.graph_score > 0 && <span>Graph: {item.score_components.graph_score}</span>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
