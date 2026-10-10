'use client';

import React, { useState, useEffect } from 'react';
import { EthicalBanner } from '@/components/EthicalBanner';
import { EvidenceDrawer } from '@/components/EvidenceDrawer';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  Message,
  ConversationSession,
  ResponseSource,
  RAGQueryResponse,
} from '@/types';
import {
  Send,
  User,
  Sparkles,
  AlertCircle,
  Plus,
  Download,
  Trash2,
  ShieldCheck,
  ShieldAlert,
  Info,
  ChevronDown,
  ChevronUp,
  FileText,
  AlertTriangle,
} from 'lucide-react';

export default function ConversationPage() {
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('demo-session-001');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lifecycleStep, setLifecycleStep] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState('');
  const [selectedSource, setSelectedSource] = useState<ResponseSource | null>(null);
  const [expandedExplanationId, setExpandedExplanationId] = useState<string | null>(null);
  const [memorialProfileId, setMemorialProfileId] = useState('demo-profile-001');

  // Load Sessions
  const loadSessions = async () => {
    try {
      const res = await fetch('/api/v1/conversations');
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        if (data.length > 0 && !activeSessionId) {
          setActiveSessionId(data[0].id);
          setMessages(data[0].messages || []);
        } else if (activeSessionId) {
          const active = data.find((s: ConversationSession) => s.id === activeSessionId);
          if (active) setMessages(active.messages || []);
        }
      }
    } catch {
      // Offline fallback
    }
  };

  useEffect(() => {
    loadSessions();
  }, [activeSessionId]);

  const handleSelectSession = (s: ConversationSession) => {
    setActiveSessionId(s.id);
    setMessages(s.messages || []);
    setErrorMsg('');
  };

  const handleNewSession = async () => {
    try {
      const res = await fetch('/api/v1/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          memorial_profile_id: memorialProfileId,
          user_id: 'default-user-001',
          title: `Dialogue Session ${sessions.length + 1}`,
          ethical_boundary_acknowledged: true,
        }),
      });
      if (res.ok) {
        const newSession = await res.json();
        setSessions((prev) => [newSession, ...prev]);
        setActiveSessionId(newSession.id);
        setMessages([]);
      }
    } catch (err: any) {
      setErrorMsg('Failed to create new conversation session.');
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      const res = await fetch(`/api/v1/conversations/${id}`, { method: 'DELETE' });
      if (res.ok) {
        const rem = sessions.filter((s) => s.id !== id);
        setSessions(rem);
        if (activeSessionId === id && rem.length > 0) {
          setActiveSessionId(rem[0].id);
          setMessages(rem[0].messages || []);
        } else if (rem.length === 0) {
          setActiveSessionId('');
          setMessages([]);
        }
      }
    } catch {
      setErrorMsg('Failed to delete session.');
    }
  };

  const handleExportSession = async () => {
    if (!activeSessionId) return;
    try {
      const res = await fetch(`/api/v1/conversations/${activeSessionId}/export`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `echo_transcript_${activeSessionId}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch {
      setErrorMsg('Failed to export session transcript.');
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput('');
    setErrorMsg('');

    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: userText,
      ethical_disclaimer: '',
      confidence: 'VERIFIED',
      confidence_score: 1.0,
      is_ai_generated: false,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setLifecycleStep('Searching preserved archive across vector, keyword, and knowledge graph indexes...');

    try {
      // Step simulation for streaming UX
      setTimeout(() => setLifecycleStep('Ranking archival evidence & building context...'), 300);
      setTimeout(() => setLifecycleStep('Synthesizing evidence-grounded response...'), 600);
      setTimeout(() => setLifecycleStep('Executing 18 Memory Guardian evidentiary and boundary audits...'), 900);

      const targetSession = activeSessionId || 'demo-session-001';
      const res = await fetch(`/api/v1/conversations/${targetSession}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: userText,
          memorial_profile_id: memorialProfileId,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || errorData.message || 'Error occurred');
      }

      const aiMsg: Message = await res.json();
      setMessages((prev) => [...prev, aiMsg]);
      loadSessions();
    } catch (err: any) {
      setErrorMsg(err.message || 'Unable to ground response. Verify backend connectivity.');
    } finally {
      setLoading(false);
      setLifecycleStep('');
    }
  };

  return (
    <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 py-4 sm:py-6 flex flex-col lg:flex-row gap-6 h-[calc(100vh-5rem)] overflow-hidden animate-fadeIn">
      {/* Sessions Sidebar */}
      <div className="w-full lg:w-80 shrink-0 flex flex-col bg-white dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm h-64 lg:h-full">
        <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
          <h2 className="font-semibold text-xs tracking-wider uppercase text-slate-500 dark:text-slate-400">Dialogue Sessions</h2>
          <Button
            size="sm"
            variant="primary"
            onClick={handleNewSession}
          >
            <Plus className="w-3.5 h-3.5 mr-1" />
            <span>New</span>
          </Button>
        </div>

          <div className="flex-1 overflow-y-auto py-3 space-y-2">
            {sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => handleSelectSession(s)}
                className={`p-3 rounded-xl border cursor-pointer transition-all flex items-start justify-between group ${
                  activeSessionId === s.id
                    ? 'bg-indigo-600/10 border-indigo-500/40 text-indigo-200'
                    : 'bg-slate-850/50 border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="flex-1 min-w-0 pr-2">
                  <h4 className="text-xs font-medium truncate">{s.title || 'Memorial Session'}</h4>
                  <p className="text-[10px] text-slate-500 truncate mt-0.5">
                    {s.messages?.length || 0} messages • {s.updated_at ? new Date(s.updated_at).toLocaleDateString() : 'Recent'}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(e, s.id)}
                  className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-1 rounded transition-opacity"
                  title="Delete Session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}

            {sessions.length === 0 && (
              <div className="text-center py-8 text-xs text-slate-500">
                No active dialogue sessions. Click &ldquo;New&rdquo; to start.
              </div>
            )}
          </div>

          {/* Export Action */}
          {activeSessionId && (
            <div className="pt-3 border-t border-slate-800">
              <button
                onClick={handleExportSession}
                className="w-full py-2 px-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors flex items-center justify-center gap-2"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export Session Transcript</span>
              </button>
            </div>
          )}
        </div>

        {/* Main Dialogue Panel */}
        <div className="flex-1 flex flex-col bg-white dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          <EthicalBanner variant="topbar" />

          {/* Chat Stream Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((m) => {
              const isUser = m.role === 'user';
              const isBlocked = m.guardian_status === 'BLOCK';
              const isUnknown = m.confidence === 'UNKNOWN_UNSUPPORTED';
              const hasContradictions = m.contradictions && m.contradictions.length > 0;

              return (
                <div
                  key={m.id}
                  className={`flex items-start gap-3.5 max-w-3xl ${
                    isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
                      isUser
                        ? 'bg-indigo-600 text-white'
                        : 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                    }`}
                  >
                    {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
                  </div>

                  <div
                    className={`p-4 rounded-2xl text-xs leading-relaxed ${
                      isUser
                        ? 'bg-indigo-600 text-white rounded-tr-none'
                        : 'bg-slate-850 text-slate-100 border border-slate-700/60 rounded-tl-none shadow-sm'
                    }`}
                  >
                    {/* Header for Assistant Message */}
                    {!isUser && (
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-3 pb-2.5 border-b border-slate-700/60">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 font-mono text-[10px] uppercase">
                            AI-GENERATED MEMORIAL RESPONSE
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full border text-[10px] font-mono ${
                              m.confidence === 'VERIFIED'
                                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                                : m.confidence === 'SUPPORTED_INFERENCE'
                                ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                                : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                            }`}
                          >
                            {m.confidence}
                          </span>
                        </div>

                        {/* Guardian Status Badge */}
                        <div className="flex items-center gap-1.5">
                          {isBlocked ? (
                            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px]">
                              <ShieldAlert className="w-3 h-3 text-rose-400" />
                              <span>GUARDIAN: BLOCK</span>
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px]">
                              <ShieldCheck className="w-3 h-3 text-emerald-400" />
                              <span>GUARDIAN: PASS</span>
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Contradiction Alert Banner */}
                    {!isUser && hasContradictions && (
                      <div className="mb-3 p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
                        <div>
                          <strong>Conflicting Sources Detected:</strong> Archival records contain multiple differing accounts on this topic.
                        </div>
                      </div>
                    )}

                    {/* Unknown / Insufficient Evidence State */}
                    {!isUser && isUnknown && (
                      <div className="mb-2.5 p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-[11px] flex items-center gap-2">
                        <Info className="w-3.5 h-3.5 shrink-0" />
                        <span>Insufficient preserved evidence. Anti-fabrication boundary engaged.</span>
                      </div>
                    )}

                    {/* Response Text */}
                    <p className="whitespace-pre-line text-slate-200">{m.content}</p>

                    {/* Clickable Source Pills */}
                    {!isUser && m.sources && m.sources.length > 0 && (
                      <div className="mt-3.5 pt-2.5 border-t border-slate-700/60">
                        <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                          Supporting Archival Sources:
                        </label>
                        <div className="flex flex-wrap gap-1.5">
                          {m.sources.map((src) => (
                            <button
                              key={src.source_id}
                              onClick={() => setSelectedSource(src)}
                              className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition-all text-[11px] flex items-center gap-1.5"
                            >
                              <FileText className="w-3 h-3 text-indigo-400" />
                              <span className="truncate max-w-[200px]">{src.source_title}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Retrieval Explanation Toggle */}
                    {!isUser && m.retrieval_context_summary && (
                      <div className="mt-3 pt-2 border-t border-slate-800">
                        <button
                          onClick={() =>
                            setExpandedExplanationId(
                              expandedExplanationId === m.id ? null : m.id
                            )
                          }
                          className="text-[10px] text-slate-400 hover:text-slate-300 flex items-center gap-1"
                        >
                          <span>Why was this retrieved?</span>
                          {expandedExplanationId === m.id ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDown className="w-3 h-3" />
                          )}
                        </button>
                        {expandedExplanationId === m.id && (
                          <div className="mt-2 p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-300 leading-relaxed font-mono">
                            {m.retrieval_context_summary}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Disclaimer */}
                    {!isUser && m.ethical_disclaimer && (
                      <div className="mt-3 text-[10px] text-slate-500 border-t border-slate-800 pt-1.5 italic">
                        {m.ethical_disclaimer}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Lifecycle Progress Banner */}
            {loading && (
              <div className="flex items-center gap-3 text-xs text-indigo-300 mr-auto p-4 bg-slate-900/80 rounded-2xl border border-indigo-500/30 animate-pulse">
                <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>{lifecycleStep || 'Consulting preserved vault records & validating evidence...'}</span>
              </div>
            )}
          </div>

          {errorMsg && (
            <div className="p-3 mx-6 mb-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* User Input Form */}
          <form
            onSubmit={handleSend}
            className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/80 flex items-center gap-3"
          >
            <input
              type="text"
              placeholder="Ask about documented life events, education, career, travel, or family stories..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 text-xs px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 shadow-sm"
            />
            <Button
              type="submit"
              variant="primary"
              disabled={!input.trim() || loading}
              className="shrink-0"
            >
              <span>Send</span>
              <Send className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </form>
        </div>

      {/* Slide-out Evidence Drawer */}
      <EvidenceDrawer source={selectedSource} onClose={() => setSelectedSource(null)} />
    </div>
  );
}
