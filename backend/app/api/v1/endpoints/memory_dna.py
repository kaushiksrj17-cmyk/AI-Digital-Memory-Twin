"""Memory DNA API Endpoints.

Provides structured evidence-grounded life facts and narrative elements:
- Build Memory DNA from multimodal archive evidence
- Retrieve structured Memory DNA document
- Inspect historical versions for research audit
- Query, verify, and reject individual Memory DNA items
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional

from models.enums import (
    MemoryDNACategory,
    ConfidenceLevel,
    AuditAction,
)
from models.memory_dna import (
    MemoryDNA,
    MemoryDNAItem,
    MemoryDNAVersion,
)
from backend.app.services.memory_dna_service import get_memory_dna_service
from backend.app.services.memory_service import memory_service
from backend.app.services.processing_orchestrator import processing_orchestrator
from backend.app.services.audit_service import audit_service

router = APIRouter()


@router.post("/build/{memorial_profile_id}", response_model=MemoryDNA)
async def build_memory_dna(
    memorial_profile_id: str,
    changed_by: str = "demo-guardian-001",
    change_reason: str = "Multimodal archive compilation"
):
    """Compile structured Memory DNA from stored memories, extracted entities, and events.
    
    Deterministic synthesis without AI fabrication. Missing fields remain UNKNOWN.
    """
    dna_svc = get_memory_dna_service()
    
    # Retrieve current active memories
    memories_list = await memory_service.get_memories(memorial_profile_id=memorial_profile_id, limit=200)
    memories_dicts = [m.model_dump() for m in memories_list]

    # Retrieve extracted entities and events from processing orchestrator
    entities_list = processing_orchestrator.get_all_entities(memorial_profile_id)
    events_list = processing_orchestrator.get_all_events(memorial_profile_id)
    evidence_list = processing_orchestrator.get_all_evidence(memorial_profile_id)

    # Build DNA
    dna = await dna_svc.build_from_evidence(
        memorial_profile_id=memorial_profile_id,
        memories=memories_dicts,
        evidence_list=evidence_list,
        entities=entities_list,
        events=events_list,
        changed_by=changed_by,
        change_reason=change_reason
    )

    await audit_service.record_event(
        action=AuditAction.MEMORY_DNA_BUILT,
        actor=changed_by,
        resource=f"MemoryDNA/{memorial_profile_id}",
        metadata={"version": dna.version, "categories_updated": 22}
    )

    return dna


@router.get("/{memorial_profile_id}", response_model=MemoryDNA)
async def get_memory_dna(memorial_profile_id: str):
    """Fetch active Memory DNA document for a memorial profile."""
    dna_svc = get_memory_dna_service()
    return await dna_svc.get_or_create_dna(memorial_profile_id)


@router.get("/{memorial_profile_id}/history", response_model=List[MemoryDNAVersion])
async def get_memory_dna_history(memorial_profile_id: str):
    """Retrieve historical snapshots of Memory DNA for research audit and reproducibility."""
    dna_svc = get_memory_dna_service()
    return await dna_svc.get_history(memorial_profile_id)


@router.get("/{memorial_profile_id}/items", response_model=List[MemoryDNAItem])
async def get_memory_dna_items(
    memorial_profile_id: str,
    category: Optional[MemoryDNACategory] = None,
    confidence: Optional[ConfidenceLevel] = None
):
    """Query granular Memory DNA items with optional category or confidence filtering."""
    dna_svc = get_memory_dna_service()
    return await dna_svc.get_items(memorial_profile_id, category=category, confidence=confidence)


@router.get("/{memorial_profile_id}/stats", response_model=Dict[str, Any])
async def get_memory_dna_stats(memorial_profile_id: str):
    """Return counts of items by category, confidence level, and verification status."""
    dna_svc = get_memory_dna_service()
    return await dna_svc.get_stats(memorial_profile_id)


@router.get("/items/{item_id}", response_model=MemoryDNAItem)
async def get_memory_dna_item(item_id: str):
    """Inspect a single Memory DNA item by ID."""
    dna_svc = get_memory_dna_service()
    item = await dna_svc.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Memory DNA item not found")
    return item


@router.post("/items/{item_id}/verify", response_model=MemoryDNAItem)
async def verify_memory_dna_item(item_id: str, verified_by: str = "demo-guardian-001"):
    """Manually verify a Memory DNA item with human guardian approval."""
    dna_svc = get_memory_dna_service()
    item = await dna_svc.verify_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Memory DNA item not found")

    await audit_service.record_event(
        action=AuditAction.MEMORY_DNA_VERIFIED,
        actor=verified_by,
        resource=f"MemoryDNAItem/{item_id}",
        metadata={"category": item.category.value if hasattr(item.category, "value") else str(item.category)}
    )
    return item


@router.post("/items/{item_id}/reject", response_model=MemoryDNAItem)
async def reject_memory_dna_item(item_id: str, rejected_by: str = "demo-guardian-001"):
    """Reject an ungrounded or disputed Memory DNA item."""
    dna_svc = get_memory_dna_service()
    item = await dna_svc.reject_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Memory DNA item not found")

    await audit_service.record_event(
        action=AuditAction.MEMORY_DNA_REJECTED,
        actor=rejected_by,
        resource=f"MemoryDNAItem/{item_id}",
        metadata={"category": item.category.value if hasattr(item.category, "value") else str(item.category)}
    )
    return item
