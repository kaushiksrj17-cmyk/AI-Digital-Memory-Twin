'use client';

import React, { useState, useEffect } from 'react';
import { MemoryCard } from '@/components/MemoryCard';
import { EmptyState } from '@/components/ui/EmptyState';
import { CardSkeleton } from '@/components/ui/Skeleton';
import { Memory, ConfidenceLevel } from '@/types';
import { BookOpen, Search, Filter } from 'lucide-react';

export default function MemoriesPage() {
  const [selectedConfidence, setSelectedConfidence] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMemories() {
      setLoading(true);
      try {
        const res = await fetch('/api/v1/memories');
        if (res.ok) {
          const data = await res.json();
          setMemories(data);
        }
      } catch (err) {
        console.error('Failed to load memories:', err);
      } finally {
        setLoading(false);
      }
    }
    loadMemories();
  }, []);

  const filtered = memories.filter((m) => {
    const matchesConfidence =
      selectedConfidence === 'ALL' || m.confidence === selectedConfidence;
    const matchesSearch =
      !searchQuery ||
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (m.description && m.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (m.narrative && m.narrative.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (m.location && m.location.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (m.location_name && m.location_name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesConfidence && matchesSearch;
  });

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6 animate-fadeIn">
      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search memories by keyword, place, or date..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs pl-9 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
          {['ALL', 'VERIFIED', 'SUPPORTED_INFERENCE', 'UNKNOWN_UNSUPPORTED'].map((conf) => (
            <button
              key={conf}
              onClick={() => setSelectedConfidence(conf)}
              className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap ${
                selectedConfidence === conf
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              {conf === 'ALL' ? 'All Memories' : conf.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Memories List */}
      <div className="space-y-4">
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : filtered.length > 0 ? (
          filtered.map((m) => <MemoryCard key={m.id} memory={m} />)
        ) : (
          <EmptyState
            title="No Matching Preserved Memories Found"
            description="ECHO does not fabricate memories to fill gaps. Try adjusting search filters or ingest new archival evidence into the vault."
            icon={BookOpen}
          />
        )}
      </div>
    </div>
  );
}
