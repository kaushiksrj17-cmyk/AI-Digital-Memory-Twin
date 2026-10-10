'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'amber';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className = '',
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled = false,
      iconLeft,
      iconRight,
      children,
      ...props
    },
    ref
  ) => {
    const baseClasses =
      'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none';

    const sizeClasses = {
      xs: 'text-xs px-2.5 py-1.5 gap-1.5',
      sm: 'text-xs px-3.5 py-2 gap-2',
      md: 'text-xs sm:text-sm px-4 py-2.5 gap-2',
      lg: 'text-sm sm:text-base px-5 py-3 gap-2.5',
    }[size];

    const variantClasses = {
      primary:
        'bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white shadow-sm shadow-indigo-600/30 focus:ring-indigo-500 border border-indigo-500/30',
      secondary:
        'bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-700/80 focus:ring-slate-500',
      outline:
        'bg-transparent hover:bg-slate-100 active:bg-slate-200 text-slate-700 dark:text-slate-300 dark:hover:bg-slate-800 border border-slate-300 dark:border-slate-700 focus:ring-indigo-500',
      ghost:
        'bg-transparent hover:bg-slate-100 active:bg-slate-200 text-slate-600 dark:text-slate-300 dark:hover:bg-slate-800/80 focus:ring-slate-500 border border-transparent',
      danger:
        'bg-rose-600 hover:bg-rose-500 active:bg-rose-700 text-white shadow-sm shadow-rose-600/30 focus:ring-rose-500 border border-rose-500/30',
      amber:
        'bg-amber-600 hover:bg-amber-500 active:bg-amber-700 text-white shadow-sm shadow-amber-600/30 focus:ring-amber-500 border border-amber-500/30',
    }[variant];

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseClasses} ${sizeClasses} ${variantClasses} ${className}`}
        {...props}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>{children}</span>
          </>
        ) : (
          <>
            {iconLeft && <span className="shrink-0">{iconLeft}</span>}
            <span>{children}</span>
            {iconRight && <span className="shrink-0">{iconRight}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
