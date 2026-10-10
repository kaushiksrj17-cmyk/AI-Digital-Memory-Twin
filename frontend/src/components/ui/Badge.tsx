'use client';

import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'verified' | 'inference' | 'unknown' | 'neutral' | 'indigo' | 'amber' | 'emerald';
  size?: 'sm' | 'md';
  dot?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
  }[size];

  const variantClasses = {
    verified:
      'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-medium',
    inference:
      'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 font-medium',
    unknown:
      'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20 font-medium',
    neutral:
      'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700/80',
    indigo:
      'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20 font-medium',
    amber:
      'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 font-medium',
    emerald:
      'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-medium',
  }[variant];

  const dotClasses = {
    verified: 'bg-emerald-500',
    inference: 'bg-amber-500',
    unknown: 'bg-rose-500',
    neutral: 'bg-slate-400',
    indigo: 'bg-indigo-500',
    amber: 'bg-amber-500',
    emerald: 'bg-emerald-500',
  }[variant];

  return (
    <span
      className={`inline-flex items-center rounded-full font-sans tracking-tight transition-colors ${sizeClasses} ${variantClasses} ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotClasses}`} />}
      <span>{children}</span>
    </span>
  );
};
