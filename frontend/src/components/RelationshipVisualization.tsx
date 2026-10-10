import React from 'react';
import { Network, Sparkles, Shield } from 'lucide-react';
import { Relationship } from '@/types';

interface Props {
  relationships?: Relationship[];
}

export const RelationshipVisualization: React.FC<Props> = ({ relationships }) => {
  return (
    <div className="relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-950 p-6 overflow-hidden">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(#312e81_1px,transparent_1px)] [background-size:16px_16px] opacity-25" />

      <div className="relative z-10 flex flex-col items-center justify-center py-12 text-center max-w-lg mx-auto">
        <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4 shadow-lg shadow-indigo-500/10">
          <Network className="w-7 h-7" />
        </div>

        <h3 className="font-serif text-lg font-semibold text-slate-100">
          Kinship & Social Knowledge Graph
        </h3>
        <p className="text-xs text-slate-400 mt-2 leading-relaxed">
          Interactive graph mapping authenticated kinship nodes, mentor-mentee connections, and shared biographical events.
        </p>

        {/* Mock Graph Nodes Preview */}
        <div className="mt-8 flex items-center justify-center gap-6 text-xs text-slate-300">
          <div className="flex flex-col items-center gap-1">
            <div className="w-10 h-10 rounded-full bg-indigo-600/30 border border-indigo-400 flex items-center justify-center font-bold text-xs text-indigo-200">
              AV
            </div>
            <span className="text-[10px] text-slate-400">Subject</span>
          </div>
          <div className="h-0.5 w-12 bg-indigo-500/40 relative">
            <span className="absolute -top-3 left-1/2 -translate-x-1/2 text-[9px] text-indigo-300 font-mono">
              Spouse
            </span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <div className="w-10 h-10 rounded-full bg-emerald-600/30 border border-emerald-400 flex items-center justify-center font-bold text-xs text-emerald-200">
              EV
            </div>
            <span className="text-[10px] text-slate-400">Arthur</span>
          </div>
          <div className="h-0.5 w-12 bg-indigo-500/40 relative">
            <span className="absolute -top-3 left-1/2 -translate-x-1/2 text-[9px] text-indigo-300 font-mono">
              Child
            </span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <div className="w-10 h-10 rounded-full bg-purple-600/30 border border-purple-400 flex items-center justify-center font-bold text-xs text-purple-200">
              TV
            </div>
            <span className="text-[10px] text-slate-400">Thomas</span>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-2 text-[11px] text-slate-500">
          <Shield className="w-3.5 h-3.5 text-indigo-400" />
          <span>Graph database abstraction ready (Neo4j / In-Memory NetworkX)</span>
        </div>
      </div>
    </div>
  );
};
