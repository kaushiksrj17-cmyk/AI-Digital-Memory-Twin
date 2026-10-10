"""Embeddings and Vector Indexing API Endpoints.

Provides vector generation, batch evidence indexing, index statistics,
and individual vector deletion with complete provenance preservation.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone

from ai.providers.factory import provider_registry
from models.enums import AuditAction, ProvenanceStatus, ConfidenceLevel
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import get_vector_store
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.memory_service import memory_service
from backend.app.services.processing_orchestrator import processing_orchestrator
from backend.app.services.audit_service import audit_service

router = APIRouter()


class EmbeddingRequest(BaseModel):
    text: str


class EmbeddingResponse(BaseModel):
    dimension: int
    vector_preview: List[float]
    provider: str
    model: str


@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(req: EmbeddingRequest):
    """Generate dense semantic embedding vector for memory indexing."""
    provider = provider_registry.embedding_provider
    vector = await provider.get_embedding(req.text)
    return EmbeddingResponse(
        dimension=len(vector),
        vector_preview=vector[:5],
        provider=provider.name,
        model=provider.model or "unknown"
    )


@router.post("/index/{memorial_profile_id}", response_model=Dict[str, Any])
async def index_archive(
    memorial_profile_id: str,
    actor: str = "demo-guardian-001"
):
    """Chunk and embed memories and multimodal evidence into the vector store."""
    embedding_svc = EmbeddingService()
    vector_store = get_vector_store()
    chunker = ChunkingService()

    indexed_count = 0

    # 1. Index memories
    memories = await memory_service.get_memories(memorial_profile_id=memorial_profile_id, limit=200)
    for m in memories:
        chunks = chunker.chunk_memory_narrative(
            memory_id=m.id,
            memorial_profile_id=memorial_profile_id,
            title=m.title,
            description=m.description,
            narrative=m.narrative,
            provenance=ProvenanceStatus.USER_PROVIDED if m.source_type == "USER_ENTRY" else ProvenanceStatus.DIRECTLY_OBSERVED,
            confidence=m.confidence,
            confidence_score=m.confidence_score
        )
        for c in chunks:
            vec = await embedding_svc.get_embedding(c.text)
            await vector_store.upsert(
                id=c.chunk_id,
                vector=vec,
                payload={
                    "vector_id": c.chunk_id,
                    "chunk_id": c.chunk_id,
                    "memory_id": m.id,
                    "evidence_id": None,
                    "media_id": None,
                    "memorial_profile_id": memorial_profile_id,
                    "content_type": "MEMORY_CHUNK",
                    "text": c.text,
                    "source_reference": c.source_reference,
                    "provenance_status": c.provenance.value if hasattr(c.provenance, "value") else str(c.provenance),
                    "confidence": c.confidence.value if hasattr(c.confidence, "value") else str(c.confidence),
                    "confidence_score": c.confidence_score,
                    "privacy_level": m.privacy_level.value if hasattr(m.privacy_level, "value") else str(m.privacy_level)
                }
            )
            indexed_count += 1

    # 2. Index extracted evidence
    evidence_list = processing_orchestrator.get_all_evidence(memorial_profile_id)
    for ev in evidence_list:
        ev_id = ev.get("id")
        content = ev.get("content", "")
        if not content:
            continue
        ev_chunks = chunker.chunk_text(
            text=content,
            memorial_profile_id=memorial_profile_id,
            memory_id=ev.get("memory_id"),
            media_id=ev.get("media_id"),
            evidence_id=ev_id,
            source_reference=ev.get("source_reference", "Multimodal Evidence"),
            provenance=ProvenanceStatus(ev.get("provenance_status", "DIRECTLY_OBSERVED")),
            confidence=ConfidenceLevel(ev.get("confidence", "VERIFIED")),
            confidence_score=float(ev.get("confidence_score", 1.0))
        )
        for c in ev_chunks:
            vec = await embedding_svc.get_embedding(c.text)
            await vector_store.upsert(
                id=c.chunk_id,
                vector=vec,
                payload={
                    "vector_id": c.chunk_id,
                    "chunk_id": c.chunk_id,
                    "memory_id": ev.get("memory_id"),
                    "evidence_id": ev_id,
                    "media_id": ev.get("media_id"),
                    "memorial_profile_id": memorial_profile_id,
                    "content_type": ev.get("evidence_type", "EVIDENCE"),
                    "text": c.text,
                    "source_reference": c.source_reference,
                    "provenance_status": c.provenance.value if hasattr(c.provenance, "value") else str(c.provenance),
                    "confidence": c.confidence.value if hasattr(c.confidence, "value") else str(c.confidence),
                    "confidence_score": c.confidence_score,
                    "privacy_level": "PRIVATE"
                }
            )
            indexed_count += 1

    await audit_service.record_event(
        action=AuditAction.EMBEDDING_CREATED,
        actor=actor,
        resource=f"VectorIndex/{memorial_profile_id}",
        metadata={"indexed_records": indexed_count}
    )

    return {
        "status": "COMPLETED",
        "memorial_profile_id": memorial_profile_id,
        "indexed_chunks": indexed_count,
        "store_status": vector_store.get_status()
    }


@router.get("/stats", response_model=Dict[str, Any])
async def get_embedding_stats(memorial_profile_id: Optional[str] = None):
    """Retrieve indexing statistics, vector counts, and provider status."""
    vector_store = get_vector_store()
    embedding_svc = EmbeddingService()
    count = await vector_store.count(memorial_profile_id)
    return {
        "indexed_vectors_count": count,
        "store": vector_store.get_status(),
        "provider": embedding_svc.get_status()
    }


@router.delete("/{vector_id}", response_model=Dict[str, Any])
async def delete_vector(vector_id: str, actor: str = "demo-guardian-001"):
    """Delete a specific vector record from the vector index."""
    vector_store = get_vector_store()
    deleted = await vector_store.delete(vector_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vector ID not found in vector index")

    await audit_service.record_event(
        action=AuditAction.EMBEDDING_DELETED,
        actor=actor,
        resource=f"Vector/{vector_id}",
        metadata={"vector_id": vector_id}
    )

    return {"status": "DELETED", "vector_id": vector_id}
