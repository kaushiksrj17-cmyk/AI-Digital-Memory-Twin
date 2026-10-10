"""Analytics and Executive Dashboard API Endpoint."""

from fastapi import APIRouter
from typing import Dict, Any
from backend.app.services.memory_service import memory_service

router = APIRouter()


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Retrieve raw memory vault statistics."""
    return await memory_service.get_vault_statistics()


@router.get("/processing")
async def get_processing_analytics():
    """Retrieve real-time multimodal processing metrics and job statistics."""
    from backend.app.services.processing_orchestrator import processing_orchestrator
    return processing_orchestrator.get_analytics()



@router.get("/dashboard")
@router.get("/metrics")
async def get_dashboard_metrics(memorial_profile_id: str = "default-profile-001") -> Dict[str, Any]:
    """Retrieve full memorial analytics, confidence breakdown, Phase 4 foundation metrics, and activity."""
    stats = await memory_service.get_vault_statistics()
    
    # Real Phase 4 foundation metrics
    from backend.app.services.memory_dna_service import get_memory_dna_service
    from backend.app.services.knowledge_graph_service import KnowledgeGraphService
    from backend.app.services.vector_store import get_vector_store
    from backend.app.services.retrieval_service import get_retrieval_service
    from backend.app.services.processing_orchestrator import processing_orchestrator

    dna_svc = get_memory_dna_service()
    dna_stats = await dna_svc.get_stats(memorial_profile_id)

    graph_svc = KnowledgeGraphService()
    graph_stats = await graph_svc.get_graph_stats(memorial_profile_id)

    vector_store = get_vector_store()
    vec_count = await vector_store.count(memorial_profile_id)

    retrieval_svc = get_retrieval_service()
    query_logs = retrieval_svc.get_logs()

    evidence_list = processing_orchestrator.get_all_evidence(memorial_profile_id)
    verified_ev = sum(1 for e in evidence_list if e.get("confidence") == "VERIFIED")
    supported_ev = sum(1 for e in evidence_list if e.get("confidence") == "SUPPORTED_INFERENCE")
    unknown_ev = sum(1 for e in evidence_list if e.get("confidence") == "UNKNOWN_UNSUPPORTED")

    phase4_metrics = {
        "memory_dna_items": dna_stats["total_items"],
        "graph_nodes": graph_stats["total_nodes"],
        "graph_relationships": graph_stats["total_relationships"],
        "indexed_evidence": len(evidence_list),
        "vector_records": vec_count,
        "retrieval_queries": len(query_logs),
        "verified_evidence": verified_ev + dna_stats.get("verified_count", 0),
        "supported_inferences": supported_ev + dna_stats.get("supported_inferences", 0),
        "unknown_items": unknown_ev + dna_stats.get("unknown_items", 0)
    }

    # Real Phase 5 Conversational RAG & Guardian metrics
    from backend.app.services.conversation_service import conversation_service
    from backend.app.services.rag_service import get_rag_service
    from backend.app.services.contradiction_service import get_contradiction_service

    all_sessions = await conversation_service.list_sessions(memorial_profile_id)
    total_messages = sum(len(s.messages) for s in all_sessions)
    assistant_msgs = [m for s in all_sessions for m in s.messages if m.role == "assistant"]
    verified_answers = sum(1 for m in assistant_msgs if m.confidence == "VERIFIED" or getattr(m.confidence, "value", "") == "VERIFIED")
    supported_answers = sum(1 for m in assistant_msgs if m.confidence == "SUPPORTED_INFERENCE" or getattr(m.confidence, "value", "") == "SUPPORTED_INFERENCE")
    unknown_answers = sum(1 for m in assistant_msgs if m.confidence == "UNKNOWN_UNSUPPORTED" or getattr(m.confidence, "value", "") == "UNKNOWN_UNSUPPORTED")
    
    rag_metrics = get_rag_service().get_metrics()
    guardian_revisions = sum(1 for m in rag_metrics if m.get("guardian_status") == "REVISE" or "revision" in str(m))
    guardian_blocks = sum(1 for m in assistant_msgs if getattr(m.guardian_status, "value", "") == "BLOCK" or str(m.guardian_status) == "BLOCK")

    contradiction_svc = get_contradiction_service()
    contradictions_list = contradiction_svc.get_contradictions(memorial_profile_id)

    phase5_metrics = {
        "conversations": len(all_sessions),
        "messages": total_messages,
        "rag_queries": len(rag_metrics),
        "verified_responses": verified_answers,
        "supported_inferences": supported_answers,
        "unknown_responses": unknown_answers,
        "guardian_revisions": guardian_revisions,
        "guardian_blocks": guardian_blocks,
        "contradictions_detected": len(contradictions_list),
    }

    return {
        "cards": stats,
        "phase4_metrics": phase4_metrics,
        "phase5_metrics": phase5_metrics,
        "recent_memories": [
            {
                "id": "demo-mem-001",
                "title": "Graduation Day at Trinity College Library",
                "date": "June 1968",
                "confidence": "VERIFIED",
                "source": "Photograph & Degree Certificate"
            },
            {
                "id": "demo-mem-002",
                "title": "Summer Sailing on Lake Windermere",
                "date": "August 1974",
                "confidence": "SUPPORTED_INFERENCE",
                "source": "Handwritten Travel Journal"
            }
        ],
        "recent_evidence": [
            {
                "id": "demo-doc-001",
                "title": "University Degree Registry 1968",
                "type": "DOCUMENT",
                "provenance": "Folio 82, Cambridge Archives"
            },
            {
                "id": "demo-media-002",
                "title": "Oral History Tape - Highland Journey",
                "type": "AUDIO_RECORDING",
                "provenance": "Side A (14m:22s)"
            }
        ],
        "recent_activity": [
            {
                "action": "Evidence Verified",
                "description": "Family trustee corroborated 1968 graduation photograph.",
                "timestamp": "2026-10-08T10:15:00Z"
            },
            {
                "action": "Dialogue Grounding Audited",
                "description": "Conversation citation verified against Primary Box 1.",
                "timestamp": "2026-10-08T09:40:00Z"
            }
        ],
        "privacy_status": {
            "level": "Private Vault (Kinship Circle)",
            "location": "D:\\ECHO\\storage\\local",
            "consent_verified": True
        }
    }
