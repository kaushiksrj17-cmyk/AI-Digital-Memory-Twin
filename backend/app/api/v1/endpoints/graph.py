"""Knowledge Graph API Endpoints.

Provides entity and relation graph inspection, neighborhood traversal,
safe evidence-grounded rebuilding, and semantic search over the graph.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional

from models.enums import GraphNodeType, GraphRelationshipType, AuditAction
from models.graph import (
    GraphNodeModel,
    GraphRelationshipModel,
    GraphNeighborhood,
    GraphSearchResult,
)
from backend.app.services.knowledge_graph_service import KnowledgeGraphService, get_graph_store
from backend.app.services.memory_service import memory_service
from backend.app.services.processing_orchestrator import processing_orchestrator
from backend.app.services.audit_service import audit_service

router = APIRouter()


@router.get("/nodes", response_model=List[GraphNodeModel])
async def get_graph_nodes(
    memorial_profile_id: str = "default-profile-001",
    label: Optional[GraphNodeType] = None,
    query: Optional[str] = None,
    limit: int = 100
):
    """Retrieve nodes in the knowledge graph with optional label or query filtering."""
    graph_svc = KnowledgeGraphService()
    if query:
        return await graph_svc.store.search_nodes(query, memorial_profile_id=memorial_profile_id, label=label, limit=limit)
    nodes = await graph_svc.get_all_nodes(memorial_profile_id=memorial_profile_id)
    if label:
        nodes = [n for n in nodes if n.label == label]
    return nodes[:limit]


@router.get("/nodes/{node_id}", response_model=GraphNodeModel)
async def get_graph_node(node_id: str):
    """Retrieve a single graph node by ID."""
    graph_svc = KnowledgeGraphService()
    node = await graph_svc.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Graph node not found")
    return node


@router.get("/nodes/{node_id}/neighbors", response_model=GraphNeighborhood)
async def get_node_neighbors(node_id: str, max_depth: int = Query(default=1, ge=1, le=3)):
    """Retrieve connected neighbors and edges up to max_depth."""
    graph_svc = KnowledgeGraphService()
    neighborhood = await graph_svc.get_neighborhood(node_id, max_depth=max_depth)
    if not neighborhood:
        raise HTTPException(status_code=404, detail="Graph node not found")
    return neighborhood


@router.get("/relationships", response_model=List[GraphRelationshipModel])
async def get_graph_relationships(memorial_profile_id: str = "default-profile-001", limit: int = 200):
    """List all evidence-backed relationship edges in the archive."""
    graph_svc = KnowledgeGraphService()
    rels = await graph_svc.get_all_relationships(memorial_profile_id=memorial_profile_id)
    return rels[:limit]


@router.get("/search", response_model=GraphSearchResult)
async def search_graph(
    query: str,
    memorial_profile_id: str = "default-profile-001",
    label: Optional[GraphNodeType] = None,
    limit: int = 50
):
    """Search graph entities and their connected relationships."""
    graph_svc = KnowledgeGraphService()
    return await graph_svc.search(query=query, memorial_profile_id=memorial_profile_id, label=label, limit=limit)


@router.get("/stats", response_model=Dict[str, Any])
async def get_graph_stats(memorial_profile_id: str = "default-profile-001"):
    """Return total nodes, relationships, and breakdowns by type."""
    graph_svc = KnowledgeGraphService()
    return await graph_svc.get_graph_stats(memorial_profile_id=memorial_profile_id)


@router.post("/rebuild/{memorial_profile_id}", response_model=Dict[str, int])
async def rebuild_graph(memorial_profile_id: str, actor: str = "demo-guardian-001"):
    """Safely rebuild the knowledge graph from primary memories, entities, and events."""
    graph_svc = KnowledgeGraphService()
    
    memories = await memory_service.get_memories(memorial_profile_id=memorial_profile_id, limit=200)
    memories_dicts = [m.model_dump() for m in memories]

    entities = processing_orchestrator.get_all_entities(memorial_profile_id)
    events = processing_orchestrator.get_all_events(memorial_profile_id)
    evidence = processing_orchestrator.get_all_evidence(memorial_profile_id)

    result = await graph_svc.build_from_memories_and_evidence(
        memorial_profile_id=memorial_profile_id,
        memories=memories_dicts,
        evidence_list=evidence,
        entities=entities,
        events=events
    )

    await audit_service.record_event(
        action=AuditAction.GRAPH_REBUILT,
        actor=actor,
        resource=f"KnowledgeGraph/{memorial_profile_id}",
        metadata=result
    )

    return result
