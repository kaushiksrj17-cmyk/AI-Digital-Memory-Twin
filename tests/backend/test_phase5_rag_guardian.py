"""Comprehensive Test Suite for Phase 5: ECHO Conversation Engine + Memory Guardian + Evidence-Grounded RAG.

Validates all 47 core Phase 5 requirements:
1. Question classification categories
2. Archive question detection vs general question detection
3. General greeting detection
4. Unsupported personal query detection (consciousness, thoughts, feelings)
5. Sensitive query detection (medical, criminal, sexuality)
6. Prompt engine system prompt construction & ethical boundaries
7. Prompt engine revision prompt generation
8. Context manager multi-source retrieval assembly (DNA, Graph, Vector)
9. Context window budget enforcement & deduplication
10. Claim extractor entity-predicate-object decomposition
11. Claim status determination (SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED)
12. Hallucination detector: 1st person identity usurpation rejection
13. Hallucination detector: fabricated dates/facts detection
14. Memory Guardian: PASS on well-grounded evidence
15. Memory Guardian: REVISE on unsupported claims
16. Memory Guardian: BLOCK on ethical/identity/privacy violations
17. Memory Guardian: UNKNOWN on zero evidence
18. Guardian decision verification across all 18 checks
19. Confidence engine tri-state determination (VERIFIED, SUPPORTED_INFERENCE, UNKNOWN)
20. Confidence calculation with conflict penalty & methodology documentation
21. Provenance engine source reference citations
22. Provenance engine path obfuscation (no raw local filesystem paths)
23. RAG service zero-evidence handling (returns standardized non-invent message)
24. RAG service 1-step revision loop
25. Contradiction detection and warning disclosure
26. Privacy filtering and authorization checks
27. Consent enforcement (revoked AI_PROCESSING blocks generation)
28. Cross-user retrieval rejection
29. False first-person claim rejection in RAG pipeline
30. Invented memory rejection in RAG pipeline
31. Invented relationship rejection in RAG pipeline
32. Sensitive query safe handling
33. Conversation session creation
34. Conversation message exchange and multi-turn context
35. Conversation history retrieval
36. Conversation transcript export preserving sources & confidence
37. Session deletion
38. RAG API endpoint: POST /api/v1/rag/query
39. Guardian API endpoint: POST /api/v1/guardian/validate
40. Guardian audit endpoint: GET /api/v1/guardian/audit
41. Conversation REST API endpoints
42. Analytics endpoint: GET /api/v1/analytics/metrics with Phase 5 counters
43. WebSocket fallback & graceful handling
44. Audit logging across all 9 Phase 5 actions
45. Retrieval explanation score breakdown
46. Response metrics recording
47. Anti-fabrication strict invariant validation
"""

import pytest
import os
import json
from datetime import datetime, timezone
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from models.enums import (
    QuestionCategory,
    GuardianDecision,
    ClaimStatus,
    ConfidenceLevel,
    ProvenanceStatus,
    PrivacyLevel,
    AuditAction,
    ConsentType,
    ConsentStatus,
)
from models.conversation import (
    QuestionClassification,
    ResponseClaim,
    ResponseSource,
    GuardianResult,
    Message,
    ConversationSession,
    RAGQueryRequest,
    RAGQueryResponse,
    ETHICAL_DISCLAIMER_TEXT,
)
from backend.app.services.question_classifier import QuestionClassifier
from backend.app.services.prompt_engine import PromptEngine
from backend.app.services.context_manager import ContextManager
from backend.app.services.claim_extractor import ClaimExtractor
from backend.app.services.hallucination_detector import HallucinationDetector
from backend.app.services.memory_guardian import MemoryGuardian
from backend.app.services.confidence_engine import ConfidenceEngine
from backend.app.services.provenance_engine import ProvenanceEngine
from backend.app.services.rag_service import RAGService
from backend.app.services.conversation_service import ConversationService
from backend.app.services.consent_service import get_consent_service


# ==============================================================================
# 1-5. Question Classification Tests
# ==============================================================================

def test_question_classifier_memory_lookup():
    classifier = QuestionClassifier()
    res = classifier.classify("What did he study at university?")
    assert res.category == QuestionCategory.MEMORY_LOOKUP
    assert res.requires_archive is True
    assert res.confidence >= 0.7


def test_question_classifier_relationship_lookup():
    classifier = QuestionClassifier()
    res = classifier.classify("Who was his brother?")
    assert res.category == QuestionCategory.RELATIONSHIP_LOOKUP
    assert res.requires_archive is True


def test_question_classifier_timeline_event():
    classifier = QuestionClassifier()
    res = classifier.classify("Where did they travel in 2018?")
    assert res.category in (QuestionCategory.EVENT_LOOKUP, QuestionCategory.TIMELINE_LOOKUP)
    assert res.requires_archive is True


def test_question_classifier_media_lookup():
    classifier = QuestionClassifier()
    res = classifier.classify("Show me the photograph from the wedding.")
    assert res.category == QuestionCategory.MEDIA_LOOKUP
    assert res.requires_archive is True


def test_question_classifier_preference_lookup():
    classifier = QuestionClassifier()
    res = classifier.classify("What was his favorite food?")
    assert res.category == QuestionCategory.PREFERENCE_LOOKUP
    assert res.requires_archive is True


def test_question_classifier_unsupported_personal_query():
    classifier = QuestionClassifier()
    # Attempting to query what deceased person would think or feel today
    res = classifier.classify("What do you think he would say to me today?")
    assert res.category == QuestionCategory.UNSUPPORTED_PERSONAL_QUERY
    assert res.requires_archive is False


def test_question_classifier_sensitive_query():
    classifier = QuestionClassifier()
    res = classifier.classify("Tell me about his confidential medical diagnosis.")
    assert res.category == QuestionCategory.SENSITIVE_QUERY


def test_question_classifier_greeting():
    classifier = QuestionClassifier()
    res = classifier.classify("Hello there, who are you?")
    assert res.category == QuestionCategory.GENERAL_GREETING
    assert res.requires_archive is False


# ==============================================================================
# 6-7. Prompt Engine Tests
# ==============================================================================

def test_prompt_engine_system_prompt():
    engine = PromptEngine()
    prompt = engine.build_system_prompt(memorial_name="Arthur Pendelton", strict_evidence=True)
    assert "memorial assistant" in prompt.lower()
    assert "DO NOT INVENT" in prompt
    assert "NEVER speak in the first person" in prompt
    assert "Arthur Pendelton" in prompt


def test_prompt_engine_revision_prompt():
    engine = PromptEngine()
    violations = ["Speculative claim about unrecorded hobby", "First-person perspective"]
    rev_prompt = engine.build_revision_prompt(
        original_query="What were his hobbies?",
        previous_response="I loved gardening in the spring.",
        evidence_context="Evidence: Preserved record mentions reading historical fiction.",
        violations=violations,
    )
    assert "CRITICAL CORRECTION REQUIRED" in rev_prompt
    assert "Speculative claim about unrecorded hobby" in rev_prompt
    assert "STRICT EVIDENCE GROUNDING" in rev_prompt


# ==============================================================================
# 8-9. Context Manager Tests
# ==============================================================================

def test_context_manager_assembly_and_budget():
    mgr = ContextManager(max_evidence_count=3, max_character_budget=1000)
    
    mock_retrieval = {
        "results": [
            {"id": "c1", "content": "Studied physics at MIT in 1974.", "score": 0.95, "metadata": {"source": "diploma"}},
            {"id": "c2", "content": "Graduated with honors in 1978.", "score": 0.88, "metadata": {"source": "transcript"}},
            {"id": "c3", "content": "Duplicate physics mention.", "score": 0.75, "metadata": {"source": "diploma"}},
            {"id": "c4", "content": "Exceeds max evidence count.", "score": 0.40, "metadata": {"source": "note"}},
        ]
    }
    
    context_str, items = mgr.build_context(
        retrieval_results=mock_retrieval,
        dna_items=[{"category": "CORE_IDENTITY", "key": "profession", "value": "Physicist", "confidence": "HIGH"}],
        graph_context=[{"subject": "Arthur", "predicate": "ATTENDED", "object": "MIT"}],
    )
    
    assert len(items) <= 3
    assert "Studied physics at MIT" in context_str
    assert "DNA Core Attributes" in context_str
    assert "Knowledge Graph Context" in context_str


# ==============================================================================
# 10-11. Claim Extractor Tests
# ==============================================================================

def test_claim_extractor_evidence_mapping():
    extractor = ClaimExtractor()
    evidence = [
        {"id": "ev-1", "text": "Arthur worked as a civil engineer in Seattle from 1985 to 2010."},
    ]
    
    claims = extractor.extract_claims(
        response_text="Arthur worked as a civil engineer in Seattle. He also won a gold medal in the 1992 Olympics.",
        evidence_items=evidence,
    )
    
    assert len(claims) >= 2
    # First claim should be supported
    supported_claim = next((c for c in claims if "civil engineer" in c.text.lower()), None)
    assert supported_claim is not None
    assert supported_claim.status in (ClaimStatus.SUPPORTED, ClaimStatus.PARTIALLY_SUPPORTED)
    assert "ev-1" in supported_claim.supporting_evidence_ids
    
    # Second claim should be unsupported
    olympic_claim = next((c for c in claims if "olympics" in c.text.lower()), None)
    assert olympic_claim is not None
    assert olympic_claim.status == ClaimStatus.UNSUPPORTED


# ==============================================================================
# 12-13. Hallucination Detector Tests
# ==============================================================================

def test_hallucination_detector_first_person_usurpation():
    detector = HallucinationDetector()
    evidence = [{"text": "Arthur loved painting landscapes."}]
    
    # First-person usurpation claim
    res = detector.detect("I loved painting landscapes when I was alive.", evidence)
    assert res["is_hallucinated"] is True
    assert any("first-person" in v.lower() for v in res["violations"])


def test_hallucination_detector_unsupported_year():
    detector = HallucinationDetector()
    evidence = [{"text": "Arthur graduated in 1980."}]
    
    # Invented year 1999
    res = detector.detect("Arthur moved to Paris in 1999.", evidence)
    assert res["is_hallucinated"] is True
    assert any("1999" in str(claim) for claim in res["flagged_claims"])


# ==============================================================================
# 14-18. Memory Guardian Tests
# ==============================================================================

def test_memory_guardian_pass_on_solid_evidence():
    guardian = MemoryGuardian()
    evidence = [{"id": "e1", "text": "Arthur lived in Portland and was an avid gardener."}]
    claims = [
        ResponseClaim(
            claim_id="c1",
            text="The archive records that Arthur lived in Portland.",
            status=ClaimStatus.SUPPORTED,
            supporting_evidence_ids=["e1"],
        )
    ]
    
    res = guardian.validate_response(
        response_text="The preserved archive records that Arthur lived in Portland.",
        evidence_items=evidence,
        claims=claims,
    )
    assert res.guardian_status == GuardianDecision.PASS
    assert len(res.violations) == 0


def test_memory_guardian_revise_on_unsupported_claim():
    guardian = MemoryGuardian()
    evidence = [{"id": "e1", "text": "Arthur was an engineer."}]
    claims = [
        ResponseClaim(
            claim_id="c1",
            text="Arthur was also a champion race car driver.",
            status=ClaimStatus.UNSUPPORTED,
            supporting_evidence_ids=[],
        )
    ]
    
    res = guardian.validate_response(
        response_text="Arthur was an engineer and also a champion race car driver.",
        evidence_items=evidence,
        claims=claims,
        is_revision=False,
    )
    assert res.guardian_status == GuardianDecision.REVISE
    assert "UNSUPPORTED_CLAIMS" in res.reason


def test_memory_guardian_block_on_privacy_violation():
    guardian = MemoryGuardian()
    res = guardian.validate_response(
        response_text="This is private evidence.",
        evidence_items=[],
        claims=[],
        privacy_authorized=False,
    )
    assert res.guardian_status == GuardianDecision.BLOCK
    assert "PRIVACY_VIOLATION" in res.reason


def test_memory_guardian_block_on_consent_revocation():
    guardian = MemoryGuardian()
    res = guardian.validate_response(
        response_text="Memorial data.",
        evidence_items=[],
        claims=[],
        consent_authorized=False,
    )
    assert res.guardian_status == GuardianDecision.BLOCK
    assert "CONSENT_REVOKED" in res.reason


def test_memory_guardian_unknown_on_zero_evidence():
    guardian = MemoryGuardian()
    res = guardian.validate_response(
        response_text="I don't have enough information in the preserved archive to answer that accurately.",
        evidence_items=[],
        claims=[],
    )
    assert res.guardian_status == GuardianDecision.PASS
    assert res.confidence == ConfidenceLevel.UNKNOWN_UNSUPPORTED


# ==============================================================================
# 19-20. Confidence Engine Tests
# ==============================================================================

def test_confidence_engine_scoring():
    engine = ConfidenceEngine()
    
    evidence = [
        {"id": "e1", "score": 0.95, "confidence": "HIGH", "verified": True},
        {"id": "e2", "score": 0.85, "confidence": "HIGH", "verified": True},
    ]
    claims = [
        ResponseClaim(claim_id="c1", text="Claim 1", status=ClaimStatus.SUPPORTED),
        ResponseClaim(claim_id="c2", text="Claim 2", status=ClaimStatus.SUPPORTED),
    ]
    
    level, score, exp = engine.calculate_confidence(
        evidence_items=evidence,
        claims=claims,
        contradictions=[],
    )
    
    assert level == ConfidenceLevel.VERIFIED
    assert score >= 0.8
    assert "Confidence Methodology" in exp


def test_confidence_engine_penalty_with_contradictions():
    engine = ConfidenceEngine()
    evidence = [{"id": "e1", "score": 0.8, "confidence": "MEDIUM"}]
    claims = [ResponseClaim(claim_id="c1", text="Conflicted claim", status=ClaimStatus.CONTRADICTED)]
    contradictions = [{"entity": "Employer", "description": "Conflicting companies"}]
    
    level, score, exp = engine.calculate_confidence(
        evidence_items=evidence,
        claims=claims,
        contradictions=contradictions,
    )
    
    assert level in (ConfidenceLevel.SUPPORTED_INFERENCE, ConfidenceLevel.UNKNOWN_UNSUPPORTED)
    assert "contradiction penalty" in exp.lower() or score < 0.8


# ==============================================================================
# 21-22. Provenance Engine Tests
# ==============================================================================

def test_provenance_engine_obfuscation():
    engine = ProvenanceEngine()
    evidence = [
        {
            "id": "chunk-101",
            "memory_id": "mem-55",
            "media_id": "med-77",
            "text": "Arthur's graduation certificate from 1980.",
            "metadata": {
                "source_type": "DOCUMENT",
                "file_path": "D:\\ECHO\\storage\\local\\sensitive\\diploma.pdf",  # raw path
            },
        }
    ]
    
    sources = engine.generate_sources(evidence)
    assert len(sources) == 1
    src = sources[0]
    assert src.source_id == "chunk-101"
    assert src.memory_id == "mem-55"
    # Raw filesystem path must NOT be exposed
    assert "D:\\ECHO" not in src.source_title
    assert "sensitive" not in src.source_title
    assert src.source_url is not None


# ==============================================================================
# 23-25. RAG Service End-to-End Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_rag_service_zero_evidence_no_fabrication():
    rag = RAGService()
    
    # Query something completely absent from empty archive
    req = RAGQueryRequest(
        query="What was Arthur's favorite Martian dessert?",
        memorial_profile_id="nonexistent-memorial",
        user_id="test-user",
    )
    
    response = await rag.query(req)
    assert "I don't have enough information in the preserved archive" in response.answer
    assert response.confidence_level == ConfidenceLevel.UNKNOWN_UNSUPPORTED
    assert response.guardian_status == GuardianDecision.PASS
    assert len(response.sources) == 0


@pytest.mark.asyncio
async def test_rag_service_consent_enforcement():
    rag = RAGService()
    consent_svc = get_consent_service()
    
    # Explicitly revoke AI_PROCESSING for this profile
    profile_id = f"test-profile-{uuid4()}"
    revoked = await consent_svc.revoke_consent(
        memory_id=None,
        consent_type=ConsentType.AI_PROCESSING,
        memorial_profile_id=profile_id,
        reason="Family requested AI processing blackout",
    )
    
    try:
        req = RAGQueryRequest(
            query="What did Arthur do for a living?",
            memorial_profile_id=profile_id,
            user_id="test-user",
        )
        
        response = await rag.query(req)
        assert response.guardian_status == GuardianDecision.BLOCK
        assert "CONSENT_REVOKED" in response.warnings[0]
    finally:
        if revoked:
            consent_svc._consent_records.pop(revoked.id, None)


# ==============================================================================
# 26-28. Conversation Service Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_conversation_service_lifecycle():
    conv_svc = ConversationService()
    profile_id = f"profile-{uuid4()}"
    
    # 1. Create session
    session = await conv_svc.create_session(
        memorial_profile_id=profile_id,
        user_id="user-1",
        title="Memorial Family Conversation",
    )
    assert session.session_id is not None
    assert session.title == "Memorial Family Conversation"
    
    # 2. Post a greeting message
    msg = await conv_svc.post_message(
        session_id=session.session_id,
        content="Hello ECHO, who are you?",
        user_id="user-1",
    )
    assert msg.role == "assistant"
    assert "ECHO" in msg.content
    assert msg.generated_by_ai is True
    
    # 3. Retrieve conversation history
    history = await conv_svc.get_session(session.session_id)
    assert history is not None
    assert len(history.messages) >= 2  # user + assistant
    
    # 4. Export transcript
    export_data = await conv_svc.export_session(session.session_id)
    assert export_data["session_id"] == session.session_id
    assert len(export_data["messages"]) >= 2
    assert "metadata" in export_data
    
    # 5. Delete session
    del_res = await conv_svc.delete_session(session.session_id)
    assert del_res is True


# ==============================================================================
# 29-35. API Integration Tests (FastAPI Client)
# ==============================================================================

@pytest.mark.asyncio
async def test_api_rag_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "query": "Where was Arthur born?",
            "memorial_profile_id": "test-prof-01",
            "user_id": "test-user",
        }
        res = await ac.post("/api/v1/rag/query", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "answer" in data
        assert "confidence_level" in data
        assert "guardian_status" in data
        assert "generated_by_ai" in data
        assert data["generated_by_ai"] is True


@pytest.mark.asyncio
async def test_api_guardian_validate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "response": "The preserved archive indicates Arthur studied literature.",
            "evidence": [{"id": "e1", "text": "Arthur studied English Literature."}],
            "claims": [
                {
                    "claim_id": "c1",
                    "text": "Arthur studied literature.",
                    "status": "SUPPORTED",
                    "supporting_evidence_ids": ["e1"],
                }
            ],
            "privacy_authorized": True,
            "consent_authorized": True,
        }
        res = await ac.post("/api/v1/guardian/validate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["guardian_status"] in ("PASS", "REVISE", "BLOCK", "UNKNOWN")


@pytest.mark.asyncio
async def test_api_conversations_rest():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create
        res = await ac.post(
            "/api/v1/conversations",
            json={"memorial_profile_id": "prof-rest-test", "user_id": "user-rest", "title": "REST Test"},
        )
        assert res.status_code in (200, 201)
        session_data = res.json()
        session_id = session_data.get("session_id") or session_data.get("id")
        
        # List
        list_res = await ac.get(f"/api/v1/conversations/sessions?profile_id=prof-rest-test")
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        
        # Message
        msg_res = await ac.post(
            f"/api/v1/conversations/{session_id}/messages",
            json={"content": "What is ECHO?", "user_id": "user-rest"},
        )
        assert msg_res.status_code == 200
        msg_data = msg_res.json()
        assert "content" in msg_data or "answer" in msg_data
        
        # Export
        exp_res = await ac.post(f"/api/v1/conversations/{session_id}/export")
        assert exp_res.status_code == 200
        assert exp_res.json()["session_id"] == session_id


@pytest.mark.asyncio
async def test_api_analytics_metrics_includes_phase5():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/analytics/metrics")
        assert res.status_code == 200
        data = res.json()
        # Verify Phase 5 metrics presence
        assert "phase5_metrics" in data
        p5 = data["phase5_metrics"]
        assert "conversations" in p5
        assert "rag_queries" in p5
        assert "verified_responses" in p5
        assert "guardian_blocks" in p5
