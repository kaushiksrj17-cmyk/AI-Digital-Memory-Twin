import React from 'react';
import { ConfidenceLevel } from '@/types';
import { CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

interface Props {
  level: ConfidenceLevel;
  score?: number;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: string;
}

export const ConfidenceIndicator: React.FC<Props> = ({
  level,
  score,
  showText = true,
  size = 'md',
}) => {
  const configs = {
    VERIFIED: {
      label: 'Verified Evidence',
      badgeClass: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
      icon: CheckCircle2,
      dotClass: 'bg-emerald-500',
    },
    SUPPORTED_INFERENCE: {
      label: 'Supported Inference',
      badgeClass: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30',
      icon: AlertTriangle,
      dotClass: 'bg-amber-500',
    },
    UNKNOWN_UNSUPPORTED: {
      label: 'Unknown / Unsupported',
      badgeClass: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30',
      icon: HelpCircle,
      dotClass: 'bg-rose-500',
    },
  };

  const current = configs[level] || configs.UNKNOWN_UNSUPPORTED;
  const Icon = current.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2',
  };

  return (
    <span
      className={`inline-flex items-center font-medium border rounded-full ${current.badgeClass} ${sizeClasses[size]}`}
      title={
        level === 'VERIFIED'
          ? 'Grounded in authenticated primary documents, photos, or recordings'
          : level === 'SUPPORTED_INFERENCE'
          ? 'Plausible contextual inference corroborated by intersecting memories'
          : 'Unrecorded in preserved archives; model explicitly refuses fabrication'
      }
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      {showText && <span>{current.label}</span>}
      {score !== undefined && (
        <span className="opacity-70 text-[10px]">({Math.round(score * 100)}%)</span>
      )}
    </span>
  );
};
