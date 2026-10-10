import React from 'react';
import { ShieldCheck, Info } from 'lucide-react';

interface Props {
  variant?: 'topbar' | 'card' | 'footer';
}

export const EthicalBanner: React.FC<Props> = ({ variant = 'topbar' }) => {
  const disclaimer =
    'ECHO is an AI-generated memorial representation. It does not recreate consciousness, identity, or the actual person.';

  if (variant === 'card') {
    return (
      <div className="rounded-lg p-3 bg-slate-900/40 border border-slate-800 text-xs text-slate-400 flex items-start gap-2.5">
        <ShieldCheck className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
        <div>
          <span className="font-semibold text-slate-300">Ethical Boundary: </span>
          {disclaimer} Preserved memories are grounded in verified historical artifacts.
        </div>
      </div>
    );
  }

  return (
    <div className="w-full bg-slate-900/90 border-b border-slate-800/80 px-4 py-2 text-center text-xs text-slate-300 flex items-center justify-center gap-2">
      <ShieldCheck className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
      <span>
        <strong>Notice:</strong> {disclaimer}
      </span>
    </div>
  );
};
