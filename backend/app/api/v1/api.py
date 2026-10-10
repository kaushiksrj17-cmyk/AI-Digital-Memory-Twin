"""API v1 Router Aggregator.

Exposes all modular endpoints under /api/v1.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    health,
    auth,
    users,
    memories,
    media,
    timeline,
    people,
    relationships,
    conversation,
    rag,
    embeddings,
    voice,
    avatar,
    provenance,
    confidence,
    guardian,
    security,
    analytics,
    consent,
    audit,
    processing,
    evidence,
    memory_dna,
    graph,
    retrieval,
    memory_room,
    family,
    research
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(memories.router, prefix="/memories", tags=["Memories"])
api_router.include_router(media.router, prefix="/media", tags=["Media"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
api_router.include_router(people.router, prefix="/people", tags=["People"])
api_router.include_router(relationships.router, prefix="/relationships", tags=["Relationships"])
api_router.include_router(conversation.router, prefix="/conversation", tags=["Conversation"])
api_router.include_router(conversation.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(embeddings.router, prefix="/embeddings", tags=["Embeddings"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice"])
api_router.include_router(avatar.router, prefix="/avatar", tags=["Avatar & Presence"])
api_router.include_router(memory_room.router, prefix="/memory-room", tags=["3D Memory Room"])
api_router.include_router(family.router, prefix="/family", tags=["Family Collaboration"])
api_router.include_router(provenance.router, prefix="/provenance", tags=["Provenance"])
api_router.include_router(confidence.router, prefix="/confidence", tags=["Confidence"])
api_router.include_router(guardian.router, prefix="/guardian", tags=["Memory Guardian"])
api_router.include_router(security.router, prefix="/security", tags=["Security & Privacy"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Dashboard"])
api_router.include_router(consent.router, prefix="/consent", tags=["Consent Management"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Logs"])
api_router.include_router(processing.router, prefix="/processing", tags=["Multimodal Processing"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["Evidence Explorer"])
api_router.include_router(memory_dna.router, prefix="/memory-dna", tags=["Memory DNA"])
api_router.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph"])
api_router.include_router(retrieval.router, prefix="/retrieval", tags=["Retrieval Engine"])
api_router.include_router(research.router, prefix="/research", tags=["Research & Benchmarks"])


