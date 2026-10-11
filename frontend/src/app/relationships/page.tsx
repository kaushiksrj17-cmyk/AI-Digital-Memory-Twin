'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Network,
  GitFork,
  Search,
  Filter,
  ShieldCheck,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Merge,
  Table as TableIcon,
  Layers,
  CheckCircle2,
  XCircle,
  FileText,
  Users,
  Building,
  MapPin,
  Calendar,
  Sparkles,
  ChevronRight,
  Eye,
  Info
} from 'lucide-react';
import {
  RelationshipGraphResponse,
  RelationshipDetail,
  RelationshipGraphNode,
  DuplicateEntityCandidate,
  VerificationStatus
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export default function RelationshipsPage() {
  const [graphData, setGraphData] = useState<RelationshipGraphResponse | null>(null);
  const [duplicateCandidates, setDuplicateCandidates] = useState<DuplicateEntityCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & View state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRelType, setSelectedRelType] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [viewMode, setViewMode] = useState<'graph' | 'table'>('graph');

  // Inspection Drawer
  const [selectedNode, setSelectedNode] = useState<RelationshipGraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<RelationshipDetail | null>(null);

  // Merge workflow state
  const [showMergeModal, setShowMergeModal] = useState<boolean>(false);
  const [activeDuplicate, setActiveDuplicate] = useState<DuplicateEntityCandidate | null>(null);
  const [mergeNotes, setMergeNotes] = useState<string>('');
  const [isMerging, setIsMerging] = useState<boolean>(false);

  // Graph Zoom & Pan
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('memorial_profile_id', 'demo-profile-001');
      if (selectedRelType) params.append('relationship_type', selectedRelType);
      if (selectedStatus) params.append('verification_status', selectedStatus);
      if (searchQuery) params.append('search_query', searchQuery);

      const res = await fetch(`${API_BASE}/relationships/?${params.toString()}`);
      if (!res.ok) throw new Error(`Failed to load relationships: ${res.statusText}`);
      const data: RelationshipGraphResponse = await res.json();
      setGraphData(data);

      // Fetch duplicate candidates
      const dupRes = await fetch(`${API_BASE}/relationships/duplicates?memorial_profile_id=demo-profile-001`);
      if (dupRes.ok) {
        const dups = await dupRes.json();
        setDuplicateCandidates(dups);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error communicating with backend relationship service');
    } finally {
      setLoading(false);
    }
  }, [selectedRelType, selectedStatus, searchQuery]);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  // Handle Edge Verification
  const handleVerifyEdge = async (edgeId: string, status: VerificationStatus) => {
    try {
      const res = await fetch(`${API_BASE}/relationships/${edgeId}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-role': 'FAMILY_ADMIN'
        },
        body: JSON.stringify({
          verification_status: status,
          notes: 'Reviewed and confirmed against primary archival evidence.'
        })
      });
      if (!res.ok) throw new Error('Verification failed');
      await fetchGraph();
      if (selectedEdge && selectedEdge.id === edgeId) {
        const updated = await res.json();
        setSelectedEdge(updated);
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Handle Merge Execution
  const handleExecuteMerge = async () => {
    if (!activeDuplicate) return;
    setIsMerging(true);
    try {
      const res = await fetch(`${API_BASE}/relationships/merge-duplicates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-role': 'FAMILY_ADMIN'
        },
        body: JSON.stringify({
          canonical_entity_id: activeDuplicate.suggested_canonical_id,
          duplicate_entity_id:
            activeDuplicate.suggested_canonical_id === activeDuplicate.entity_a_id
              ? activeDuplicate.entity_b_id
              : activeDuplicate.entity_a_id,
          merge_notes: mergeNotes || 'Approved canonical entity consolidation via Family Portal.'
        })
      });
      if (!res.ok) throw new Error('Merge execution failed');
      setShowMergeModal(false);
      setActiveDuplicate(null);
      setMergeNotes('');
      await fetchGraph();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsMerging(false);
    }
  };

  // Node Icon Helper
  const getNodeIcon = (label: string) => {
    switch (label.toUpperCase()) {
      case 'PERSON':
        return <Users className="w-3.5 h-3.5" />;
      case 'ORGANIZATION':
        return <Building className="w-3.5 h-3.5" />;
      case 'PLACE':
        return <MapPin className="w-3.5 h-3.5" />;
      case 'EVENT':
        return <Calendar className="w-3.5 h-3.5" />;
      case 'MEMORY':
      default:
        return <Sparkles className="w-3.5 h-3.5" />;
    }
  };

  // Node Color Helper
  const getNodeColor = (label: string) => {
    switch (label.toUpperCase()) {
      case 'PERSON':
        return 'border-indigo-500 bg-indigo-950/80 text-indigo-300';
      case 'ORGANIZATION':
        return 'border-amber-500 bg-amber-950/80 text-amber-300';
      case 'PLACE':
        return 'border-emerald-500 bg-emerald-950/80 text-emerald-300';
      case 'EVENT':
        return 'border-sky-500 bg-sky-950/80 text-sky-300';
      case 'MEMORY':
      default:
        return 'border-purple-500 bg-purple-950/80 text-purple-300';
    }
  };

  // Force-directed layout calculation for SVG rendering
  const layoutNodes = useMemo(() => {
    if (!graphData?.nodes) return [];
    const count = graphData.nodes.length;
    const radius = Math.min(260, 50 + count * 35);
    const centerX = 400;
    const centerY = 280;

    return graphData.nodes.map((node, idx) => {
      // Put subject in center
      if (node.id === 'demo-profile-001' || node.name.toLowerCase().includes('subject')) {
        return { ...node, x: centerX, y: centerY };
      }
      const angle = (idx / (count - 1 || 1)) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      return { ...node, x, y };
    });
  }, [graphData]);

  const nodePositions = useMemo(() => {
    const map: Record<string, { x: number; y: number }> = {};
    layoutNodes.forEach((n) => {
      map[n.id] = { x: n.x, y: n.y };
    });
    return map;
  }, [layoutNodes]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 w-full space-y-6 animate-fadeIn">
      {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-950/40 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Top Metric Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-slate-400">Total Graph Entities</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold font-serif text-white">
                {graphData?.total_nodes ?? 0}
              </span>
              <span className="text-[10px] text-indigo-400">Archival Nodes</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-slate-400">Evidence-Backed Edges</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold font-serif text-emerald-400">
                {graphData?.verified_edges_count ?? 0}
              </span>
              <span className="text-[10px] text-slate-400">Certified Grounding</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-slate-400">Contested Connections</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold font-serif text-amber-400">
                {graphData?.disputed_edges_count ?? 0}
              </span>
              <span className="text-[10px] text-amber-500/80">Multiple Perspectives</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
            <span className="text-[11px] font-medium text-slate-400">Duplicate Entity Candidates</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold font-serif text-sky-400">
                {duplicateCandidates.length}
              </span>
              <span className="text-[10px] text-slate-400">Review &amp; Merge</span>
            </div>
          </div>
        </div>

        {/* Duplicate Entity Banner (if any) */}
        {duplicateCandidates.length > 0 && (
          <div className="p-4 rounded-2xl border border-indigo-500/30 bg-indigo-950/30 flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 text-indigo-200">
              <Merge className="w-4 h-4 text-indigo-400" />
              <span>
                <strong>{duplicateCandidates.length} potential duplicate entity candidate(s)</strong> detected.
                Consolidate variations to prevent fragmented memory associations.
              </span>
            </div>
            <button
              onClick={() => {
                setActiveDuplicate(duplicateCandidates[0]);
                setShowMergeModal(true);
              }}
              className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-md shadow-indigo-600/20"
            >
              Review &amp; Merge Candidates
            </button>
          </div>
        )}

        {/* Controls Toolbar */}
        <div className="p-4 rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-md flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
            {/* Search Input */}
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search entities, kinship roles, or evidence notes..."
                className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Relationship Type Filter */}
            <select
              value={selectedRelType}
              onChange={(e) => setSelectedRelType(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Relationships</option>
              <option value="PARENT_OF">Parent of</option>
              <option value="CHILD_OF">Child of</option>
              <option value="SPOUSE_OF">Spouse of</option>
              <option value="FRIEND_OF">Friend of</option>
              <option value="STUDIED_AT">Studied at</option>
              <option value="WORKED_AT">Worked at</option>
              <option value="VISITED">Visited</option>
              <option value="CONNECTED_TO_MEMORY">Connected to Memory</option>
            </select>

            {/* Verification Status Filter */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Verification States</option>
              <option value="VERIFIED">Verified</option>
              <option value="PENDING_REVIEW">Pending Review</option>
              <option value="DISPUTED">Disputed</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            {/* View Mode Toggle */}
            <div className="p-1 rounded-xl border border-slate-700 bg-slate-800 flex items-center">
              <button
                onClick={() => setViewMode('graph')}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                  viewMode === 'graph' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Network className="w-3.5 h-3.5" />
                <span>Graph View</span>
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                  viewMode === 'table' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <TableIcon className="w-3.5 h-3.5" />
                <span>Table Fallback</span>
              </button>
            </div>
          </div>
        </div>

        {/* Content Area: Graph Canvas or Table Fallback */}
        {loading ? (
          <div className="py-24 text-center space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin mx-auto" />
            <p className="text-xs text-slate-400">Traversing evidence-grounded relationship graph...</p>
          </div>
        ) : viewMode === 'graph' ? (
          <div className="relative rounded-2xl border border-slate-800 bg-slate-900/40 overflow-hidden h-[620px] flex">
            {/* SVG Interactive Canvas */}
            <div
              className="flex-1 h-full relative cursor-grab active:cursor-grabbing select-none"
              onMouseDown={(e) => {
                setIsDragging(true);
                setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
              }}
              onMouseMove={(e) => {
                if (isDragging) {
                  setPanOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
                }
              }}
              onMouseUp={() => setIsDragging(false)}
              onMouseLeave={() => setIsDragging(false)}
            >
              {/* Zoom Controls */}
              <div className="absolute top-4 left-4 z-20 flex flex-col gap-1.5 p-1.5 rounded-xl border border-slate-800 bg-slate-900/90 shadow-lg">
                <button
                  onClick={() => setZoomLevel((z) => Math.min(z + 0.2, 2.5))}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white"
                  title="Zoom In"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setZoomLevel((z) => Math.max(z - 0.2, 0.5))}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    setZoomLevel(1);
                    setPanOffset({ x: 0, y: 0 });
                  }}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white"
                  title="Reset View"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>

              {/* Background Grid Pattern */}
              <svg className="w-full h-full pointer-events-none absolute inset-0">
                <defs>
                  <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                    <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" strokeWidth="0.5" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
              </svg>

              {/* Graph SVG Rendering */}
              <svg
                className="w-full h-full absolute inset-0"
                style={{
                  transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                  transformOrigin: '400px 280px',
                  transition: isDragging ? 'none' : 'transform 0.1s ease-out'
                }}
              >
                {/* Edges */}
                {graphData?.edges.map((edge) => {
                  const srcPos = nodePositions[edge.source_entity_id];
                  const tgtPos = nodePositions[edge.target_entity_id];
                  if (!srcPos || !tgtPos) return null;

                  const isSelected = selectedEdge?.id === edge.id;
                  const isEdgeDisputed = edge.is_disputed;

                  const strokeColor = isSelected
                    ? '#818cf8'
                    : isEdgeDisputed
                    ? '#f59e0b'
                    : '#475569';

                  const strokeWidth = isSelected ? 3 : 1.5;
                  const strokeDasharray = isEdgeDisputed ? '4,4' : undefined;

                  const midX = (srcPos.x + tgtPos.x) / 2;
                  const midY = (srcPos.y + tgtPos.y) / 2;

                  return (
                    <g
                      key={edge.id}
                      className="cursor-pointer group"
                      onClick={() => {
                        setSelectedEdge(edge);
                        setSelectedNode(null);
                      }}
                    >
                      <line
                        x1={srcPos.x}
                        y1={srcPos.y}
                        x2={tgtPos.x}
                        y2={tgtPos.y}
                        stroke={strokeColor}
                        strokeWidth={strokeWidth}
                        strokeDasharray={strokeDasharray}
                        className="transition-all group-hover:stroke-indigo-400 group-hover:stroke-[2.5]"
                      />
                      {/* Edge Label Pill */}
                      <g transform={`translate(${midX}, ${midY})`}>
                        <rect
                          x="-42"
                          y="-9"
                          width="84"
                          height="18"
                          rx="9"
                          fill="#0f172a"
                          stroke={strokeColor}
                          strokeWidth="1"
                        />
                        <text
                          textAnchor="middle"
                          dy="3.5"
                          className="text-[9px] font-mono fill-slate-300 font-medium tracking-tight pointer-events-none"
                        >
                          {edge.relationship_type.replace(/_/g, ' ')}
                        </text>
                      </g>
                    </g>
                  );
                })}

                {/* Nodes */}
                {layoutNodes.map((node) => {
                  const isSelected = selectedNode?.id === node.id;
                  return (
                    <g
                      key={node.id}
                      transform={`translate(${node.x}, ${node.y})`}
                      className="cursor-pointer group"
                      onClick={() => {
                        setSelectedNode(node);
                        setSelectedEdge(null);
                      }}
                    >
                      <circle
                        r={isSelected ? 26 : 22}
                        className={`transition-all duration-200 stroke-2 ${
                          isSelected
                            ? 'stroke-indigo-400 fill-indigo-900/90'
                            : 'stroke-slate-700 fill-slate-900 group-hover:stroke-indigo-500'
                        }`}
                      />
                      {/* Inner Node Text / Initial */}
                      <text
                        textAnchor="middle"
                        dy="4"
                        className="text-[10px] font-bold fill-white pointer-events-none font-sans"
                      >
                        {node.name.slice(0, 2).toUpperCase()}
                      </text>
                      {/* Node Label Below */}
                      <text
                        textAnchor="middle"
                        dy="36"
                        className="text-[10px] fill-slate-300 font-serif font-medium pointer-events-none drop-shadow-md"
                      >
                        {node.name.length > 18 ? node.name.slice(0, 16) + '…' : node.name}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Inspection Side Panel */}
            <div className="w-80 border-l border-slate-800 bg-slate-900/90 p-5 overflow-y-auto space-y-4">
              {selectedEdge ? (
                <div className="space-y-4 animate-in fade-in">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <span className="text-xs font-semibold text-indigo-400 flex items-center gap-1.5">
                      <GitFork className="w-4 h-4" />
                      Relationship Edge
                    </span>
                    <button
                      onClick={() => setSelectedEdge(null)}
                      className="text-slate-400 hover:text-white text-xs"
                    >
                      ✕
                    </button>
                  </div>

                  <div>
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">
                      Connection
                    </span>
                    <h4 className="font-serif text-sm font-bold text-white mt-0.5">
                      {selectedEdge.source_entity_name} → {selectedEdge.target_entity_name}
                    </h4>
                    <span className="inline-block mt-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                      {selectedEdge.relationship_type}
                    </span>
                  </div>

                  {selectedEdge.description && (
                    <div className="space-y-1">
                      <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">
                        Description
                      </span>
                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-800/40 p-2.5 rounded-xl border border-slate-800">
                        {selectedEdge.description}
                      </p>
                    </div>
                  )}

                  {/* Evidentiary Citations */}
                  <div className="space-y-2">
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">
                      Archival Evidence
                    </span>
                    {selectedEdge.source_evidence_ids.length > 0 ? (
                      <div className="space-y-1.5">
                        {selectedEdge.source_evidence_ids.map((evId) => (
                          <div
                            key={evId}
                            className="p-2 rounded-lg border border-slate-800 bg-slate-800/50 flex items-center gap-2 text-xs text-slate-300"
                          >
                            <FileText className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="font-mono text-[11px]">{evId}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No direct document IDs referenced.</p>
                    )}
                  </div>

                  {/* Status & Verification */}
                  <div className="space-y-1 pt-2 border-t border-slate-800 text-xs">
                    <div className="flex justify-between py-1">
                      <span className="text-slate-400">Confidence:</span>
                      <span className="font-semibold text-emerald-400">{selectedEdge.confidence}</span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span className="text-slate-400">Status:</span>
                      <span className="font-semibold text-slate-200">{selectedEdge.verification_status}</span>
                    </div>
                  </div>

                  {/* Verification Actions */}
                  {selectedEdge.verification_status === 'PENDING_REVIEW' && (
                    <div className="pt-2 flex gap-2">
                      <button
                        onClick={() => handleVerifyEdge(selectedEdge.id, 'VERIFIED')}
                        className="flex-1 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                      >
                        Verify Edge
                      </button>
                      <button
                        onClick={() => handleVerifyEdge(selectedEdge.id, 'REJECTED')}
                        className="px-3 py-1.5 rounded-xl border border-rose-800 text-rose-300 hover:bg-rose-950 text-xs"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              ) : selectedNode ? (
                <div className="space-y-4 animate-in fade-in">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <span className="text-xs font-semibold text-indigo-400 flex items-center gap-1.5">
                      {getNodeIcon(selectedNode.label)}
                      <span>Entity Node Details</span>
                    </span>
                    <button
                      onClick={() => setSelectedNode(null)}
                      className="text-slate-400 hover:text-white text-xs"
                    >
                      ✕
                    </button>
                  </div>

                  <div>
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">
                      Entity Name
                    </span>
                    <h4 className="font-serif text-base font-bold text-white mt-0.5">
                      {selectedNode.name}
                    </h4>
                    <span className="inline-block mt-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                      Type: {selectedNode.label}
                    </span>
                  </div>

                  {/* Connected Edges */}
                  <div className="space-y-2">
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">
                      Connected Relationships
                    </span>
                    <div className="space-y-1.5">
                      {graphData?.edges
                        .filter(
                          (e) =>
                            e.source_entity_id === selectedNode.id ||
                            e.target_entity_id === selectedNode.id
                        )
                        .map((edge) => (
                          <div
                            key={edge.id}
                            onClick={() => setSelectedEdge(edge)}
                            className="p-2 rounded-lg border border-slate-800 bg-slate-800/40 hover:bg-slate-800 cursor-pointer text-xs space-y-1 transition-colors"
                          >
                            <div className="font-semibold text-slate-200 flex items-center justify-between">
                              <span>{edge.relationship_type}</span>
                              <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                            </div>
                            <span className="text-[11px] text-slate-400">
                              {edge.source_entity_name === selectedNode.name
                                ? `→ ${edge.target_entity_name}`
                                : `← ${edge.source_entity_name}`}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-20 text-center space-y-3">
                  <Info className="w-8 h-8 text-slate-600 mx-auto" />
                  <p className="text-xs text-slate-400">
                    Click any node or relationship edge in the graph canvas to inspect grounded archival evidence.
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Table Fallback View */
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/80 text-slate-400 font-mono uppercase text-[10px]">
                    <th className="p-3.5">Source Entity</th>
                    <th className="p-3.5">Relationship</th>
                    <th className="p-3.5">Target Entity</th>
                    <th className="p-3.5">Confidence</th>
                    <th className="p-3.5">Status</th>
                    <th className="p-3.5">Evidence IDs</th>
                    <th className="p-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-200">
                  {graphData?.edges.map((edge) => (
                    <tr key={edge.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-3.5 font-semibold text-white">{edge.source_entity_name}</td>
                      <td className="p-3.5 font-mono text-indigo-400">{edge.relationship_type}</td>
                      <td className="p-3.5 font-semibold text-white">{edge.target_entity_name}</td>
                      <td className="p-3.5">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            edge.confidence === 'VERIFIED'
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                              : 'bg-amber-950 text-amber-300 border border-amber-500/40'
                          }`}
                        >
                          {edge.confidence}
                        </span>
                      </td>
                      <td className="p-3.5">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                            edge.is_disputed
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                              : edge.verification_status === 'VERIFIED'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : 'bg-sky-500/10 text-sky-400 border border-sky-500/30'
                          }`}
                        >
                          {edge.is_disputed ? 'DISPUTED' : edge.verification_status}
                        </span>
                      </td>
                      <td className="p-3.5 font-mono text-slate-400 text-[11px]">
                        {edge.source_evidence_ids.join(', ') || '—'}
                      </td>
                      <td className="p-3.5 text-right">
                        <button
                          onClick={() => {
                            setSelectedEdge(edge);
                            setViewMode('graph');
                          }}
                          className="px-2.5 py-1 rounded-lg border border-slate-700 hover:border-indigo-500 text-slate-300 hover:text-white"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

      {/* Duplicate Entity Merge Modal */}
      {showMergeModal && activeDuplicate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="font-serif text-base font-bold text-white flex items-center gap-2">
                <Merge className="w-4 h-4 text-indigo-400" />
                <span>Review &amp; Merge Duplicate Entities</span>
              </h3>
              <button onClick={() => setShowMergeModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Consolidate duplicate mentions into one canonical record. All existing relationship edges will be
              automatically re-routed to the selected canonical entity without losing archival evidence.
            </p>

            <div className="p-4 rounded-xl border border-slate-800 bg-slate-800/40 space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Candidate A</span>
                  <div className="font-bold text-white text-sm">{activeDuplicate.entity_a_name}</div>
                  <span className="text-[10px] text-slate-500">ID: {activeDuplicate.entity_a_id}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Candidate B</span>
                  <div className="font-bold text-white text-sm">{activeDuplicate.entity_b_name}</div>
                  <span className="text-[10px] text-slate-500">ID: {activeDuplicate.entity_b_id}</span>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                <span>Similarity Match: <strong>{activeDuplicate.similarity_score * 100}%</strong></span>
                <span>Recommended Canonical: <strong>{activeDuplicate.suggested_canonical_id}</strong></span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Merge Audit Justification Notes
              </label>
              <textarea
                rows={2}
                value={mergeNotes}
                onChange={(e) => setMergeNotes(e.target.value)}
                placeholder="Reason for confirming these entities refer to the same individual or institution..."
                className="w-full p-2.5 rounded-xl border border-slate-700 bg-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowMergeModal(false)}
                className="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-300 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isMerging}
                onClick={handleExecuteMerge}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
              >
                {isMerging ? 'Merging...' : 'Confirm & Re-route Edges'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
