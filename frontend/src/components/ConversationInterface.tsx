'use client';

import React, { useState } from 'react';
import { Message, ProvenanceRecord } from '@/types';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { ProvenanceIndicator } from '@/components/ProvenanceIndicator';
import { AIGeneratedBadge } from '@/components/AIGeneratedBadge';
import { EthicalBanner } from '@/components/EthicalBanner';
import { Send, User, Sparkles, AlertCircle } from 'lucide-react';

interface Props {
  initialMessages?: Message[];
}

export const ConversationInterface: React.FC<Props> = ({ initialMessages = [] }) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput('');
    setErrorMsg('');

    const newMsg: Message = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: userText,
      ethical_disclaimer: '',
      confidence: 'VERIFIED',
      is_ai_generated: false,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, newMsg]);
    setLoading(true);

    try {
      const res = await fetch('/api/v1/conversation/sessions/demo-session-001/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: userText }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.message || 'Error occurred');
      }

      const aiMsg: Message = await res.json();
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      setErrorMsg(err.message || 'Unable to ground response. Verify backend connectivity.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[700px] rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm overflow-hidden">
      {/* Dialogue Header Banner */}
      <EthicalBanner variant="topbar" />

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((m) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={m.id}
              className={`flex items-start gap-3.5 max-w-2xl ${
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
                    : 'bg-slate-100 dark:bg-slate-800/80 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700/60 rounded-tl-none shadow-sm'
                }`}
              >
                {!isUser && (
                  <div className="flex items-center justify-between gap-3 mb-2.5 pb-2 border-b border-slate-200/60 dark:border-slate-700/60">
                    <AIGeneratedBadge minimal />
                    <ConfidenceIndicator level={m.confidence} size="sm" />
                  </div>
                )}

                <p>{m.content}</p>

                {/* Provenance Citations */}
                {!isUser && m.provenance_citations && (
                  <ProvenanceIndicator citations={m.provenance_citations} />
                )}

                {!isUser && m.ethical_disclaimer && (
                  <div className="mt-3 text-[10px] text-slate-400 dark:text-slate-500 border-t border-slate-200/40 dark:border-slate-700/40 pt-1.5 italic">
                    {m.ethical_disclaimer}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-3 text-xs text-slate-500 mr-auto p-4 bg-slate-100 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800 animate-pulse">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>Consulting preserved vault records & validating evidence citations...</span>
          </div>
        )}
      </div>

      {errorMsg && (
        <div className="p-3 mx-4 mb-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-500 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Input Form */}
      <form
        onSubmit={handleSend}
        className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40 flex items-center gap-3"
      >
        <input
          type="text"
          placeholder="Ask about preserved life memories (e.g., 'What occurred during the 1968 graduation?')..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 text-xs px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white transition-colors disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
