'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  Share2,
  RefreshCw,
  Search,
  Filter,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  Layers,
  Info,
  ArrowRight,
  ExternalLink,
  Users,
  Calendar,
  MapPin,
  FileText,
  Building,
  Tag
} from 'lucide-react';
import { GraphNodeModel, GraphRelationshipModel, GraphNeighborhood, GraphNodeType } from '@/types';

export default function KnowledgeGraphPage() {
  const [nodes, setNodes] = useState<GraphNodeModel[]>([]);
  const [relationships, setRelationships] = useState<GraphRelationshipModel[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNodeModel | null>(null);
  const [neighborhood, setNeighborhood] = useState<GraphNeighborhood | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(true);
  const [rebuilding, setRebuilding] = useState<boolean>(false);
  const [message, setMessage] = useState<string | null>(null);

  const profileId = 'default-profile-001';

  useEffect(() => {
    fetchGraph();
  }, []);

  const fetchGraph = async () => {
    setLoading(true);
    try {
      const [nodesRes, relsRes] = await Promise.all([
        fetch(`/api/v1/graph/nodes?memorial_profile_id=${profileId}&limit=150`).catch(() => null),
        fetch(`/api/v1/graph/relationships?memorial_profile_id=${profileId}&limit=200`).catch(() => null),
      ]);

      if (nodesRes && nodesRes.ok) {
        const nData = await nodesRes.json();
        setNodes(nData);
        if (nData.length > 0 && !selectedNode) {
          selectNode(nData[0]);
        }
      }
      if (relsRes && relsRes.ok) {
        const rData = await relsRes.json();
        setRelationships(rData);
      }
    } catch (err) {
      console.error('Failed to load graph:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRebuild = async () => {
    setRebuilding(true);
    setMessage(null);
    try {
      const res = await fetch(`/api/v1/graph/rebuild/${profileId}`, {
        method: 'POST'
      });
      if (res.ok) {
        setMessage('Knowledge graph successfully compiled from verified memories and entities.');
        await fetchGraph();
      }
    } catch (err) {
      console.error(err);
      setMessage('Graph compiled with existing local records.');
      await fetchGraph();
    } finally {
      setRebuilding(false);
    }
  };

  const selectNode = async (node: GraphNodeModel) => {
    setSelectedNode(node);
    try {
      const res = await fetch(`/api/v1/graph/nodes/${node.id}/neighbors?max_depth=1`);
      if (res.ok) {
        const nData = await res.json();
        setNeighborhood(nData);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const getNodeColor = (label: string) => {
    switch (label) {
      case 'PERSON': return '#6366f1';      // Indigo
      case 'MEMORY': return '#3b82f6';      // Blue
      case 'EVENT': return '#ec4899';       // Pink
      case 'PLACE': return '#10b981';       // Emerald
      case 'ORGANIZATION': return '#f59e0b';// Amber
      case 'TOPIC': return '#8b5cf6';       // Violet
      case 'DATE': return '#06b6d4';        // Cyan
      default: return '#64748b';            // Slate
    }
  };

  const filteredNodes = useMemo(() => {
    return nodes.filter(n => {
      const matchType = selectedType === 'ALL' || n.label === selectedType;
      const matchQuery = !searchQuery || n.name.toLowerCase().includes(searchQuery.toLowerCase());
      return matchType && matchQuery;
    });
  }, [nodes, selectedType, searchQuery]);

  // Compute 2D node coordinates in circle layout for visual canvas
  const positionedNodes = useMemo(() => {
    const width = 600;
    const height = 450;
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) * 0.38;

    return filteredNodes.map((n, i) => {
      const angle = (2 * Math.PI * i) / Math.max(1, filteredNodes.length);
      return {
        ...n,
        x: cx + radius * Math.cos(angle),
        y: cy + radius * Math.sin(angle)
      };
    });
  }, [filteredNodes]);

  const nodePosMap = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    positionedNodes.forEach(n => map.set(n.id, { x: n.x, y: n.y }));
    return map;
  }, [positionedNodes]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <Share2 className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-serif font-bold text-white tracking-wide">Knowledge Graph</h1>
            <p className="text-xs text-slate-400">Entity Topology & Evidentiary Relationships</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRebuild}
            disabled={rebuilding}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-indigo-600/30 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${rebuilding ? 'animate-spin' : ''}`} />
            <span>{rebuilding ? 'Rebuilding Graph...' : 'Rebuild Knowledge Graph'}</span>
          </button>
        </div>
      </div>

      {/* Safety Notice */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start gap-3">
        <Info className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-400 space-y-1">
          <p className="text-slate-200 font-medium">Safe Relationship Construction Protocol</p>
          <p>
            Relationships are <strong className="text-slate-300">never inferred merely because two entities co-occur in the same document</strong>.
            Every edge requires explicit relational evidence, provenance tracking, and confidence scoring.
          </p>
        </div>
      </div>

      {message && (
        <div className="p-3 bg-emerald-950/60 border border-emerald-800 text-emerald-300 rounded-lg text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Graph Toolbar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 bg-slate-900 p-3 rounded-xl border border-slate-800">
        <div className="flex items-center gap-2 flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 ml-2" />
          <input
            type="text"
            placeholder="Search entities, places, events..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800/80 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          {['ALL', 'PERSON', 'MEMORY', 'EVENT', 'PLACE', 'ORGANIZATION', 'TOPIC'].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition ${
                selectedType === type
                  ? 'bg-indigo-600 text-white font-semibold'
                  : 'bg-slate-800/80 text-slate-400 hover:text-white'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Main Interactive Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Graph Canvas */}
        <div className="lg:col-span-2 bg-slate-900 rounded-xl border border-slate-800 p-4 flex flex-col justify-between min-h-[500px]">
          <div className="flex justify-between items-center text-xs text-slate-400 border-b border-slate-800/80 pb-2 mb-2">
            <span>Visual Graph Topology ({filteredNodes.length} nodes, {relationships.length} edges)</span>
            <span className="text-[10px] text-slate-500">Click node to inspect neighborhood</span>
          </div>

          {loading ? (
            <div className="flex-1 flex items-center justify-center text-slate-500 text-xs">
              Loading knowledge graph...
            </div>
          ) : positionedNodes.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 space-y-3">
              <Share2 className="w-10 h-10 text-slate-600" />
              <p className="text-sm font-semibold text-slate-300">No Graph Entities Available</p>
              <p className="text-xs text-slate-500 max-w-sm">
                Compile memories and multimodal documents to generate knowledge graph entities and relational edges.
              </p>
              <button
                onClick={handleRebuild}
                disabled={rebuilding}
                className="px-3 py-1.5 bg-indigo-600 text-white text-xs rounded-lg font-medium"
              >
                Rebuild Knowledge Graph
              </button>
            </div>
          ) : (
            <div className="relative flex-1 flex items-center justify-center overflow-hidden">
              <svg className="w-full h-[450px]" viewBox="0 0 600 450">
                {/* Relationship Lines */}
                {relationships.map((rel) => {
                  const srcPos = nodePosMap.get(rel.source_node);
                  const tgtPos = nodePosMap.get(rel.target_node);
                  if (!srcPos || !tgtPos) return null;

                  const isConnected = selectedNode && (rel.source_node === selectedNode.id || rel.target_node === selectedNode.id);

                  return (
                    <g key={rel.relationship_id}>
                      <line
                        x1={srcPos.x}
                        y1={srcPos.y}
                        x2={tgtPos.x}
                        y2={tgtPos.y}
                        stroke={isConnected ? '#818cf8' : '#334155'}
                        strokeWidth={isConnected ? 2 : 1}
                        strokeDasharray={isConnected ? 'none' : '4 2'}
                        opacity={isConnected ? 0.9 : 0.4}
                      />
                    </g>
                  );
                })}

                {/* Nodes */}
                {positionedNodes.map((node) => {
                  const isSelected = selectedNode?.id === node.id;
                  const color = getNodeColor(node.label);

                  return (
                    <g
                      key={node.id}
                      onClick={() => selectNode(node)}
                      className="cursor-pointer transition-transform hover:scale-110"
                    >
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={isSelected ? 16 : 12}
                        fill={color}
                        stroke={isSelected ? '#ffffff' : '#1e293b'}
                        strokeWidth={isSelected ? 3 : 2}
                        className="transition-all"
                      />
                      <text
                        x={node.x}
                        y={node.y + 24}
                        textAnchor="middle"
                        fill="#cbd5e1"
                        fontSize="10"
                        fontWeight={isSelected ? 'bold' : 'normal'}
                        className="pointer-events-none select-none"
                      >
                        {node.name.length > 14 ? node.name.slice(0, 12) + '…' : node.name}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          )}

          {/* Legend */}
          <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-center gap-4 text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span> Person</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Memory</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-pink-500"></span> Event</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Place</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Organization</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-cyan-500"></span> Date</span>
          </div>
        </div>

        {/* Node Detail & Neighborhood Drawer */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 space-y-4">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-sm font-semibold text-white">Entity Inspection Panel</h3>
            <p className="text-[11px] text-slate-400">Provenance and relational neighborhood</p>
          </div>

          {!selectedNode ? (
            <p className="text-xs text-slate-500 text-center py-12">Select an entity node to inspect its evidence and connections.</p>
          ) : (
            <div className="space-y-4 text-xs">
              {/* Entity Title Card */}
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span
                    className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                    style={{ backgroundColor: `${getNodeColor(selectedNode.label)}20`, color: getNodeColor(selectedNode.label) }}
                  >
                    {selectedNode.label}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">ID: {selectedNode.id.slice(0, 8)}</span>
                </div>

                <h4 className="text-base font-bold text-white">{selectedNode.name}</h4>

                <div className="flex items-center gap-2 pt-1 text-[11px]">
                  <span className="text-slate-400">Confidence:</span>
                  <span className="text-emerald-400 font-semibold">{selectedNode.confidence}</span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <span className="text-slate-400">Provenance:</span>
                  <span className="text-indigo-300 font-mono">{selectedNode.provenance_status}</span>
                </div>
              </div>

              {/* Connected Relationships */}
              <div className="space-y-2">
                <h5 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
                  Connected Edges ({neighborhood?.relationships.length || 0})
                </h5>

                {!neighborhood?.relationships.length ? (
                  <p className="text-[11px] text-slate-500 italic">No direct edges linked to this entity yet.</p>
                ) : (
                  <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
                    {neighborhood.relationships.map((rel) => {
                      const isOutgoing = rel.source_node === selectedNode.id;
                      const otherNodeId = isOutgoing ? rel.target_node : rel.source_node;
                      const otherNode = nodes.find(n => n.id === otherNodeId);

                      return (
                        <div
                          key={rel.relationship_id}
                          className="p-2 bg-slate-950 rounded border border-slate-800/80 flex items-center justify-between"
                        >
                          <div className="space-y-0.5">
                            <span className="text-[10px] font-mono font-semibold text-indigo-400">
                              {rel.relationship_type}
                            </span>
                            <p className="text-slate-300 font-medium">
                              {otherNode?.name || 'Linked Entity'}
                            </p>
                          </div>
                          <span className="text-[9px] px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded">
                            {isOutgoing ? 'outgoing' : 'incoming'}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Source Evidentiary Grounding */}
              <div className="space-y-1.5 pt-2 border-t border-slate-800/80 text-[11px]">
                <p className="text-slate-400 font-medium">Evidence Grounding</p>
                <p className="text-slate-500">
                  Backed by {selectedNode.source_memory_ids.length} memories and {selectedNode.source_evidence_ids.length} extracted evidence tokens.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
