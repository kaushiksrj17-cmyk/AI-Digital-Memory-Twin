'use client';

import React, { useState } from 'react';
import { RoomObject } from '@/types';
import { ConfidenceIndicator } from '@/components/ConfidenceIndicator';
import { ProvenanceIndicator } from '@/components/ProvenanceIndicator';
import {
  Image,
  BookOpen,
  Music,
  Calendar,
  FileText,
  Compass,
  Search,
  ExternalLink,
  Tag,
  MapPin,
  Clock,
  Sparkles,
} from 'lucide-react';

interface AccessibleMemoryListProps {
  objects: RoomObject[];
  selectedObject: RoomObject | null;
  onSelectObject: (obj: RoomObject) => void;
  onOpenDetails: (obj: RoomObject) => void;
}

export function AccessibleMemoryList({
  objects,
  selectedObject,
  onSelectObject,
  onOpenDetails,
}: AccessibleMemoryListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');

  const filtered = objects.filter((obj) => {
    const matchesSearch =
      searchTerm === '' ||
      obj.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      obj.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (obj.location && obj.location.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesCategory =
      categoryFilter === 'ALL' || obj.category === categoryFilter;

    return matchesSearch && matchesCategory;
  });

  const getObjectIcon = (type: string) => {
    switch (type) {
      case 'PHOTO_FRAME':
        return <Image className="w-4 h-4 text-emerald-400" />;
      case 'ARCHIVE_BOOKSHELF':
        return <BookOpen className="w-4 h-4 text-amber-400" />;
      case 'AUDIO_STATION':
        return <Music className="w-4 h-4 text-cyan-400" />;
      case 'TIMELINE_WALL':
        return <Calendar className="w-4 h-4 text-indigo-400" />;
      case 'STORY_STATION':
        return <FileText className="w-4 h-4 text-purple-400" />;
      default:
        return <Compass className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-4" role="region" aria-label="Accessible Archival Memory Catalog">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search memories by title, narrative, or location..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            aria-label="Filter archival records"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
            aria-label="Filter by category"
          >
            <option value="ALL">All Categories</option>
            <option value="FAMILY">Family</option>
            <option value="CAREER">Career</option>
            <option value="CHILDHOOD">Childhood</option>
            <option value="EDUCATION">Education</option>
            <option value="TRAVEL">Travel</option>
            <option value="PERSONAL_STORY">Personal Story</option>
            <option value="ACHIEVEMENT">Achievement</option>
          </select>
        </div>
      </div>

      {/* Memory Grid/List */}
      {filtered.length === 0 ? (
        <div className="p-12 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-950/40">
          <p className="text-xs text-slate-400">
            No memory records matched your criteria. Upload records in the Memory Vault.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3" role="list">
          {filtered.map((obj) => {
            const isSelected = selectedObject?.object_id === obj.object_id;
            return (
              <div
                key={obj.object_id}
                role="listitem"
                tabIndex={0}
                onClick={() => {
                  onSelectObject(obj);
                  onOpenDetails(obj);
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectObject(obj);
                    onOpenDetails(obj);
                  }
                }}
                className={`p-4 rounded-2xl border transition-all cursor-pointer text-left focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  isSelected
                    ? 'bg-indigo-950/40 border-indigo-500/60 shadow-lg shadow-indigo-500/10'
                    : 'bg-slate-900/60 hover:bg-slate-900 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
                      {getObjectIcon(obj.object_type)}
                    </div>
                    <div>
                      <h4 className="font-serif text-sm font-semibold text-slate-100 line-clamp-1">
                        {obj.title}
                      </h4>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider">
                        {obj.category} &bull; {obj.object_type.replace('_', ' ')}
                      </span>
                    </div>
                  </div>

                  <ConfidenceIndicator level={obj.confidence} variant="badge" />
                </div>

                <p className="text-xs text-slate-300 line-clamp-2 mb-3">
                  {obj.description || 'Verified archival memory record.'}
                </p>

                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/60 text-[11px] text-slate-400">
                  <div className="flex items-center gap-3">
                    {obj.date && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {obj.date}
                      </span>
                    )}
                    {obj.location && (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-500" />
                        {obj.location}
                      </span>
                    )}
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onOpenDetails(obj);
                    }}
                    className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
                  >
                    <span>View Evidence</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
