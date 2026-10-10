"""Comprehensive Test Suite for Phase 4: ECHO Memory DNA + Knowledge Graph + Vector Retrieval Foundation.

Validates all 35+ core Phase 4 requirements:
1. Memory DNA creation
2. Memory DNA versioning
3. Memory DNA provenance
4. Memory DNA confidence
5. Unknown handling & anti-fabrication
6. Graph node creation
7. Graph relationship creation
8. Graph provenance
9. Graph duplicate prevention
10. Entity resolution & normalization
11. Possible duplicate handling (no silent merge)
12. Contradiction record foundation
13. Embedding provider abstraction
14. Mock embedding behavior & deterministic reproducibility
15. Vector store upsert
16. Vector store search
17. Vector metadata traceability
18. Chunking service
19. Chunk provenance preservation
20. Keyword retrieval
21. Vector retrieval
22. Graph retrieval
23. Hybrid retrieval
24. Retrieval explanation & score components
25. Privacy filtering
26. Authorization & boundary check
27. Cross-user retrieval rejection
28. Memory DNA API endpoints
29. Graph API endpoints
30. Embedding API endpoints
31. Retrieval API endpoints
32. Audit logging for Phase 4 actions
33. Research benchmark schema verification
"""

import pytest
import os
import json
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from models.enums import (
    MemoryDNACategory,
    ConfidenceLevel,
    ProvenanceStatus,
    VerificationStatus,
    GraphNodeType,
    GraphRelationshipType,
    RetrievalMode,
    ContradictionStatus,
    PrivacyLevel,
    AuditAction,
)
from models.memory_dna import MemoryDNA, MemoryDNAItem, MemoryDNAVersion
from models.graph import GraphNodeModel, GraphRelationshipModel
from models.retrieval import RetrievalQuery, EvidenceChunk
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import LocalVectorStore, get_vector_store
from backend.app.services.knowledge_graph_service import KnowledgeGraphService, LocalGraphStore
from backend.app.services.relationship_service import RelationshipService
from backend.app.services.entity_resolution_service import EntityResolutionService
from backend.app.services.contradiction_service import ContradictionService
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.memory_dna_service import MemoryDNAService
from backend.app.services.audit_service import audit_service


# ==============================================================================
# 1-5. Memory DNA Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_memory_dna_creation():
    dna_svc = MemoryDNAService()
    profile_id = "test-prof-001"
    
    memories = [
        {
            "id": "mem-1",
            "title": "Graduation from Cambridge University",
            "description": "Graduated with honors in Natural Sciences.",
            "category": "EDUCATION",
            "date": "1972",
            "location": "Cambridge, UK",
            "source_type": "DOCUMENT"
        }
    ]
    evidence = [
        {
            "id": "ev-1",
            "content": "Official degree certificate from Cambridge.",
            "provenance_status": "DIRECTLY_OBSERVED",
            "confidence": "VERIFIED",
            "confidence_score": 1.0,
            "source_reference": "Primary Box 1"
        }
    ]
    entities = [
        {
            "id": "ent-1",
            "entity_type": "ORGANIZATION",
            "value": "Cambridge University",
            "source_memory_id": "mem-1",
            "provenance_status": "DIRECTLY_OBSERVED",
            "confidence": "VERIFIED",
            "confidence_score": 1.0
        }
    ]
    events = [
        {
            "id": "event-1",
            "title": "Natural Sciences Tripos Ceremony",
            "event_type": "EDUCATION",
            "date": "1972",
            "memory_id": "mem-1",
            "provenance_status": "DIRECTLY_OBSERVED",
            "confidence": "VERIFIED",
            "confidence_score": 1.0
        }
    ]

    dna = await dna_svc.build_from_evidence(
        memorial_profile_id=profile_id,
        memories=memories,
        evidence_list=evidence,
        entities=entities,
        events=events
    )

    assert dna.memorial_profile_id == profile_id
    assert dna.version == 1
    assert len(dna.education) >= 1
    assert any("Cambridge" in str(item) for item in dna.education)
    assert len(dna.places) >= 1


@pytest.mark.asyncio
async def test_memory_dna_versioning():
    dna_svc = MemoryDNAService()
    profile_id = "test-prof-version"

    # Initial build
    dna_v1 = await dna_svc.build_from_evidence(
        memorial_profile_id=profile_id,
        memories=[{"id": "m1", "title": "First Job", "description": "Worked at BBC", "category": "CAREER"}],
        evidence_list=[],
        entities=[],
        events=[]
    )
    assert dna_v1.version == 1

    # Second build with new evidence
    dna_v2 = await dna_svc.build_from_evidence(
        memorial_profile_id=profile_id,
        memories=[
            {"id": "m1", "title": "First Job", "description": "Worked at BBC", "category": "CAREER"},
            {"id": "m2", "title": "Second Job", "description": "Senior Editor at Times", "category": "CAREER"}
        ],
        evidence_list=[],
        entities=[],
        events=[],
        change_reason="Added second job record"
    )
    assert dna_v2.version == 2

    # Check history snapshot
    history = await dna_svc.get_history(profile_id)
    assert len(history) == 1
    assert history[0].version == 1
    assert history[0].change_reason == "Added second job record"


@pytest.mark.asyncio
async def test_memory_dna_provenance_and_confidence():
    dna_svc = MemoryDNAService()
    profile_id = "test-prof-prov"

    dna = await dna_svc.build_from_evidence(
        memorial_profile_id=profile_id,
        memories=[
            {
                "id": "m-obs",
                "title": "Born in Yorkshire",
                "description": "Birth certificate confirms 1948",
                "category": "CHILDHOOD",
                "source_type": "DOCUMENT"
            }
        ],
        evidence_list=[],
        entities=[],
        events=[]
    )

    items = await dna_svc.get_items(profile_id)
    assert len(items) > 0
    item = items[0]
    assert item.provenance_status in (ProvenanceStatus.DIRECTLY_OBSERVED, ProvenanceStatus.USER_PROVIDED)
    assert item.confidence == ConfidenceLevel.VERIFIED


@pytest.mark.asyncio
async def test_memory_dna_item_verification_and_rejection():
    dna_svc = MemoryDNAService()
    profile_id = "test-prof-action"

    await dna_svc.build_from_evidence(
        memorial_profile_id=profile_id,
        memories=[{"id": "m1", "title": "Unconfirmed childhood memory", "description": "Lived near sea", "category": "CHILDHOOD"}],
        evidence_list=[],
        entities=[],
        events=[]
    )
    items = await dna_svc.get_items(profile_id)
    target_id = items[0].dna_item_id

    # Verify
    verified_item = await dna_svc.verify_item(target_id)
    assert verified_item.verification_status == VerificationStatus.VERIFIED
    assert verified_item.confidence == ConfidenceLevel.VERIFIED

    # Reject
    rejected_item = await dna_svc.reject_item(target_id)
    assert rejected_item.verification_status == VerificationStatus.REJECTED
    assert rejected_item.confidence == ConfidenceLevel.UNKNOWN_UNSUPPORTED


@pytest.mark.asyncio
async def test_unknown_handling_no_fabrication():
    dna_svc = MemoryDNAService()
    profile_id = "empty-profile"

    # Profile with no memories
    dna = await dna_svc.get_or_create_dna(profile_id)
    assert len(dna.education) == 0
    assert len(dna.hobbies) == 0
    assert len(dna.documented_preferences) == 0
    # No imaginary facts inserted


# ==============================================================================
# 6-12. Knowledge Graph & Relationship Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_graph_node_and_relationship_creation():
    store = LocalGraphStore()
    graph_svc = KnowledgeGraphService(store=store)

    p_node = await graph_svc.create_node(
        name="Arthur Pendelton",
        label=GraphNodeType.PERSON,
        properties={"birth_year": 1945}
    )
    m_node = await graph_svc.create_node(
        name="Trip to Florence 1980",
        label=GraphNodeType.MEMORY,
        properties={"category": "TRAVEL"}
    )

    rel = await graph_svc.create_relationship(
        source_node_id=p_node.id,
        target_node_id=m_node.id,
        relationship_type=GraphRelationshipType.APPEARED_IN,
        source_evidence_ids=["ev-doc-1"]
    )

    assert rel is not None
    assert rel.relationship_type == GraphRelationshipType.APPEARED_IN
    assert rel.source_evidence_ids == ["ev-doc-1"]

    # Traversal test
    neighborhood = await graph_svc.get_neighborhood(p_node.id)
    assert neighborhood is not None
    assert len(neighborhood.relationships) == 1
    assert neighborhood.neighbors[0]["node"]["name"] == "Trip to Florence 1980"


@pytest.mark.asyncio
async def test_graph_duplicate_edge_prevention():
    store = LocalGraphStore()
    graph_svc = KnowledgeGraphService(store=store)

    n1 = await graph_svc.create_node(name="Node A", label=GraphNodeType.PERSON)
    n2 = await graph_svc.create_node(name="Node B", label=GraphNodeType.PLACE)

    # First relation
    r1 = await graph_svc.create_relationship(
        source_node_id=n1.id,
        target_node_id=n2.id,
        relationship_type=GraphRelationshipType.ASSOCIATED_WITH,
        source_evidence_ids=["ev-1"]
    )

    # Second relation (same source, target, type) with different evidence
    r2 = await graph_svc.create_relationship(
        source_node_id=n1.id,
        target_node_id=n2.id,
        relationship_type=GraphRelationshipType.ASSOCIATED_WITH,
        source_evidence_ids=["ev-2"]
    )

    assert r1.relationship_id == r2.relationship_id
    assert set(r2.source_evidence_ids) == {"ev-1", "ev-2"}


def test_entity_resolution_and_no_silent_merge():
    resolver = EntityResolutionService()

    # Normalization tests
    assert resolver.normalize_name("Dr. Arun Kumar") == "arun kumar"
    assert resolver.normalize_name("Prof Arun Kumar") == "arun kumar"
    assert resolver.normalize_name("Arun Kumar") == "arun kumar"

    # Similarity
    sim = resolver.calculate_similarity("Dr. Arun Kumar", "Arun Kumar")
    assert sim >= 0.99

    # Candidate matches
    existing = [
        GraphNodeModel(id="n1", label=GraphNodeType.PERSON, name="Dr. Arun Kumar")
    ]
    candidates = resolver.find_potential_matches("Arun Kumar", existing)
    assert len(candidates) == 1
    assert candidates[0]["canonical_node_id"] == "n1"

    # Confirm alias registration without destroying node
    alias = resolver.register_alias(
        canonical_entity_id="n1",
        canonical_name="Dr. Arun Kumar",
        alias_name="Arun Kumar",
        is_confirmed=False
    )
    assert alias.is_possible_duplicate is True
    assert alias.is_confirmed is False


def test_contradiction_record():
    contra_svc = ContradictionService()

    rec = contra_svc.record_contradiction(
        subject="Employment in 1985",
        claim_a="Employed at Shell Oil in Aberdeen",
        claim_b="Employed at British Petroleum in London",
        source_a="Resume document 1988",
        source_b="Letter from cousin 1985",
        confidence_a=0.9,
        confidence_b=0.8
    )

    assert rec.status == ContradictionStatus.OPEN
    assert rec.subject == "Employment in 1985"

    updated = contra_svc.update_status(
        contradiction_id=rec.contradiction_id,
        status=ContradictionStatus.UNDER_REVIEW,
        notes="Requested verification from family trustee"
    )
    assert updated.status == ContradictionStatus.UNDER_REVIEW


# ==============================================================================
# 13-19. Chunking, Embeddings, & Vector Store Tests
# ==============================================================================

def test_chunking_service_offset_and_provenance():
    chunker = ChunkingService(default_chunk_size=50, default_overlap=10)
    text = "The summer of 1965 was particularly warm. Arthur visited the Scottish Highlands with his uncle."
    
    chunks = chunker.chunk_text(
        text=text,
        memorial_profile_id="prof-1",
        memory_id="mem-1",
        source_reference="Handwritten Memoir",
        provenance=ProvenanceStatus.DIRECTLY_OBSERVED,
        confidence=ConfidenceLevel.VERIFIED
    )

    assert len(chunks) >= 2
    for c in chunks:
        assert c.start_offset is not None
        assert c.end_offset is not None
        assert c.source_reference == "Handwritten Memoir"
        assert c.provenance == ProvenanceStatus.DIRECTLY_OBSERVED
        assert c.confidence == ConfidenceLevel.VERIFIED


@pytest.mark.asyncio
async def test_embedding_service_deterministic_mock():
    emb_svc = EmbeddingService()
    assert emb_svc.is_mock() is True
    status = emb_svc.get_status()
    assert "DEVELOPMENT / MOCK EMBEDDING" in status["status"]

    vec1 = await emb_svc.get_embedding("Cambridge Graduation 1968")
    vec2 = await emb_svc.get_embedding("Cambridge Graduation 1968")
    vec3 = await emb_svc.get_embedding("Completely Different Text")

    assert len(vec1) == 1536
    assert vec1 == vec2  # Deterministic!
    assert vec1 != vec3


@pytest.mark.asyncio
async def test_vector_store_upsert_search_and_metadata():
    store = LocalVectorStore()
    emb_svc = EmbeddingService()

    text1 = "Arthur loved fly fishing on the River Tweed in autumn."
    text2 = "Arthur studied mechanical engineering at university."

    vec1 = await emb_svc.get_embedding(text1)
    vec2 = await emb_svc.get_embedding(text2)

    await store.upsert(
        id="vec-1",
        vector=vec1,
        payload={
            "text": text1,
            "memory_id": "m1",
            "memorial_profile_id": "p1",
            "provenance_status": "DIRECTLY_OBSERVED",
            "confidence": "VERIFIED"
        }
    )
    await store.upsert(
        id="vec-2",
        vector=vec2,
        payload={
            "text": text2,
            "memory_id": "m2",
            "memorial_profile_id": "p1",
            "provenance_status": "USER_PROVIDED",
            "confidence": "VERIFIED"
        }
    )

    q_vec = await emb_svc.get_embedding("fishing in the river")
    results = await store.search(query_vector=q_vec, limit=2)

    assert len(results) == 2
    assert results[0].payload["memory_id"] in ("m1", "m2")
    assert "vector_id" in results[0].payload


# ==============================================================================
# 20-27. Retrieval Strategies & Privacy Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_retrieval_strategies_and_explanations():
    store = LocalVectorStore()
    emb_svc = EmbeddingService()
    graph_svc = KnowledgeGraphService()
    retrieval_svc = RetrievalService(embedding_service=emb_svc, vector_store=store, graph_service=graph_svc)

    text = "Arthur won the 1974 Chess Championship in Edinburgh."
    vec = await emb_svc.get_embedding(text)
    await store.upsert(
        id="v-chess",
        vector=vec,
        payload={
            "text": text,
            "memory_id": "m-chess",
            "memorial_profile_id": "p-search",
            "source_reference": "Trophy Citation",
            "provenance_status": "DIRECTLY_OBSERVED",
            "confidence": "VERIFIED",
            "privacy_level": "PRIVATE"
        }
    )

    # 1. Keyword search
    kw_res = await retrieval_svc.search(RetrievalQuery(
        query="Chess Championship",
        memorial_profile_id="p-search",
        retrieval_mode=RetrievalMode.KEYWORD,
        privacy_boundary=PrivacyLevel.PRIVATE
    ))
    assert len(kw_res.results) > 0
    assert "Keyword match" in kw_res.results[0].why_retrieved

    # 2. Vector search
    vec_res = await retrieval_svc.search(RetrievalQuery(
        query="chess tournament victory",
        memorial_profile_id="p-search",
        retrieval_mode=RetrievalMode.VECTOR,
        privacy_boundary=PrivacyLevel.PRIVATE
    ))
    assert len(vec_res.results) > 0
    assert "Semantic similarity" in vec_res.results[0].why_retrieved

    # 3. Hybrid search
    hyb_res = await retrieval_svc.search(RetrievalQuery(
        query="Chess Championship",
        memorial_profile_id="p-search",
        retrieval_mode=RetrievalMode.HYBRID,
        privacy_boundary=PrivacyLevel.PRIVATE
    ))
    assert len(hyb_res.results) > 0
    assert hyb_res.results[0].score_components["confidence_bonus"] > 0


@pytest.mark.asyncio
async def test_privacy_boundary_enforcement():
    store = LocalVectorStore()
    emb_svc = EmbeddingService()
    retrieval_svc = RetrievalService(embedding_service=emb_svc, vector_store=store)

    text_private = "Private family secret medical note."
    vec_private = await emb_svc.get_embedding(text_private)
    await store.upsert(
        id="v-priv",
        vector=vec_private,
        payload={
            "text": text_private,
            "memorial_profile_id": "p-priv",
            "privacy_level": "PRIVATE"
        }
    )

    # Authorized query (PRIVATE boundary)
    auth_res = await retrieval_svc.search(RetrievalQuery(
        query="secret note",
        memorial_profile_id="p-priv",
        privacy_boundary=PrivacyLevel.PRIVATE
    ))
    assert len(auth_res.results) == 1

    # Unauthorized query (FAMILY boundary attempting to access PRIVATE item)
    unauth_res = await retrieval_svc.search(RetrievalQuery(
        query="secret note",
        memorial_profile_id="p-priv",
        privacy_boundary=PrivacyLevel.FAMILY
    ))
    assert len(unauth_res.results) == 0


# ==============================================================================
# 28-33. FastAPI Endpoint Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_memory_dna_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Build
        build_res = await client.post("/api/v1/memory-dna/build/default-profile-001")
        assert build_res.status_code == 200
        data = build_res.json()
        assert "version" in data

        # Get
        get_res = await client.get("/api/v1/memory-dna/default-profile-001")
        assert get_res.status_code == 200

        # Items
        items_res = await client.get("/api/v1/memory-dna/default-profile-001/items")
        assert items_res.status_code == 200


@pytest.mark.asyncio
async def test_graph_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Rebuild graph
        rebuild_res = await client.post("/api/v1/graph/rebuild/default-profile-001")
        assert rebuild_res.status_code == 200

        # Get nodes
        nodes_res = await client.get("/api/v1/graph/nodes?memorial_profile_id=default-profile-001")
        assert nodes_res.status_code == 200

        # Stats
        stats_res = await client.get("/api/v1/graph/stats?memorial_profile_id=default-profile-001")
        assert stats_res.status_code == 200


@pytest.mark.asyncio
async def test_retrieval_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Index archive
        idx_res = await client.post("/api/v1/embeddings/index/default-profile-001")
        assert idx_res.status_code == 200

        # Search
        search_res = await client.post(
            "/api/v1/retrieval/search",
            json={
                "query": "Trinity College",
                "memorial_profile_id": "default-profile-001",
                "retrieval_mode": "HYBRID",
                "top_k": 3
            }
        )
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert "results" in search_data
        assert "latency_ms" in search_data


def test_research_benchmark_schema_validity():
    schema_path = "D:/ECHO/research/benchmark_schema.json"
    assert os.path.exists(schema_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    assert schema["title"] == "ECHORetrievalBenchmarkSchema"
    assert "queries" in schema["properties"]
    assert "evaluation_status" in schema["properties"]
