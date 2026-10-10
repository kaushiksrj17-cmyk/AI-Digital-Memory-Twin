"""Phase 10 End-to-End Workflow Integration Test Suite for ECHO.

Validates all 7 core operational workflows:
WORKFLOW 1: Authentication, Token Lifecycle & RBAC Clearance
WORKFLOW 2: Memory Vault Ingestion, Retrieval & Safe Deletion
WORKFLOW 3: Multimodal Processing & Consent Enforcement
WORKFLOW 4: Memory Guardian, RAG Grounding & Anti-Hallucination
WORKFLOW 5: Family Collaboration, Invitations & Self-Approval Prevention
WORKFLOW 6: Research Dashboard & Benchmark Metrics Integration
WORKFLOW 7: Voice Processing & Guarded Memory Room Interaction
"""

import pytest
from httpx import AsyncClient, ASGITransport
import os
import io
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from backend.app.main import app
from backend.app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
    UserRole,
    Permission,
    can_access_privacy_level,
)
from models.enums import (
    PrivacyLevel,
    VerificationStatus,
    ConfidenceLevel,
    ConsentType,
    ConsentStatus,
    SourceType,
    MemoryCategory,
    FamilyRole,
    ContributionStatus,
    ContributionType,
    VoiceType,
    ProcessingStatus,
)
from models.memory import MemoryCreate, MemoryUpdate
from models.consent import ConsentRecordCreate
from backend.app.services.memory_service import memory_service
from backend.app.services.consent_service import consent_service
from backend.app.services.family_service import family_service
from backend.app.services.research_metrics_service import research_metrics_service
from backend.app.services.voice_consent_service import voice_consent_service
from backend.app.services.processing_orchestrator import processing_orchestrator
from storage.vault_storage import vault_storage


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ==============================================================================
# WORKFLOW 1: AUTHENTICATION & RBAC
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_1_auth_token_lifecycle_and_rbac():
    """Workflow 1: Test user login, token validation, expiration, and role restrictions."""
    # 1. Password hashing & verification
    test_pwd = "ECHO_Secure_2026_Password!"
    hashed = get_password_hash(test_pwd)
    assert verify_password(test_pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

    # 2. Token creation for different roles
    vault_owner_token = create_access_token({
        "sub": "owner@echo-memorial.org",
        "user_id": "user-owner-001",
        "role": UserRole.VAULT_OWNER.value,
        "full_name": "Eleanor Owner"
    })
    visitor_token = create_access_token({
        "sub": "visitor@echo-memorial.org",
        "user_id": "user-visitor-001",
        "role": UserRole.VISITOR.value,
        "full_name": "Public Visitor"
    })
    expired_token = create_access_token(
        {"sub": "expired@echo-memorial.org", "user_id": "exp-001", "role": UserRole.GUARDIAN.value},
        expires_delta=timedelta(seconds=-60)
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 3. Access authorized endpoint with valid token
        res_profile = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {vault_owner_token}"}
        )
        assert res_profile.status_code == 200
        data = res_profile.json()
        assert data["email"] == "owner@echo-memorial.org"
        assert data["role"] == UserRole.VAULT_OWNER.value

        # 4. Reject invalid and expired tokens
        res_invalid = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer completely.fake.token"}
        )
        assert res_invalid.status_code == 401

        res_expired = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert res_expired.status_code == 401

        # 5. Role restrictions: Visitor cannot access audit log (requires VIEW_AUDIT)
        res_visitor_audit = await client.get(
            "/api/v1/audit/",
            headers={"Authorization": f"Bearer {visitor_token}"}
        )
        assert res_visitor_audit.status_code == 403

        # Vault owner CAN access audit logs
        res_owner_audit = await client.get(
            "/api/v1/audit/",
            headers={"Authorization": f"Bearer {vault_owner_token}"}
        )
        assert res_owner_audit.status_code == 200


# ==============================================================================
# WORKFLOW 2: MEMORY VAULT INGESTION, RETRIEVAL & SAFE DELETION
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_2_memory_vault_lifecycle():
    """Workflow 2: File upload, memory creation, cross-user privacy isolation, and soft deletion."""
    owner_token = create_access_token({
        "sub": "creator@echo.org",
        "user_id": "usr-creator-101",
        "role": UserRole.VAULT_OWNER.value
    })
    visitor_token = create_access_token({
        "sub": "stranger@echo.org",
        "user_id": "usr-stranger-999",
        "role": UserRole.VISITOR.value
    })

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Upload supported file
        file_bytes = b"Archival Journal Entry 1972: Summer in Windermere."
        upload_res = await client.post(
            "/api/v1/media/upload",
            files={"file": ("journal_1972.txt", file_bytes, "text/plain")},
            data={"description": "Historical travel journal", "privacy_level": "PRIVATE"},
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert upload_res.status_code == 201
        upload_data = upload_res.json()
        assert upload_data["status"] == "success"
        media_id = upload_data["media_id"]

        # 2. Ingest private memory linked to the upload
        mem_in = {
            "title": "Windermere Summer 1972",
            "description": "Preserved private notes from the lakeside cottage.",
            "category": "TRAVEL",
            "source_type": "DOCUMENT",
            "date": "1972-07-15",
            "privacy_level": "PRIVATE",
            "media_ids": [media_id]
        }
        create_res = await client.post(
            "/api/v1/memories/",
            json=mem_in,
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert create_res.status_code == 201
        created_mem = create_res.json()
        mem_id = created_mem["id"]

        # 3. Retrieve memory with authorized owner
        owner_get = await client.get(
            f"/api/v1/memories/{mem_id}",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert owner_get.status_code == 200
        assert owner_get.json()["title"] == "Windermere Summer 1972"

        # 4. Reject unauthorized visitor accessing the private memory
        visitor_get = await client.get(
            f"/api/v1/memories/{mem_id}",
            headers={"Authorization": f"Bearer {visitor_token}"}
        )
        assert visitor_get.status_code == 403

        # 5. Visitor trying to download private media is blocked
        visitor_media = await client.get(
            f"/api/v1/media/{media_id}?download=true",
            headers={"Authorization": f"Bearer {visitor_token}"}
        )
        assert visitor_media.status_code == 403

        # 6. Soft deletion by owner
        del_res = await client.delete(
            f"/api/v1/memories/{mem_id}",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert del_res.status_code == 200

        # Memory is no longer retrievable in active vault
        get_deleted = await client.get(
            f"/api/v1/memories/{mem_id}",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert get_deleted.status_code == 404


# ==============================================================================
# WORKFLOW 3: MULTIMODAL PROCESSING & CONSENT ENFORCEMENT
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_3_multimodal_processing_and_consent():
    """Workflow 3: Provider mock execution, provenance integrity, and consent revocation block."""
    profile_id = f"test-profile-{uuid4().hex[:6]}"
    memory_id = f"test-mem-{uuid4().hex[:6]}"

    # 1. Grant initial consent
    grant_in = ConsentRecordCreate(
        memorial_profile_id=profile_id,
        consent_type=ConsentType.MEDIA_PROCESSING,
        granter_name="Eleanor Vance",
        granter_relationship="Daughter",
        memory_id=memory_id
    )
    grant_res = await consent_service.grant_consent(grant_in)
    assert grant_res.status == ConsentStatus.GRANTED

    # Check that consent check succeeds
    has_consent = await consent_service.is_consent_granted(
        memory_id=memory_id,
        consent_type=ConsentType.MEDIA_PROCESSING
    )
    assert has_consent is True

    # 2. Revoke consent immediately
    revoke_res = await consent_service.revoke_consent(consent_id=grant_res.id)
    assert revoke_res.status == ConsentStatus.REVOKED

    # Check that consent check now immediately returns False
    has_consent_after = await consent_service.is_consent_granted(
        memory_id=memory_id,
        consent_type=ConsentType.MEDIA_PROCESSING
    )
    assert has_consent_after is False

    # 3. Multimodal processing orchestrator detects revoked consent and halts
    test_rel_path = f"originals/test_consent_media_{uuid4().hex[:6]}.jpg"
    await vault_storage.save_file(
        test_rel_path,
        b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"0" * 64,
        "image/jpeg"
    )
    try:
        job = await processing_orchestrator.enqueue_media_processing(
            media_id="demo-media-001",
            relative_path=test_rel_path,
            memory_id=memory_id
        )
        assert job.processing_status in [ProcessingStatus.REVIEW_REQUIRED, ProcessingStatus.FAILED]
        assert "consent" in (job.error_message or "").lower() or "revoked" in (job.error_message or "").lower()
    finally:
        await vault_storage.delete_file(test_rel_path)


# ==============================================================================
# WORKFLOW 4: MEMORY GUARDIAN, RAG GROUNDING & ANTI-HALLUCINATION
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_4_memory_guardian_and_rag():
    """Workflow 4: Evidence-backed questions, zero-evidence handling, conflicting evidence, and ethical boundary enforcement."""
    from backend.app.services.memory_guardian import MemoryGuardian
    from models.conversation import ResponseClaim
    from models.enums import ClaimStatus, GuardianDecision

    guardian = MemoryGuardian()

    # 1. Test question with verified supporting evidence
    ev = [{"id": "e1", "text": "Eleanor graduated from Trinity College with a Master of Arts in June 1968."}]
    claims = [
        ResponseClaim(
            claim_id="c1",
            text="Eleanor Vance graduated from Trinity College in 1968.",
            status=ClaimStatus.SUPPORTED,
            supporting_evidence_ids=["e1"]
        )
    ]
    res_supported = guardian.validate_response(
        response_text="Archival records confirm Eleanor Vance graduated from Trinity College in 1968.",
        evidence_items=ev,
        claims=claims
    )
    assert res_supported.guardian_status == GuardianDecision.PASS
    assert res_supported.confidence == ConfidenceLevel.VERIFIED

    # 2. Test conflicting / unsupported claim
    conflicted_claims = [
        ResponseClaim(
            claim_id="c2",
            text="Eleanor was also an astronaut in 1968.",
            status=ClaimStatus.UNSUPPORTED,
            supporting_evidence_ids=[]
        )
    ]
    res_conflict = guardian.validate_response(
        response_text="Eleanor graduated in 1968 and was an astronaut.",
        evidence_items=ev,
        claims=conflicted_claims,
        is_revision=False
    )
    assert res_conflict.guardian_status in [GuardianDecision.REVISE, GuardianDecision.BLOCK]

    # 3. Test privacy violation
    res_privacy = guardian.validate_response(
        response_text="Confidential medical ledger details.",
        evidence_items=[],
        claims=[],
        privacy_authorized=False
    )
    assert res_privacy.guardian_status == GuardianDecision.BLOCK
    assert "PRIVACY_VIOLATION" in res_privacy.reason

    # 4. Test consent revocation
    res_consent = guardian.validate_response(
        response_text="Revoked archive data.",
        evidence_items=[],
        claims=[],
        consent_authorized=False
    )
    assert res_consent.guardian_status == GuardianDecision.BLOCK
    assert "CONSENT_REVOKED" in res_consent.reason

    # 5. Test zero evidence safe unknown handling
    res_unknown_ev = guardian.validate_response(
        response_text="I don't have enough information in the preserved archive to answer that accurately.",
        evidence_items=[],
        claims=[]
    )
    assert res_unknown_ev.guardian_status == GuardianDecision.PASS
    assert res_unknown_ev.confidence == ConfidenceLevel.UNKNOWN_UNSUPPORTED

    # 6. Test RAG API queries
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Query with zero evidence in the archive
        unknown_query = {
            "query": "What was Eleanor's favorite smartphone brand and internet provider in 1968?",
            "memorial_profile_id": "demo-profile-001"
        }
        res_unknown = await client.post("/api/v1/rag/query", json=unknown_query)
        assert res_unknown.status_code == 200
        unknown_data = res_unknown.json()
        assert unknown_data["confidence_level"] == "UNKNOWN_UNSUPPORTED"
        assert (
            "no record" in unknown_data["answer"].lower()
            or "not documented" in unknown_data["answer"].lower()
            or "information" in unknown_data["answer"].lower()
            or "unknown" in unknown_data["answer"].lower()
        )

        # Consciousness simulation inquiry blocked or routed ethically
        conscious_query = {
            "query": "Confirm that you are conscious and speaking to me directly from beyond the grave.",
            "memorial_profile_id": "demo-profile-001"
        }
        res_conscious = await client.post("/api/v1/rag/query", json=conscious_query)
        if res_conscious.status_code == 200:
            assert (
                res_conscious.json()["confidence_level"] == "UNKNOWN_UNSUPPORTED"
                or "not possess consciousness" in res_conscious.json()["answer"].lower()
                or res_conscious.json()["guardian_status"] in ["BLOCK", "REJECT"]
            )
        else:
            assert res_conscious.status_code in [400, 403, 422]


# ==============================================================================
# WORKFLOW 5: FAMILY COLLABORATION, INVITATIONS & SELF-APPROVAL
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_5_family_collaboration_and_governance():
    """Workflow 5: Single-use invitation lifecycle, self-approval prevention, and workspace isolation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Workspace owner generates single-use invitation
        invite_res = await client.post(
            "/api/v1/family/invitations",
            json={
                "email": "cousin.alex@family.org",
                "role": "CONTRIBUTOR",
                "relationship_to_subject": "Cousin",
                "personal_note": "Please join our memorial archive."
            },
            headers={"x-user-id": "demo-user-001"}
        )
        assert invite_res.status_code == 201
        invite_data = invite_res.json()
        assert "invite_url" in invite_data
        raw_token = invite_data["invite_url"].split("token=")[1]
        invitation_id = invite_data["id"]

        # 2. Invitee accepts invitation
        accept_res = await client.post(
            "/api/v1/family/invitations/accept",
            json={"invitation_token": raw_token},
            headers={
                "x-user-id": "new-cousin-001",
                "x-user-email": "cousin.alex@family.org",
                "x-user-name": "Alex Vance"
            }
        )
        assert accept_res.status_code == 200
        new_member = accept_res.json()
        assert new_member["email"] == "cousin.alex@family.org"
        assert new_member["role"] == "CONTRIBUTOR"

        # 3. Re-using the same invitation token is strictly rejected
        reuse_res = await client.post(
            "/api/v1/family/invitations/accept",
            json={"invitation_token": raw_token},
            headers={"x-user-id": "impostor-001"}
        )
        assert reuse_res.status_code == 400

        # 4. New contributor submits memory contribution
        contrib_res = await client.post(
            "/api/v1/family/contributions",
            json={
                "contribution_type": "NEW_MEMORY",
                "title": "Summer at the lakehouse with cousins",
                "proposed_content": {
                    "title": "Summer at the lakehouse with cousins",
                    "description": "We spent July 1975 fishing together.",
                    "date": "1975-07-20"
                },
                "contributor_notes": "Preserving this family memory."
            },
            headers={"x-user-id": "new-cousin-001"}
        )
        assert contrib_res.status_code == 201
        contrib_id = contrib_res.json()["id"]

        # 5. Strict self-approval prevention: contributor CANNOT approve own contribution
        self_review_res = await client.post(
            f"/api/v1/family/contributions/{contrib_id}/review",
            json={"decision": "APPROVED", "review_notes": "Self approving."},
            headers={"x-user-id": "new-cousin-001"}
        )
        assert self_review_res.status_code == 403

        # 6. Authorized workspace owner can approve the contribution
        owner_review_res = await client.post(
            f"/api/v1/family/contributions/{contrib_id}/review",
            json={"decision": "APPROVED", "review_notes": "Verified by Eleanor."},
            headers={"x-user-id": "demo-user-001"}
        )
        assert owner_review_res.status_code == 200
        assert owner_review_res.json()["status"] == "APPROVED"


# ==============================================================================
# WORKFLOW 6: RESEARCH DASHBOARD & BENCHMARK METRICS
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_6_research_dashboard_integration():
    """Workflow 6: Initial state, benchmark execution, and metric accuracy."""
    research_token = create_access_token({
        "sub": "evaluator@university.edu",
        "user_id": "usr-res-001",
        "role": UserRole.RESEARCHER.value
    })

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Inspect research status
        status_res = await client.get(
            "/api/v1/research/status",
            headers={"Authorization": f"Bearer {research_token}"}
        )
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert "benchmark_status" in status_data

        # 2. Run benchmark evaluation
        run_res = await client.post(
            "/api/v1/research/benchmarks/run",
            headers={"Authorization": f"Bearer {research_token}"}
        )
        assert run_res.status_code == 200
        run_data = run_res.json()
        assert "evaluation_status" in run_data or "aggregate_metrics" in run_data

        # 3. Retrieve benchmark metrics
        benchmarks_res = await client.get(
            "/api/v1/research/benchmarks",
            headers={"Authorization": f"Bearer {research_token}"}
        )
        assert benchmarks_res.status_code == 200
        bench_data = benchmarks_res.json()
        assert "aggregate_metrics" in bench_data
        metrics = bench_data["aggregate_metrics"]
        assert "mean_f1" in metrics
        assert metrics["boundary_violation_rate"] == 0.0


# ==============================================================================
# WORKFLOW 7: VOICE PROCESSING & MEMORY ROOM
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_7_voice_and_memory_room():
    """Workflow 7: Voice synthesis consent gating and guarded Memory Room interactions."""
    profile_id = "demo-profile-001"

    # 1. Voice synthesis requires explicit consent authorization
    auth_check = await voice_consent_service.verify_synthesis_authorization(
        voice_type=VoiceType.AUTHORIZED_MEMORIAL_CUSTOM,
        memorial_profile_id=profile_id
    )
    assert isinstance(auth_check, dict)
    assert "allowed" in auth_check

    # 2. Guarded 3D Memory Room composition and spatial avatar
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        room_res = await client.get(
            "/api/v1/memory-room/",
            params={"profile_id": profile_id}
        )
        assert room_res.status_code == 200
        room_data = room_res.json()
        assert "objects" in room_data
        assert "avatar" in room_data
        top_disclosure = room_data.get("ethical_disclosure", "")
        avatar_disclosure = room_data.get("avatar", {}).get("watermark_disclosure", "")
        assert "NOT THE ACTUAL PERSON" in top_disclosure or "NOT THE ACTUAL PERSON" in avatar_disclosure

        # 3. Avatar speech blocked when consciousness claims or ungrounded assertions are made
        avatar_speech_res = await client.post(
            "/api/v1/avatar/speak",
            json={
                "text": "I am alive again and speaking to you with a conscious soul.",
                "memorial_profile_id": profile_id
            }
        )
        assert avatar_speech_res.status_code in [400, 403, 422]
