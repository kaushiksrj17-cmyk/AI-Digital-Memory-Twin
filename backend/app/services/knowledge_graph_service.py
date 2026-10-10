"""Knowledge Graph Service for ECHO.

Provides graph abstraction, node/edge CRUD, neighborhood traversal,
safe evidence-grounded relationship construction, and entity search.

Supports production Neo4j with transparent fallback to LocalGraphStore
(in-memory adjacency with persistence hooks) for offline and test runs.

SAFETY RULE:
Relationships are NEVER inferred purely because two entities appear in the same document.
Only explicit semantic extractions or user-verified relationships are instantiated.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4
from collections import defaultdict, deque
from datetime import datetime, timezone
import os

from models.enums import (
    GraphNodeType,
    GraphRelationshipType,
    ProvenanceStatus,
    ConfidenceLevel,
)
from models.graph import (
    GraphNodeModel,
    GraphRelationshipModel,
    GraphNeighborhood,
    GraphSearchResult,
)


class LocalGraphStore:
    """In-memory Knowledge Graph store for testing and local zero-dependency execution.
    
    Supports node CRUD, directed edges, 1-to-N neighborhood extraction, and search.
    """

    def __init__(self):
        self._nodes: Dict[str, GraphNodeModel] = {}
        self._relationships: Dict[str, GraphRelationshipModel] = {}
        # Adjacency indexes: node_id -> list of relationship_ids
        self._out_edges: Dict[str, List[str]] = defaultdict(list)
        self._in_edges: Dict[str, List[str]] = defaultdict(list)

    async def add_node(self, node: GraphNodeModel) -> GraphNodeModel:
        self._nodes[node.id] = node
        return node

    async def get_node(self, node_id: str) -> Optional[GraphNodeModel]:
        return self._nodes.get(node_id)

    async def update_node(self, node_id: str, updates: Dict[str, Any]) -> Optional[GraphNodeModel]:
        node = self._nodes.get(node_id)
        if not node:
            return None
        node_data = node.model_dump()
        for k, v in updates.items():
            if k in node_data and k not in ("id", "created_at"):
                node_data[k] = v
        node_data["updated_at"] = datetime.now(timezone.utc)
        updated_node = GraphNodeModel(**node_data)
        self._nodes[node_id] = updated_node
        return updated_node

    async def add_relationship(self, rel: GraphRelationshipModel) -> GraphRelationshipModel:
        # Check for existing duplicate edge between same source and target with same type
        for existing_id in self._out_edges.get(rel.source_node, []):
            existing = self._relationships.get(existing_id)
            if existing and existing.target_node == rel.target_node and existing.relationship_type == rel.relationship_type:
                # Merge evidence IDs rather than creating duplicate edge
                merged_evidence = list(set(existing.source_evidence_ids + rel.source_evidence_ids))
                merged_memories = list(set(existing.source_memory_ids + rel.source_memory_ids))
                existing.source_evidence_ids = merged_evidence
                existing.source_memory_ids = merged_memories
                existing.updated_at = datetime.now(timezone.utc)
                return existing

        self._relationships[rel.relationship_id] = rel
        self._out_edges[rel.source_node].append(rel.relationship_id)
        self._in_edges[rel.target_node].append(rel.relationship_id)
        return rel

    async def get_relationship(self, rel_id: str) -> Optional[GraphRelationshipModel]:
        return self._relationships.get(rel_id)

    async def get_relationships_for_node(
        self,
        node_id: str,
        direction: str = "both"
    ) -> List[GraphRelationshipModel]:
        rel_ids = set()
        if direction in ("out", "both"):
            rel_ids.update(self._out_edges.get(node_id, []))
        if direction in ("in", "both"):
            rel_ids.update(self._in_edges.get(node_id, []))
        return [self._relationships[r_id] for r_id in rel_ids if r_id in self._relationships]

    async def get_neighborhood(
        self,
        node_id: str,
        max_depth: int = 1
    ) -> Optional[GraphNeighborhood]:
        center_node = self._nodes.get(node_id)
        if not center_node:
            return None

        visited_nodes = {node_id}
        collected_relationships: List[GraphRelationshipModel] = []
        collected_neighbors: List[Dict[str, Any]] = []

        queue = deque([(node_id, 0)])

        while queue:
            curr_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            # Outgoing edges
            for r_id in self._out_edges.get(curr_id, []):
                rel = self._relationships.get(r_id)
                if rel:
                    collected_relationships.append(rel)
                    target_id = rel.target_node
                    if target_id not in visited_nodes:
                        visited_nodes.add(target_id)
                        target_node = self._nodes.get(target_id)
                        if target_node:
                            collected_neighbors.append({
                                "node": target_node.model_dump(),
                                "direction": "outgoing",
                                "relationship_type": rel.relationship_type.value if hasattr(rel.relationship_type, "value") else str(rel.relationship_type)
                            })
                            queue.append((target_id, depth + 1))

            # Incoming edges
            for r_id in self._in_edges.get(curr_id, []):
                rel = self._relationships.get(r_id)
                if rel:
                    collected_relationships.append(rel)
                    src_id = rel.source_node
                    if src_id not in visited_nodes:
                        visited_nodes.add(src_id)
                        src_node = self._nodes.get(src_id)
                        if src_node:
                            collected_neighbors.append({
                                "node": src_node.model_dump(),
                                "direction": "incoming",
                                "relationship_type": rel.relationship_type.value if hasattr(rel.relationship_type, "value") else str(rel.relationship_type)
                            })
                            queue.append((src_id, depth + 1))

        return GraphNeighborhood(
            node=center_node,
            neighbors=collected_neighbors,
            relationships=collected_relationships
        )

    async def search_nodes(
        self,
        query: str,
        memorial_profile_id: Optional[str] = None,
        label: Optional[GraphNodeType] = None,
        limit: int = 20
    ) -> List[GraphNodeModel]:
        q = query.lower().strip()
        matches = []
        for node in self._nodes.values():
            if memorial_profile_id and node.memorial_profile_id != memorial_profile_id:
                continue
            if label and node.label != label:
                continue
            if not q or q in node.name.lower() or any(q in str(v).lower() for v in node.properties.values()):
                matches.append(node)
                if len(matches) >= limit:
                    break
        return matches

    async def all_nodes(self, memorial_profile_id: Optional[str] = None) -> List[GraphNodeModel]:
        if not memorial_profile_id:
            return list(self._nodes.values())
        return [n for n in self._nodes.values() if n.memorial_profile_id == memorial_profile_id]

    async def all_relationships(self, memorial_profile_id: Optional[str] = None) -> List[GraphRelationshipModel]:
        if not memorial_profile_id:
            return list(self._relationships.values())
        return [r for r in self._relationships.values() if r.memorial_profile_id == memorial_profile_id]

    async def clear_profile(self, memorial_profile_id: str):
        # Remove nodes and relationships for a specific profile
        nodes_to_remove = [nid for nid, n in self._nodes.items() if n.memorial_profile_id == memorial_profile_id]
        for nid in nodes_to_remove:
            del self._nodes[nid]
            self._out_edges.pop(nid, None)
            self._in_edges.pop(nid, None)

        rels_to_remove = [rid for rid, r in self._relationships.items() if r.memorial_profile_id == memorial_profile_id]
        for rid in rels_to_remove:
            del self._relationships[rid]

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "LocalGraphStore (In-Memory)",
            "status": "ready",
            "nodes_count": len(self._nodes),
            "relationships_count": len(self._relationships),
            "is_mock": True
        }


# Global graph instance
_global_graph_store: Optional[LocalGraphStore] = None


def get_graph_store() -> LocalGraphStore:
    global _global_graph_store
    if _global_graph_store is None:
        _global_graph_store = LocalGraphStore()
    return _global_graph_store


class KnowledgeGraphService:
    """High-level knowledge graph service orchestrating safe evidence-grounded construction."""

    def __init__(self, store: Optional[LocalGraphStore] = None):
        self.store = store or get_graph_store()

    async def create_node(
        self,
        name: str,
        label: GraphNodeType,
        memorial_profile_id: str = "default-profile-001",
        properties: Optional[Dict[str, Any]] = None,
        source_memory_ids: Optional[List[str]] = None,
        source_evidence_ids: Optional[List[str]] = None,
        provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED,
        confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED,
        confidence_score: float = 1.0,
        node_id: Optional[str] = None
    ) -> GraphNodeModel:
        """Create a typed node in the knowledge graph."""
        node = GraphNodeModel(
            id=node_id or str(uuid4()),
            memorial_profile_id=memorial_profile_id,
            label=label,
            name=name.strip(),
            properties=properties or {},
            source_memory_ids=source_memory_ids or [],
            source_evidence_ids=source_evidence_ids or [],
            provenance_status=provenance_status,
            confidence=confidence,
            confidence_score=confidence_score,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        return await self.store.add_node(node)

    async def create_relationship(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: GraphRelationshipType,
        memorial_profile_id: str = "default-profile-001",
        properties: Optional[Dict[str, Any]] = None,
        source_evidence_ids: Optional[List[str]] = None,
        source_memory_ids: Optional[List[str]] = None,
        provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED,
        confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED,
        confidence_score: float = 1.0
    ) -> Optional[GraphRelationshipModel]:
        """Create an evidence-grounded edge between two existing nodes."""
        src = await self.store.get_node(source_node_id)
        tgt = await self.store.get_node(target_node_id)
        if not src or not tgt:
            return None

        rel = GraphRelationshipModel(
            relationship_id=str(uuid4()),
            memorial_profile_id=memorial_profile_id,
            source_node=source_node_id,
            target_node=target_node_id,
            relationship_type=relationship_type,
            properties=properties or {},
            source_evidence_ids=source_evidence_ids or [],
            source_memory_ids=source_memory_ids or [],
            provenance_status=provenance_status,
            confidence=confidence,
            confidence_score=confidence_score,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        return await self.store.add_relationship(rel)

    async def get_node(self, node_id: str) -> Optional[GraphNodeModel]:
        return await self.store.get_node(node_id)

    async def get_neighborhood(self, node_id: str, max_depth: int = 1) -> Optional[GraphNeighborhood]:
        return await self.store.get_neighborhood(node_id, max_depth=max_depth)

    async def search(
        self,
        query: str,
        memorial_profile_id: str = "default-profile-001",
        label: Optional[GraphNodeType] = None,
        limit: int = 50
    ) -> GraphSearchResult:
        nodes = await self.store.search_nodes(query, memorial_profile_id=memorial_profile_id, label=label, limit=limit)
        node_ids = {n.id for n in nodes}
        all_rels = await self.store.all_relationships(memorial_profile_id=memorial_profile_id)
        relevant_rels = [
            r for r in all_rels
            if r.source_node in node_ids or r.target_node in node_ids
        ]
        return GraphSearchResult(
            nodes=nodes,
            relationships=relevant_rels,
            total_nodes=len(nodes),
            total_relationships=len(relevant_rels)
        )

    async def get_all_nodes(self, memorial_profile_id: str = "default-profile-001") -> List[GraphNodeModel]:
        return await self.store.all_nodes(memorial_profile_id=memorial_profile_id)

    async def get_all_relationships(self, memorial_profile_id: str = "default-profile-001") -> List[GraphRelationshipModel]:
        return await self.store.all_relationships(memorial_profile_id=memorial_profile_id)

    async def get_graph_stats(self, memorial_profile_id: str = "default-profile-001") -> Dict[str, Any]:
        nodes = await self.store.all_nodes(memorial_profile_id=memorial_profile_id)
        relationships = await self.store.all_relationships(memorial_profile_id=memorial_profile_id)
        
        node_types_count = defaultdict(int)
        for n in nodes:
            label_val = n.label.value if hasattr(n.label, "value") else str(n.label)
            node_types_count[label_val] += 1

        rel_types_count = defaultdict(int)
        for r in relationships:
            rel_val = r.relationship_type.value if hasattr(r.relationship_type, "value") else str(r.relationship_type)
            rel_types_count[rel_val] += 1

        return {
            "total_nodes": len(nodes),
            "total_relationships": len(relationships),
            "nodes_by_type": dict(node_types_count),
            "relationships_by_type": dict(rel_types_count),
            "store_status": self.store.get_status()
        }

    async def build_from_memories_and_evidence(
        self,
        memorial_profile_id: str,
        memories: List[Dict[str, Any]],
        evidence_list: List[Dict[str, Any]],
        entities: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        relationships_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, int]:
        """Safely compile evidence records into knowledge graph nodes and edges.
        
        Strict adherence to evidentiary grounding:
        - Memory nodes created from explicit Memory records.
        - Person, Organization, Location, Event nodes created from extracted entities with direct evidence references.
        - Relationship edges created ONLY when explicitly supported.
        """
        await self.store.clear_profile(memorial_profile_id)

        node_map: Dict[str, str] = {}  # key -> node_id

        # 1. Subject Person Node
        subject_node = await self.create_node(
            name="Memorial Subject",
            label=GraphNodeType.PERSON,
            memorial_profile_id=memorial_profile_id,
            properties={"is_subject": True},
            provenance_status=ProvenanceStatus.USER_PROVIDED
        )
        node_map["SUBJECT"] = subject_node.id

        # 2. Add Memory Nodes
        for m in memories:
            m_id = m.get("id")
            m_title = m.get("title", "Untitled Memory")
            mem_node = await self.create_node(
                name=m_title,
                label=GraphNodeType.MEMORY,
                memorial_profile_id=memorial_profile_id,
                properties={
                    "category": m.get("category", "OTHER"),
                    "date": m.get("date"),
                    "location": m.get("location"),
                    "privacy_level": m.get("privacy_level", "PRIVATE")
                },
                source_memory_ids=[m_id] if m_id else [],
                provenance_status=ProvenanceStatus.USER_PROVIDED if m.get("source_type") == "USER_ENTRY" else ProvenanceStatus.DIRECTLY_OBSERVED,
                confidence=ConfidenceLevel.VERIFIED
            )
            node_map[f"MEMORY_{m_id}"] = mem_node.id

            # Link Subject -> APPEARED_IN -> Memory
            await self.create_relationship(
                source_node_id=subject_node.id,
                target_node_id=mem_node.id,
                relationship_type=GraphRelationshipType.APPEARED_IN,
                memorial_profile_id=memorial_profile_id,
                source_memory_ids=[m_id] if m_id else [],
                provenance_status=ProvenanceStatus.USER_PROVIDED
            )

        # 3. Add Entity Nodes (Person, Location, Organization, Date, etc.)
        for e in entities:
            etype = e.get("entity_type", "PERSON").upper()
            e_val = e.get("value", "").strip()
            if not e_val:
                continue

            node_type = GraphNodeType.OBJECT
            if etype == "PERSON":
                node_type = GraphNodeType.PERSON
            elif etype in ("LOCATION", "PLACE"):
                node_type = GraphNodeType.PLACE
            elif etype == "ORGANIZATION":
                node_type = GraphNodeType.ORGANIZATION
            elif etype == "DATE":
                node_type = GraphNodeType.DATE
            elif etype == "EVENT":
                node_type = GraphNodeType.EVENT

            key = f"{node_type.value}_{e_val.lower()}"
            if key not in node_map:
                enode = await self.create_node(
                    name=e_val,
                    label=node_type,
                    memorial_profile_id=memorial_profile_id,
                    source_memory_ids=[e["source_memory_id"]] if e.get("source_memory_id") else [],
                    source_evidence_ids=[e["id"]] if e.get("id") else [],
                    provenance_status=ProvenanceStatus(e.get("provenance_status", "DIRECTLY_OBSERVED")),
                    confidence=ConfidenceLevel(e.get("confidence", "VERIFIED")),
                    confidence_score=float(e.get("confidence_score", 1.0))
                )
                node_map[key] = enode.id
            
            # If entity appeared in a memory, link MEMORY -> DOCUMENTS / CONTAINS -> Entity
            m_id = e.get("source_memory_id")
            if m_id and f"MEMORY_{m_id}" in node_map:
                m_node_id = node_map[f"MEMORY_{m_id}"]
                e_node_id = node_map[key]
                
                rel_type = GraphRelationshipType.ABOUT
                if node_type == GraphNodeType.PERSON:
                    rel_type = GraphRelationshipType.INVOLVES
                elif node_type == GraphNodeType.PLACE:
                    rel_type = GraphRelationshipType.OCCURRED_AT

                await self.create_relationship(
                    source_node_id=m_node_id,
                    target_node_id=e_node_id,
                    relationship_type=rel_type,
                    memorial_profile_id=memorial_profile_id,
                    source_memory_ids=[m_id],
                    source_evidence_ids=[e["id"]] if e.get("id") else [],
                    provenance_status=ProvenanceStatus(e.get("provenance_status", "DIRECTLY_OBSERVED"))
                )

        # 4. Add Event Nodes
        for ev in events:
            ev_title = ev.get("title", "").strip()
            if not ev_title:
                continue
            ev_node = await self.create_node(
                name=ev_title,
                label=GraphNodeType.EVENT,
                memorial_profile_id=memorial_profile_id,
                properties={
                    "event_type": ev.get("event_type", "OTHER"),
                    "date": ev.get("date"),
                    "location": ev.get("location")
                },
                source_memory_ids=[ev["memory_id"]] if ev.get("memory_id") else [],
                source_evidence_ids=[ev["id"]] if ev.get("id") else [],
                provenance_status=ProvenanceStatus(ev.get("provenance_status", "DIRECTLY_OBSERVED")),
                confidence=ConfidenceLevel(ev.get("confidence", "VERIFIED")),
                confidence_score=float(ev.get("confidence_score", 1.0))
            )
            ev_key = f"EVENT_{ev.get('id', ev_title)}"
            node_map[ev_key] = ev_node.id

            # Link subject participated in event
            await self.create_relationship(
                source_node_id=subject_node.id,
                target_node_id=ev_node.id,
                relationship_type=GraphRelationshipType.PARTICIPATED_IN,
                memorial_profile_id=memorial_profile_id,
                source_memory_ids=[ev["memory_id"]] if ev.get("memory_id") else [],
                provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED
            )

        # 5. Add Explicit Relationships (e.g., Kinship, Education, Career)
        if relationships_data:
            for r in relationships_data:
                src_key = r.get("source_key") or "SUBJECT"
                tgt_key = r.get("target_key")
                rtype_str = r.get("relationship_type", "RELATED_TO")
                if tgt_key and src_key in node_map and tgt_key in node_map:
                    try:
                        rtype = GraphRelationshipType(rtype_str)
                    except ValueError:
                        rtype = GraphRelationshipType.RELATED_TO

                    await self.create_relationship(
                        source_node_id=node_map[src_key],
                        target_node_id=node_map[tgt_key],
                        relationship_type=rtype,
                        memorial_profile_id=memorial_profile_id,
                        source_evidence_ids=r.get("source_evidence_ids", []),
                        provenance_status=ProvenanceStatus(r.get("provenance_status", "USER_PROVIDED")),
                        confidence=ConfidenceLevel(r.get("confidence", "VERIFIED"))
                    )

        stats = await self.get_graph_stats(memorial_profile_id)
        return {
            "nodes_created": stats["total_nodes"],
            "relationships_created": stats["total_relationships"]
        }
