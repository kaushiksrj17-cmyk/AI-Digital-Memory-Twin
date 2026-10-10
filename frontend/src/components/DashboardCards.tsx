import React from 'react';
import {
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Image as ImageIcon,
  Video,
  Music,
  FileText,
  Users,
  Calendar,
  MessageSquare
} from 'lucide-react';
import { DashboardStats } from '@/types';

interface Props {
  stats: DashboardStats;
}

export const DashboardCards: React.FC<Props> = ({ stats }) => {
  const cards = [
    {
      title: 'Total Memories',
      value: stats.total_memories,
      icon: BookOpen,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-500/10',
      description: 'Preserved personal life narratives',
    },
    {
      title: 'Verified Memories',
      value: stats.verified_memories,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      description: 'Grounded in primary archival evidence (GREEN)',
    },
    {
      title: 'Supported Inferences',
      value: stats.supported_inferences,
      icon: AlertTriangle,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      description: 'Corroborated deductions (YELLOW)',
    },
    {
      title: 'Unknown Memories',
      value: stats.unknown_unsupported,
      icon: HelpCircle,
      color: 'text-rose-400',
      bgColor: 'bg-rose-500/10',
      description: 'Unrecorded / non-fabricated (RED)',
    },
    {
      title: 'Photos',
      value: stats.photos_count,
      icon: ImageIcon,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      description: 'Historical portraits & albums',
    },
    {
      title: 'Videos',
      value: stats.videos_count,
      icon: Video,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      description: 'Preserved motion films',
    },
    {
      title: 'Audio',
      value: stats.audio_count,
      icon: Music,
      color: 'text-teal-400',
      bgColor: 'bg-teal-500/10',
      description: 'Oral history recordings',
    },
    {
      title: 'Documents',
      value: stats.documents_count,
      icon: FileText,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10',
      description: 'Letters, diaries, certificates',
    },
    {
      title: 'People',
      value: stats.people_count,
      icon: Users,
      color: 'text-sky-400',
      bgColor: 'bg-sky-500/10',
      description: 'Kinship & social network',
    },
    {
      title: 'Life Events',
      value: stats.life_events_count,
      icon: Calendar,
      color: 'text-pink-400',
      bgColor: 'bg-pink-500/10',
      description: 'Milestones on chronological timeline',
    },
    {
      title: 'Conversation Sessions',
      value: stats.conversation_sessions_count,
      icon: MessageSquare,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      description: 'Evidence-grounded dialogue exchanges',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div
            key={idx}
            className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400">
                {c.title}
              </span>
              <div className={`p-2 rounded-lg ${c.bgColor}`}>
                <Icon className={`w-4 h-4 ${c.color}`} />
              </div>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-serif font-bold text-slate-900 dark:text-slate-100">
                {c.value}
              </span>
              <span className="text-[10px] text-slate-500">records</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-400 dark:text-slate-500 truncate">
              {c.description}
            </p>
          </div>
        );
      })}
    </div>
  );
};
