"""Knowledge Graph Pydantic Models for ECHO.

Defines schemas for nodes, edges, neighborhoods, and traversal results.
All nodes and edges carry provenance status, confidence, and source evidence IDs.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from models.enums import (
    GraphNodeType,
    GraphRelationshipType,
    ConfidenceLevel,
    ProvenanceStatus,
)


class GraphNodeModel(BaseModel):
    """A node in the ECHO Knowledge Graph."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "default-profile-001"
    label: GraphNodeType
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    source_memory_ids: List[str] = Field(default_factory=list)
    source_evidence_ids: List[str] = Field(default_factory=list)
    provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    confidence_score: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphRelationshipModel(BaseModel):
    """A directed, evidence-backed edge between two nodes in the ECHO Knowledge Graph."""
    relationship_id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "default-profile-001"
    source_node: str
    target_node: str
    relationship_type: GraphRelationshipType
    properties: Dict[str, Any] = Field(default_factory=dict)
    source_evidence_ids: List[str] = Field(default_factory=list)
    source_memory_ids: List[str] = Field(default_factory=list)
    provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    confidence_score: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphNeighborhood(BaseModel):
    """Local graph neighborhood of a focal node."""
    node: GraphNodeModel
    neighbors: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[GraphRelationshipModel] = Field(default_factory=list)


class GraphSearchResult(BaseModel):
    """Result of graph entity search or traversal."""
    nodes: List[GraphNodeModel] = Field(default_factory=list)
    relationships: List[GraphRelationshipModel] = Field(default_factory=list)
    total_nodes: int = 0
    total_relationships: int = 0
