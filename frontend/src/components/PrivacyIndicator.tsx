import React from 'react';
import { Lock, Shield, EyeOff, Users, Globe } from 'lucide-react';
import { PrivacyLevel } from '@/types';

interface Props {
  path?: string;
  level?: PrivacyLevel;
}

export const PrivacyIndicator: React.FC<Props> = ({ path, level }) => {
  if (level) {
    const levelConfigs: Record<string, { label: string; icon: any; colorClass: string }> = {
      PRIVATE: {
        label: 'Private Vault',
        icon: Lock,
        colorClass: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      },
      RESTRICTED: {
        label: 'Restricted Access',
        icon: EyeOff,
        colorClass: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      },
      FAMILY: {
        label: 'Family Archive',
        icon: Users,
        colorClass: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
      },
      FAMILY_ONLY: {
        label: 'Family Archive',
        icon: Users,
        colorClass: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
      },
      AUTHORIZED_USERS: {
        label: 'Authorized Users',
        icon: Shield,
        colorClass: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      },
      MEMORIAL_PUBLIC: {
        label: 'Memorial Public',
        icon: Globe,
        colorClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      },
    };

    const config = levelConfigs[level] || {
      label: level.replace('_', ' '),
      icon: Shield,
      colorClass: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
    };
    const Icon = config.icon;

    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${config.colorClass}`}
        title={`Archival Privacy Classification: ${level}`}
      >
        <Icon className="w-3.5 h-3.5" />
        <span>{config.label}</span>
      </span>
    );
  }

  const storagePath = path || 'D:\\ECHO\\storage\\local';
  return (
    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-500/20">
      <Lock className="w-3.5 h-3.5 text-emerald-500" />
      <span>Private Vault &bull; Local Storage ({storagePath})</span>
    </div>
  );
};
