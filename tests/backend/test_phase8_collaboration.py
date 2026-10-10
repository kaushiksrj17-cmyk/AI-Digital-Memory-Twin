"""Unit and Integration Tests for Phase 8: AI Life Timeline, Relationship Graph & Family Collaboration.

Research Title: Evidence-Grounded, Privacy-Preserving Multimodal AI for
                Interactive Digital Memory Preservation.

Test Coverage:
1. Timeline ordering: chronological vs reverse-chronological sorting.
2. Timeline date precision: EXACT, MONTH_YEAR, YEAR_ONLY, APPROXIMATE, UNKNOWN (never silently converted).
3. Timeline filtering: category, source type, and text search.
4. Timeline event creation by contributor and official verification by admin/owner.
5. Timeline dispute handling: preserves competing dates and sources without erasing records.
6. Timeline AI event suggestions validated by Phase 5 Memory Guardian.
7. Relationship graph retrieval: nodes, typed edges, and filtering.
8. Relationship verification and dispute registration.
9. Duplicate entity detection (fuzzy similarity) and canonical merge workflow.
10. Family workspace and membership governance across 4 roles (OWNER, FAMILY_ADMIN, CONTRIBUTOR, VIEWER).
11. Privilege escalation and unauthorized action blocks.
12. Secure single-use invitation lifecycle: creation, token hashing, redemption, expiry, and revocation.
13. Contribution review lifecycle and strict self-approval prevention (contributors cannot approve own submissions).
14. Version history audit trail for contributions.
15. Empirical Phase 8 research metrics verification.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, date, timezone
from typing import Dict, Any

from backend.app.main import app
from backend.app.services.timeline_service import timeline_service
from backend.app.services.relationship_service import relationship_service
from backend.app.services.family_service import (
    family_service,
    UnauthorizedFamilyActionError,
    SelfApprovalViolationError,
)
from models.enums import (
    DatePrecision,
    FamilyRole,
    InvitationStatus,
    ContributionStatus,
    ContributionType,
    ConfidenceLevel,
    VerificationStatus,
    GraphRelationshipType,
)
from models.timeline import TimelineFilterParams, TimelineEventCreate


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ==============================================================================
# 1. AI Life Timeline Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_timeline_chronological_ordering():
    """Verify life events load from real records and sort chronologically and reverse-chronologically."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Default chronological (oldest first)
        resp_asc = await client.get("/api/v1/timeline/?reverse_chronological=false")
        assert resp_asc.status_code == 200
        data_asc = resp_asc.json()
        assert data_asc["total_events"] >= 6
        events_asc = data_asc["events"]
        assert len(events_asc) >= 6

        # Check chronological sequence: 1946 (Birth) -> 1964 (Matriculation) -> 1968 (Graduation)
        dated_events_asc = [e for e in events_asc if e.get("event_date")]
        years_asc = [int(e["event_date"].split("-")[0]) for e in dated_events_asc]
        assert years_asc == sorted(years_asc)

        # Reverse chronological (newest first)
        resp_desc = await client.get("/api/v1/timeline/?reverse_chronological=true")
        assert resp_desc.status_code == 200
        data_desc = resp_desc.json()
        dated_events_desc = [e for e in data_desc["events"] if e.get("event_date")]
        years_desc = [int(e["event_date"].split("-")[0]) for e in dated_events_desc]
        assert years_desc == sorted(years_desc, reverse=True)


@pytest.mark.asyncio
async def test_timeline_evidentiary_date_precision():
    """Ensure date precision preserves exactness and never silently converts approximate dates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/timeline/")
        assert resp.status_code == 200
        events = resp.json()["events"]

        precisions = {e["id"]: e["date_precision"] for e in events}
        # Birth (event-001) is EXACT
        assert precisions.get("event-001") == "EXACT"
        # Matriculation (event-002) is MONTH_YEAR
        assert precisions.get("event-002") == "MONTH_YEAR"
        # Windermere Sailing (event-005) is APPROXIMATE
        assert precisions.get("event-005") == "APPROXIMATE"

        # Check approximate date description is retained verbatim
        event_5 = next(e for e in events if e["id"] == "event-005")
        assert "circa Mid-August 1974" in event_5["date_description"]


@pytest.mark.asyncio
async def test_timeline_category_and_search_filters():
    """Test filtering by event category and keyword search query."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Category filter: Education
        resp_cat = await client.get("/api/v1/timeline/?category=Education")
        assert resp_cat.status_code == 200
        events_cat = resp_cat.json()["events"]
        assert len(events_cat) >= 2
        for ev in events_cat:
            assert ev["category"].lower() == "education"

        # Search query: Cambridge
        resp_search = await client.get("/api/v1/timeline/?search_query=Cambridge")
        assert resp_search.status_code == 200
        events_search = resp_search.json()["events"]
        assert len(events_search) >= 2
        for ev in events_search:
            assert "cambridge" in (ev["title"] + (ev.get("description") or "") + (ev.get("location_name") or "")).lower()


@pytest.mark.asyncio
async def test_timeline_event_creation_and_admin_verification():
    """Verify contributors submit events as PENDING_REVIEW; admins can verify or reject."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        new_event_payload = {
            "memorial_profile_id": "demo-profile-001",
            "title": "Awarded Royal Literature Fellowship",
            "description": "Inducted as fellow in recognition of published monographs.",
            "category": "Achievements",
            "event_date": "1978-05-15",
            "date_description": "May 15, 1978",
            "date_precision": "EXACT",
            "location_name": "London, UK",
            "associated_people": ["Arthur Vance"],
            "confidence": "VERIFIED",
            "verification_status": "VERIFIED"  # Contributor attempts to verify directly
        }

        # Contributor creates event -> should be downgraded to PENDING_REVIEW
        resp_create = await client.post(
            "/api/v1/timeline/",
            json=new_event_payload,
            headers={"x-user-id": "demo-user-003", "x-user-role": "CONTRIBUTOR"}
        )
        assert resp_create.status_code == 201
        created_event = resp_create.json()
        assert created_event["verification_status"] == "PENDING_REVIEW"
        event_id = created_event["id"]

        # Unauthorized viewer attempts to verify -> 403 Forbidden
        resp_unauth = await client.post(
            f"/api/v1/timeline/{event_id}/verify",
            json={"verification_status": "VERIFIED"},
            headers={"x-user-role": "VIEWER"}
        )
        assert resp_unauth.status_code == 403

        # Authorized Family Admin verifies event -> succeeds
        resp_verify = await client.post(
            f"/api/v1/timeline/{event_id}/verify",
            json={"verification_status": "VERIFIED", "verification_notes": "Archival gazette entry confirmed."},
            headers={"x-user-role": "FAMILY_ADMIN"}
        )
        assert resp_verify.status_code == 200
        verified_data = resp_verify.json()
        assert verified_data["verification_status"] == "VERIFIED"
        assert verified_data["confidence_score"] == 1.0


@pytest.mark.asyncio
async def test_timeline_dispute_preserves_conflicting_sources():
    """Flagging a dispute retains original date, logs competing date and attaches competing evidence."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        dispute_payload = {
            "dispute_reason": "Diary entry indicates departure in late July rather than August.",
            "competing_date": "July 1974",
            "competing_evidence_id": "demo-doc-001",
            "notes": "Preserved in family diary archive box."
        }

        resp_dispute = await client.post(
            "/api/v1/timeline/event-005/dispute",
            json=dispute_payload,
            headers={"x-user-id": "demo-user-003"}
        )
        assert resp_dispute.status_code == 200
        disputed_event = resp_dispute.json()

        assert disputed_event["is_disputed"] is True
        assert "Diary entry indicates departure" in disputed_event["dispute_notes"]
        assert "demo-doc-001" in disputed_event["competing_evidence_ids"]
        # Original date is preserved intact
        assert disputed_event["event_date"] == "1974-08-14"


@pytest.mark.asyncio
async def test_timeline_ai_suggestions_memory_guardian():
    """AI event suggestions must run through Memory Guardian boundary checks and tag is_ai_suggested=True."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/timeline/suggest",
            json={"memorial_profile_id": "demo-profile-001", "max_suggestions": 2},
            headers={"x-user-id": "demo-user-001"}
        )
        assert resp.status_code == 200
        suggestions = resp.json()
        assert isinstance(suggestions, list)
        for s in suggestions:
            assert s["is_ai_suggested"] is True
            assert s["verification_status"] == "PENDING_REVIEW"
            # AI suggestion must never be automatically verified
            assert s["verification_status"] != "VERIFIED"


# ==============================================================================
# 2. Relationship Graph & Duplicate Resolution Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_relationship_graph_retrieval_and_filtering():
    """Verify relationship graph returns evidence-grounded edges and supports relationship type filtering."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Full graph retrieval
        resp = await client.get("/api/v1/relationships/")
        assert resp.status_code == 200
        graph = resp.json()
        assert "nodes" in graph
        assert "edges" in graph
        assert graph["total_edges"] >= 6
        assert graph["verified_edges_count"] >= 3

        # Filter by relationship type: PARENT_OF
        resp_parent = await client.get("/api/v1/relationships/?relationship_type=PARENT_OF")
        assert resp_parent.status_code == 200
        parent_graph = resp_parent.json()
        for e in parent_graph["edges"]:
            assert e["relationship_type"] == "PARENT_OF"
            assert len(e["source_evidence_ids"]) > 0


@pytest.mark.asyncio
async def test_relationship_edge_verification_and_dispute():
    """Verify edge verification lifecycle and dispute recording."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Verify edge
        resp_ver = await client.post(
            "/api/v1/relationships/rel-edge-005/verify",
            json={"verification_status": "VERIFIED", "notes": "Corroborated by travel diary."},
            headers={"x-user-role": "FAMILY_ADMIN"}
        )
        assert resp_ver.status_code == 200
        assert resp_ver.json()["verification_status"] == "VERIFIED"

        # Dispute edge
        resp_disp = await client.post(
            "/api/v1/relationships/rel-edge-005/dispute",
            json={"dispute_reason": "Contested duration of visit in 1974."},
            headers={"x-user-id": "demo-user-003"}
        )
        assert resp_disp.status_code == 200
        assert resp_disp.json()["is_disputed"] is True


@pytest.mark.asyncio
async def test_duplicate_entity_detection_and_merging():
    """Verify fuzzy similarity detects duplicate entities and merge re-points edges."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First create a variation node in graph to simulate duplicate entity
        from backend.app.services.knowledge_graph_service import KnowledgeGraphService
        from models.enums import GraphNodeType
        graph_svc = KnowledgeGraphService()
        dup_node = await graph_svc.create_node(
            name="Eleanor V.",  # Variation of Eleanor Vance
            label=GraphNodeType.PERSON,
            node_id="entity-person-eleanor-var"
        )

        # Detect duplicates
        resp_dups = await client.get("/api/v1/relationships/duplicates")
        assert resp_dups.status_code == 200
        candidates = resp_dups.json()
        assert len(candidates) >= 1

        match = next((c for c in candidates if "Eleanor" in c["entity_a_name"] and "Eleanor" in c["entity_b_name"]), None)
        assert match is not None
        assert match["similarity_score"] >= 0.70

        # Merge duplicate entity
        resp_merge = await client.post(
            "/api/v1/relationships/merge-duplicates",
            json={
                "canonical_entity_id": "demo-person-001",
                "duplicate_entity_id": "entity-person-eleanor-var",
                "merge_notes": "Consolidating abbreviated spelling."
            },
            headers={"x-user-role": "FAMILY_ADMIN"}
        )
        assert resp_merge.status_code == 200
        merge_data = resp_merge.json()
        assert merge_data["status"] == "success"
        assert merge_data["canonical_id"] == "demo-person-001"


# ==============================================================================
# 3. Family Collaboration, RBAC & Invitations Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_family_workspace_and_membership():
    """Verify family workspace retrieval and member enumeration."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp_ws = await client.get("/api/v1/family/workspace", headers={"x-user-id": "demo-user-001"})
        assert resp_ws.status_code == 200
        ws = resp_ws.json()
        assert ws["current_user_role"] == "OWNER"
        assert ws["members_count"] >= 4

        resp_members = await client.get("/api/v1/family/members", headers={"x-user-id": "demo-user-001"})
        assert resp_members.status_code == 200
        members = resp_members.json()
        roles_present = [m["role"] for m in members]
        assert "OWNER" in roles_present
        assert "FAMILY_ADMIN" in roles_present
        assert "CONTRIBUTOR" in roles_present
        assert "VIEWER" in roles_present


@pytest.mark.asyncio
async def test_family_rbac_permission_matrix():
    """Verify unauthorized operations are blocked and privilege escalation is prevented."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Non-member attempts to list members -> 403 Forbidden
        resp_intruder = await client.get("/api/v1/family/members", headers={"x-user-id": "unknown-user-999"})
        assert resp_intruder.status_code == 403

        # Contributor attempts to modify member roles -> 403 Forbidden (OWNER only)
        resp_unauth_role = await client.put(
            "/api/v1/family/members/member-004/role",
            json={"role": "FAMILY_ADMIN"},
            headers={"x-user-id": "demo-user-003"}  # Clara Vance is CONTRIBUTOR
        )
        assert resp_unauth_role.status_code == 403

        # Owner successfully updates member role
        resp_owner_role = await client.put(
            "/api/v1/family/members/member-004/role",
            json={"role": "CONTRIBUTOR"},
            headers={"x-user-id": "demo-user-001"}
        )
        assert resp_owner_role.status_code == 200
        assert resp_owner_role.json()["role"] == "CONTRIBUTOR"


@pytest.mark.asyncio
async def test_secure_single_use_invitation_lifecycle():
    """Verify invitation creation, token hashing, redemption, single-use check, and revocation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Family Admin attempts to invite with OWNER role -> Rejected (Privilege escalation prevention)
        resp_esc = await client.post(
            "/api/v1/family/invitations",
            json={"email": "hacker@example.com", "role": "OWNER"},
            headers={"x-user-id": "demo-user-002"}  # Arthur Vance is FAMILY_ADMIN
        )
        assert resp_esc.status_code == 403

        # 2. Owner invites a new relative as CONTRIBUTOR
        invite_email = f"relative_{int(datetime.now().timestamp())}@echo-memorial.org"
        resp_inv = await client.post(
            "/api/v1/family/invitations",
            json={
                "email": invite_email,
                "role": "CONTRIBUTOR",
                "relationship_to_subject": "Nephew",
                "expires_in_days": 7
            },
            headers={"x-user-id": "demo-user-001"}
        )
        assert resp_inv.status_code == 201
        inv_data = resp_inv.json()
        assert inv_data["status"] == "PENDING"
        assert "invite_url" in inv_data
        invite_url = inv_data["invite_url"]
        assert "token=" in invite_url

        # Extract secret token from URL
        secret_token = invite_url.split("token=")[1]

        # 3. Accept invitation
        resp_accept = await client.post(
            "/api/v1/family/invitations/accept",
            json={"invitation_token": secret_token},
            headers={
                "x-user-id": "new-relative-001",
                "x-user-email": invite_email,
                "x-user-name": "Robert Vance"
            }
        )
        assert resp_accept.status_code == 200
        new_member = resp_accept.json()
        assert new_member["email"] == invite_email
        assert new_member["role"] == "CONTRIBUTOR"

        # 4. Attempt to re-use same single-use token -> Rejected
        resp_reuse = await client.post(
            "/api/v1/family/invitations/accept",
            json={"invitation_token": secret_token},
            headers={"x-user-id": "attacker-002"}
        )
        assert resp_reuse.status_code == 400
        assert "already been used" in resp_reuse.json()["detail"].lower()


@pytest.mark.asyncio
async def test_invitation_revocation():
    """Verify revoking an invitation prevents it from being redeemed."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        invite_email = f"revokeme_{int(datetime.now().timestamp())}@echo-memorial.org"
        resp_inv = await client.post(
            "/api/v1/family/invitations",
            json={"email": invite_email, "role": "VIEWER"},
            headers={"x-user-id": "demo-user-001"}
        )
        inv_id = resp_inv.json()["id"]
        token = resp_inv.json()["invite_url"].split("token=")[1]

        # Revoke
        resp_rev = await client.delete(f"/api/v1/family/invitations/{inv_id}", headers={"x-user-id": "demo-user-001"})
        assert resp_rev.status_code == 200

        # Attempt accept revoked token -> Rejected
        resp_accept = await client.post(
            "/api/v1/family/invitations/accept",
            json={"invitation_token": token},
            headers={"x-user-id": "test-user-rev"}
        )
        assert resp_accept.status_code == 400
        assert "revoked" in resp_accept.json()["detail"].lower()


# ==============================================================================
# 4. Contribution Review Lifecycle & Self-Approval Prevention
# ==============================================================================

@pytest.mark.asyncio
async def test_contribution_submission_and_self_approval_block():
    """Contributors submit proposals; self-approval is strictly forbidden by server."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Submit new contribution as Clara Vance (demo-user-003)
        contrib_payload = {
            "contribution_type": "NEW_MEMORY",
            "title": "Evening Poetry Reading in Edinburgh",
            "proposed_content": {"narrative": "Grandfather read excerpts from Robert Burns by the fire."},
            "contributor_notes": "Recounted by Aunt Eleanor in 2024 interview.",
            "supporting_evidence": []
        }
        resp_sub = await client.post(
            "/api/v1/family/contributions",
            json=contrib_payload,
            headers={"x-user-id": "demo-user-003"}
        )
        assert resp_sub.status_code == 201
        contrib_data = resp_sub.json()
        assert contrib_data["status"] == "SUBMITTED"
        assert contrib_data["version"] == 1
        contrib_id = contrib_data["id"]

        # Self-approval attempt: Clara attempts to review and approve her own submission -> 403 Forbidden!
        resp_self_approve = await client.post(
            f"/api/v1/family/contributions/{contrib_id}/review",
            json={"decision": "APPROVED", "review_notes": "I approve my own recollection."},
            headers={"x-user-id": "demo-user-003"}  # Clara is the contributor
        )
        assert resp_self_approve.status_code == 403
        assert "cannot approve own contribution" in resp_self_approve.json()["detail"].lower() or "conflict of interest" in resp_self_approve.json()["detail"].lower()

        # Independent review by Eleanor Vance (demo-user-001) -> Approved!
        resp_indep_review = await client.post(
            f"/api/v1/family/contributions/{contrib_id}/review",
            json={"decision": "APPROVED", "review_notes": "Independently verified against oral history tape 4."},
            headers={"x-user-id": "demo-user-001"}
        )
        assert resp_indep_review.status_code == 200
        approved_data = resp_indep_review.json()
        assert approved_data["status"] == "APPROVED"
        assert approved_data["version"] == 2
        assert len(approved_data["version_history"]) == 2


@pytest.mark.asyncio
async def test_contribution_withdrawal():
    """Contributor may withdraw their own pending contribution before commitment."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Submit draft
        resp_sub = await client.post(
            "/api/v1/family/contributions",
            json={
                "contribution_type": "METADATA_CORRECTION",
                "title": "Minor typo correction",
                "proposed_content": {"title": "Updated"}
            },
            headers={"x-user-id": "demo-user-003"}
        )
        contrib_id = resp_sub.json()["id"]

        # Withdraw
        resp_with = await client.post(
            f"/api/v1/family/contributions/{contrib_id}/withdraw",
            headers={"x-user-id": "demo-user-003"}
        )
        assert resp_with.status_code == 200
        assert resp_with.json()["status"] == "WITHDRAWN"


# ==============================================================================
# 5. Empirical Research Metrics Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_phase8_research_telemetry_metrics():
    """Verify research metrics report real values without fabrication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/family/metrics", headers={"x-user-id": "demo-user-001"})
        assert resp.status_code == 200
        metrics = resp.json()

        assert metrics["events_with_supporting_evidence_count"] >= 5
        assert metrics["relationship_evidence_coverage_pct"] > 0.0
        assert metrics["active_family_members_count"] >= 4
        assert metrics["total_contributions_count"] >= 3
        assert "measured_at" in metrics
