"""Relationship Service for Evidence-Grounded Social & Kinship Graph in ECHO.

Orchestrates Phase 8 Relationship Graph:
- Leverages Phase 4 KnowledgeGraphService and LocalGraphStore
- Evidence-backed edges retaining provenance, confidence, and verification lifecycle
- Verification, dispute, and rejection workflows
- Duplicate entity detection (fuzzy token similarity) and canonical merge workflow
- Neighborhood expansion and table fallback data export
"""

import time
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from uuid import uuid4
import difflib

from models.relationship import (
    RelationshipDetail,
    RelationshipEdgeCreate,
    RelationshipVerifyRequest,
    RelationshipDisputeRequest,
    DuplicateEntityCandidate,
    EntityMergeRequest,
    RelationshipGraphResponse,
)
from models.enums import (
    GraphRelationshipType,
    GraphNodeType,
    ConfidenceLevel,
    ProvenanceStatus,
    VerificationStatus,
    AuditAction,
)
from backend.app.services.knowledge_graph_service import KnowledgeGraphService, get_graph_store
from backend.app.services.audit_service import audit_service


class RelationshipService:
    """Manages social and kinship edges, evidence verification, and duplicate entity resolution."""

    def __init__(self):
        self.graph_svc = KnowledgeGraphService()
        self._edges: Dict[str, RelationshipDetail] = {}
        self._duplicate_candidates: Dict[str, DuplicateEntityCandidate] = {}
        self._init_foundation_relationships()

    def _init_foundation_relationships(self):
        """Seed verified and evidence-backed social and kinship relationships."""
        edges_data = [
            RelationshipDetail(
                id="rel-edge-001",
                memorial_profile_id="demo-profile-001",
                source_entity_id="demo-profile-001",
                source_entity_name="Memorial Subject",
                source_entity_type=GraphNodeType.PERSON,
                target_entity_id="demo-person-001",
                target_entity_name="Eleanor Vance",
                target_entity_type=GraphNodeType.PERSON,
                relationship_type=GraphRelationshipType.PARENT_OF,
                description="Parent-child kinship connection corroborated by Scottish General Register Office extract.",
                source_evidence_ids=["demo-doc-001"],
                source_memory_ids=["demo-mem-001"],
                provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=1.0,
                verification_status=VerificationStatus.VERIFIED,
                is_disputed=False,
                created_by="demo-user-001"
            ),
            RelationshipDetail(
                id="rel-edge-002",
                memorial_profile_id="demo-profile-001",
                source_entity_id="demo-profile-001",
                source_entity_name="Memorial Subject",
                source_entity_type=GraphNodeType.PERSON,
                target_entity_id="demo-person-002",
                target_entity_name="Arthur Vance",
                target_entity_type=GraphNodeType.PERSON,
                relationship_type=GraphRelationshipType.SPOUSE_OF,
                description="Spousal partnership solemnized in 1970; corroborated by marriage record and travel journals.",
                source_evidence_ids=["demo-doc-001"],
                source_memory_ids=["demo-mem-001", "demo-mem-002"],
                provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=1.0,
                verification_status=VerificationStatus.VERIFIED,
                is_disputed=False,
                created_by="demo-user-001"
            ),
            RelationshipDetail(
                id="rel-edge-003",
                memorial_profile_id="demo-profile-001",
                source_entity_id="demo-profile-001",
                source_entity_name="Memorial Subject",
                source_entity_type=GraphNodeType.PERSON,
                target_entity_id="entity-org-cambridge",
                target_entity_name="University of Cambridge",
                target_entity_type=GraphNodeType.ORGANIZATION,
                relationship_type=GraphRelationshipType.STUDIED_AT,
                description="Matriculated at Trinity College; earned Master of Arts in Modern Literature in 1968.",
                source_evidence_ids=["demo-doc-001", "demo-doc-002"],
                source_memory_ids=["demo-mem-001"],
                provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=0.99,
                verification_status=VerificationStatus.VERIFIED,
                is_disputed=False,
                created_by="demo-user-001"
            ),
            RelationshipDetail(
                id="rel-edge-004",
                memorial_profile_id="demo-profile-001",
                source_entity_id="demo-profile-001",
                source_entity_name="Memorial Subject",
                source_entity_type=GraphNodeType.PERSON,
                target_entity_id="demo-person-003",
                target_entity_name="Prof. Harold Davies",
                target_entity_type=GraphNodeType.PERSON,
                relationship_type=GraphRelationshipType.FRIEND_OF,
                description="Academic supervisor and lifelong literary confidant at Cambridge.",
                source_evidence_ids=["demo-doc-002"],
                source_memory_ids=[],
                provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=0.95,
                verification_status=VerificationStatus.VERIFIED,
                is_disputed=False,
                created_by="demo-user-001"
            ),
            RelationshipDetail(
                id="rel-edge-005",
                memorial_profile_id="demo-profile-001",
                source_entity_id="demo-profile-001",
                source_entity_name="Memorial Subject",
                source_entity_type=GraphNodeType.PERSON,
                target_entity_id="entity-place-windermere",
                target_entity_name="Lake Windermere",
                target_entity_type=GraphNodeType.PLACE,
                relationship_type=GraphRelationshipType.VISITED,
                description="Summer holiday excursion recorded in 1974 sailing log.",
                source_evidence_ids=["demo-doc-002"],
                source_memory_ids=["demo-mem-002"],
                provenance_status=ProvenanceStatus.USER_PROVIDED,
                confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
                confidence_score=0.82,
                verification_status=VerificationStatus.PENDING_REVIEW,
                is_disputed=False,
                created_by="demo-user-001"
            ),
            RelationshipDetail(
                id="rel-edge-006",
                memorial_profile_id="demo-profile-001",
                source_entity_id="demo-profile-001",
                source_entity_name="Memorial Subject",
                source_entity_type=GraphNodeType.PERSON,
                target_entity_id="demo-mem-001",
                target_entity_name="Graduation Day at Trinity College Library",
                target_entity_type=GraphNodeType.MEMORY,
                relationship_type=GraphRelationshipType.CONNECTED_TO_MEMORY,
                description="Focal milestone memory in Wren Library courtyard.",
                source_evidence_ids=["demo-doc-001"],
                source_memory_ids=["demo-mem-001"],
                provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=1.0,
                verification_status=VerificationStatus.VERIFIED,
                is_disputed=False,
                created_by="demo-user-001"
            ),
            RelationshipDetail(
                id="rel-edge-007",
                memorial_profile_id="demo-profile-001",
                source_entity_id="demo-profile-001",
                source_entity_name="Memorial Subject",
                source_entity_type=GraphNodeType.PERSON,
                target_entity_id="entity-org-edinburgh-review",
                target_entity_name="Edinburgh Literary Review",
                target_entity_type=GraphNodeType.ORGANIZATION,
                relationship_type=GraphRelationshipType.WORKED_AT,
                description="Editorial role disputed: letter correspondence claims contributor status; oral testimony claims editor.",
                source_evidence_ids=["demo-doc-001"],
                source_memory_ids=[],
                provenance_status=ProvenanceStatus.USER_PROVIDED,
                confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
                confidence_score=0.65,
                verification_status=VerificationStatus.PENDING_REVIEW,
                is_disputed=True,
                dispute_notes="Archive indicates occasional contributor; family recollections assert associate editor post in 1969.",
                competing_evidence_ids=["demo-doc-001", "demo-doc-002"],
                created_by="demo-user-001"
            ),
        ]

        for e in edges_data:
            self._edges[e.id] = e

    async def get_graph(
        self,
        memorial_profile_id: str = "demo-profile-001",
        relationship_type: Optional[GraphRelationshipType] = None,
        verification_status: Optional[VerificationStatus] = None,
        entity_label: Optional[GraphNodeType] = None,
        search_query: Optional[str] = None
    ) -> RelationshipGraphResponse:
        """Retrieve relationship graph nodes and edges with filtering."""
        # 1. Fetch all raw nodes from knowledge graph
        nodes_raw = await self.graph_svc.get_all_nodes(memorial_profile_id=memorial_profile_id)
        
        # Build node dictionary representation
        nodes_dict: Dict[str, Dict[str, Any]] = {}
        for n in nodes_raw:
            nodes_dict[n.id] = {
                "id": n.id,
                "name": n.name,
                "label": n.label.value if hasattr(n.label, "value") else str(n.label),
                "confidence": n.confidence.value if hasattr(n.confidence, "value") else str(n.confidence),
                "properties": n.properties,
            }

        # Ensure seed entities exist in node list if not already present in graph
        for e in self._edges.values():
            if e.source_entity_id not in nodes_dict:
                nodes_dict[e.source_entity_id] = {
                    "id": e.source_entity_id,
                    "name": e.source_entity_name,
                    "label": e.source_entity_type.value,
                    "confidence": "VERIFIED",
                    "properties": {}
                }
            if e.target_entity_id not in nodes_dict:
                nodes_dict[e.target_entity_id] = {
                    "id": e.target_entity_id,
                    "name": e.target_entity_name,
                    "label": e.target_entity_type.value,
                    "confidence": "VERIFIED",
                    "properties": {}
                }

        # 2. Filter edges
        edges = list(self._edges.values())
        edges = [e for e in edges if e.memorial_profile_id == memorial_profile_id]

        if relationship_type:
            edges = [e for e in edges if e.relationship_type == relationship_type]

        if verification_status:
            edges = [e for e in edges if e.verification_status == verification_status]

        if search_query:
            sq = search_query.lower()
            edges = [
                e for e in edges
                if sq in e.source_entity_name.lower() or
                   sq in e.target_entity_name.lower() or
                   sq in (e.description or "").lower() or
                   sq in e.relationship_type.value.lower()
            ]

        # 3. Filter nodes based on active edges or entity_label
        active_node_ids = set()
        for e in edges:
            active_node_ids.add(e.source_entity_id)
            active_node_ids.add(e.target_entity_id)

        filtered_nodes = [
            n for n in nodes_dict.values()
            if n["id"] in active_node_ids or (entity_label and n["label"] == entity_label.value)
        ]

        verified_count = sum(1 for e in edges if e.verification_status == VerificationStatus.VERIFIED)
        disputed_count = sum(1 for e in edges if e.is_disputed)
        pending_count = sum(1 for e in edges if e.verification_status == VerificationStatus.PENDING_REVIEW)

        # Detect any duplicate candidate entities
        duplicate_candidates = await self.detect_duplicate_entities(memorial_profile_id=memorial_profile_id)

        return RelationshipGraphResponse(
            nodes=filtered_nodes,
            edges=edges,
            total_nodes=len(filtered_nodes),
            total_edges=len(edges),
            verified_edges_count=verified_count,
            disputed_edges_count=disputed_count,
            pending_review_edges_count=pending_count,
            duplicate_candidates_count=len(duplicate_candidates)
        )

    async def get_relationship(self, edge_id: str) -> Optional[RelationshipDetail]:
        """Retrieve single relationship edge details."""
        return self._edges.get(edge_id)

    async def create_relationship(
        self,
        edge_in: RelationshipEdgeCreate,
        actor_id: str = "demo-user-001",
        actor_role: str = "CONTRIBUTOR"
    ) -> RelationshipDetail:
        """Create a new evidence-grounded edge."""
        # Find names if known
        nodes = await self.graph_svc.get_all_nodes()
        node_map = {n.id: n for n in nodes}
        
        src_name = node_map[edge_in.source_entity_id].name if edge_in.source_entity_id in node_map else edge_in.source_entity_id
        src_type = node_map[edge_in.source_entity_id].label if edge_in.source_entity_id in node_map else GraphNodeType.PERSON
        tgt_name = node_map[edge_in.target_entity_id].name if edge_in.target_entity_id in node_map else edge_in.target_entity_id
        tgt_type = node_map[edge_in.target_entity_id].label if edge_in.target_entity_id in node_map else GraphNodeType.PERSON

        # Require review for contributions
        init_status = edge_in.verification_status
        if actor_role == "CONTRIBUTOR":
            init_status = VerificationStatus.PENDING_REVIEW

        edge = RelationshipDetail(
            id=str(uuid4()),
            memorial_profile_id="demo-profile-001",
            source_entity_id=edge_in.source_entity_id,
            source_entity_name=src_name,
            source_entity_type=src_type,
            target_entity_id=edge_in.target_entity_id,
            target_entity_name=tgt_name,
            target_entity_type=tgt_type,
            relationship_type=edge_in.relationship_type,
            description=edge_in.description,
            source_evidence_ids=edge_in.source_evidence_ids,
            source_memory_ids=edge_in.source_memory_ids,
            confidence=edge_in.confidence,
            verification_status=init_status,
            created_by=actor_id,
            is_ai_suggested=False
        )

        self._edges[edge.id] = edge

        await audit_service.record_event(
            action=AuditAction.RELATIONSHIP_CREATED,
            actor=actor_id,
            resource=f"RelationshipEdge:{edge.id}",
            result="SUCCESS",
            metadata={"type": edge.relationship_type.value, "source": src_name, "target": tgt_name}
        )
        return edge

    async def verify_relationship(
        self,
        edge_id: str,
        verify_req: RelationshipVerifyRequest,
        actor_id: str = "demo-user-001",
        actor_role: str = "FAMILY_ADMIN"
    ) -> Optional[RelationshipDetail]:
        """Verify or reject relationship edge."""
        edge = self._edges.get(edge_id)
        if not edge:
            return None

        edge.verification_status = verify_req.verification_status
        if verify_req.verification_status == VerificationStatus.VERIFIED:
            edge.confidence = ConfidenceLevel.VERIFIED
            edge.confidence_score = 1.0
            edge.is_ai_suggested = False
        elif verify_req.verification_status == VerificationStatus.REJECTED:
            edge.confidence = ConfidenceLevel.UNKNOWN_UNSUPPORTED
            edge.confidence_score = 0.0

        edge.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.RELATIONSHIP_VERIFIED,
            actor=actor_id,
            resource=f"RelationshipEdge:{edge_id}",
            result="SUCCESS",
            metadata={"status": verify_req.verification_status.value, "notes": verify_req.notes}
        )
        return edge

    async def dispute_relationship(
        self,
        edge_id: str,
        dispute_req: RelationshipDisputeRequest,
        actor_id: str = "demo-user-001"
    ) -> Optional[RelationshipDetail]:
        """Dispute relationship while preserving both competing perspectives."""
        edge = self._edges.get(edge_id)
        if not edge:
            return None

        edge.is_disputed = True
        notes = f"Dispute: {dispute_req.dispute_reason}"
        if dispute_req.notes:
            notes += f" | Details: {dispute_req.notes}"
        edge.dispute_notes = notes

        if dispute_req.competing_evidence_id and dispute_req.competing_evidence_id not in edge.competing_evidence_ids:
            edge.competing_evidence_ids.append(dispute_req.competing_evidence_id)

        edge.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.RELATIONSHIP_DISPUTED,
            actor=actor_id,
            resource=f"RelationshipEdge:{edge_id}",
            result="SUCCESS",
            metadata={"dispute_reason": dispute_req.dispute_reason}
        )
        return edge

    async def detect_duplicate_entities(
        self,
        memorial_profile_id: str = "demo-profile-001"
    ) -> List[DuplicateEntityCandidate]:
        """Detect possible duplicate entity nodes using fuzzy token similarity."""
        nodes = list(self.graph_svc.store._nodes.values())
        
        # Also include entities from edges
        entity_records: Dict[str, Tuple[str, GraphNodeType]] = {}
        for n in nodes:
            entity_records[n.id] = (n.name, n.label)
        for e in self._edges.values():
            entity_records[e.source_entity_id] = (e.source_entity_name, e.source_entity_type)
            entity_records[e.target_entity_id] = (e.target_entity_name, e.target_entity_type)

        candidates: List[DuplicateEntityCandidate] = []
        entity_list = list(entity_records.items())

        for i in range(len(entity_list)):
            for j in range(i + 1, len(entity_list)):
                id_a, (name_a, label_a) = entity_list[i]
                id_b, (name_b, label_b) = entity_list[j]

                # Only compare entities of the same type
                if label_a != label_b:
                    continue

                clean_a = name_a.strip().lower()
                clean_b = name_b.strip().lower()

                # Exact match with different ID or high Levenshtein ratio
                ratio = difflib.SequenceMatcher(None, clean_a, clean_b).ratio()
                
                # Check for prefix or initial match (e.g. "Eleanor Vance" vs "Eleanor V.")
                prefix_match = False
                tokens_a = clean_a.split()
                tokens_b = clean_b.split()
                if len(tokens_a) > 1 and len(tokens_b) > 1:
                    if tokens_a[0] == tokens_b[0] and (tokens_a[1].startswith(tokens_b[1][0]) or tokens_b[1].startswith(tokens_a[1][0])):
                        prefix_match = True

                if (ratio >= 0.75 or prefix_match) and clean_a != clean_b:
                    cand_id = f"dup_{min(id_a, id_b)}_{max(id_a, id_b)}"
                    canonical_id = id_a if len(name_a) >= len(name_b) else id_b

                    candidate = DuplicateEntityCandidate(
                        id=cand_id,
                        entity_a_id=id_a,
                        entity_a_name=name_a,
                        entity_a_label=label_a,
                        entity_b_id=id_b,
                        entity_b_name=name_b,
                        entity_b_label=label_b,
                        similarity_score=round(ratio if ratio > 0.75 else 0.85, 2),
                        detection_reason=f"High token similarity between '{name_a}' and '{name_b}'",
                        suggested_canonical_id=canonical_id,
                        status="PENDING_REVIEW"
                    )
                    candidates.append(candidate)
                    self._duplicate_candidates[cand_id] = candidate

        return candidates

    async def merge_duplicate_entities(
        self,
        merge_req: EntityMergeRequest,
        actor_id: str = "demo-user-001",
        actor_role: str = "FAMILY_ADMIN"
    ) -> Dict[str, Any]:
        """Merge duplicate entity into canonical entity and re-route edges."""
        canon_id = merge_req.canonical_entity_id
        dup_id = merge_req.duplicate_entity_id

        # Re-point all edges that touch duplicate entity
        repointed_edges = 0
        for edge in self._edges.values():
            if edge.source_entity_id == dup_id:
                edge.source_entity_id = canon_id
                repointed_edges += 1
            if edge.target_entity_id == dup_id:
                edge.target_entity_id = canon_id
                repointed_edges += 1

        # Mark any candidate as merged
        for c in self._duplicate_candidates.values():
            if (c.entity_a_id == dup_id and c.entity_b_id == canon_id) or \
               (c.entity_b_id == dup_id and c.entity_a_id == canon_id):
                c.status = "MERGED"

        await audit_service.record_event(
            action=AuditAction.RELATIONSHIP_MERGED,
            actor=actor_id,
            resource=f"EntityMerge:{dup_id}->{canon_id}",
            result="SUCCESS",
            metadata={
                "canonical_id": canon_id,
                "duplicate_id": dup_id,
                "repointed_edges": repointed_edges,
                "notes": merge_req.merge_notes
            }
        )

        return {
            "status": "success",
            "canonical_id": canon_id,
            "duplicate_id": dup_id,
            "repointed_edges": repointed_edges
        }


# Singleton instance
relationship_service = RelationshipService()
