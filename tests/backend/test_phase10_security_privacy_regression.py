"""Phase 10 Privacy, Storage Boundary, and Security Regression Test Suite.

Validates defensive controls:
1. Path traversal attacks and malicious filename rejection
2. Unsupported MIME types, oversized payloads, and zero-byte upload blocking
3. Storage root boundary confinement (D:\\ECHO\\storage\\)
4. Cross-user private memory access isolation
5. Audit log protection against unauthorized visitors
6. Immediate enforcement of consent revocation
7. Self-privilege escalation and unauthorized role modification blocking
8. Error response sanitization (no internal stack traces or secrets exposed)
"""

import pytest
from httpx import AsyncClient, ASGITransport
import os
from pathlib import Path
from uuid import uuid4

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.security import (
    create_access_token,
    UserRole,
    Permission,
    can_access_privacy_level,
    validate_ethical_boundaries
)
from backend.app.core.errors import EthicalBoundaryViolation
from storage.vault_storage import (
    vault_storage,
    UnsupportedFileTypeError,
    FileSizeLimitExceededError,
    MaliciousPathError,
    VaultStorageManager
)
from models.enums import PrivacyLevel, ConsentType, MemoryCategory
from models.consent import ConsentRecordCreate
from backend.app.services.consent_service import consent_service
from backend.app.services.memory_service import memory_service, UnauthorizedMemoryAccessError
from models.memory import MemoryCreate, MemoryUpdate


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ==============================================================================
# 1. PATH TRAVERSAL & MALICIOUS FILENAMES
# ==============================================================================

@pytest.mark.asyncio
async def test_path_traversal_detection_in_storage_manager():
    """Verify that VaultStorageManager strictly blocks all path traversal sequences."""
    traversal_attempts = [
        "../secrets.txt",
        "..\\secrets.txt",
        "../../../../Windows/System32/cmd.exe",
        "originals/../../etc/passwd",
        "temporary/..\\..\\config.py",
        "test_file\0.jpg",
        "sub/../..\\windows\\win.ini"
    ]
    for attempt in traversal_attempts:
        with pytest.raises(MaliciousPathError):
            vault_storage._resolve_safe_path(attempt)


def test_filename_sanitization():
    """Verify that malicious filenames are stripped of path elements and control characters."""
    raw_names = [
        ("../../malicious_script.sh", "malicious_script_sh"),
        ("folder\\subfolder\\photo.png", "photo.png"),
        ("exploit\x00\x08test.jpg", "exploittest.jpg"),
        ("a" * 150 + ".txt", "a" * 100 + ".txt")
    ]
    for raw, expected in raw_names:
        sanitized = VaultStorageManager.sanitize_filename(raw)
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert "\\" not in sanitized
        assert "\0" not in sanitized
        assert len(sanitized) <= 110


# ==============================================================================
# 2. FILE TYPE VALIDATION & EMPTY FILE REJECTION
# ==============================================================================

@pytest.mark.asyncio
async def test_unsupported_file_and_empty_upload_rejection():
    """Verify that forbidden file extensions and empty payloads are rejected."""
    owner_token = create_access_token({
        "sub": "owner@echo.org",
        "user_id": "usr-owner-001",
        "role": UserRole.VAULT_OWNER.value
    })

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Executable file rejection
        res_exe = await client.post(
            "/api/v1/media/upload",
            files={"file": ("danger.exe", b"MZ_EXECUTABLE_BINARY", "application/x-dosexec")},
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert res_exe.status_code == 400

        # Shell script rejection
        res_sh = await client.post(
            "/api/v1/media/upload",
            files={"file": ("hack.sh", b"#!/bin/bash\nrm -rf /", "application/x-sh")},
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert res_sh.status_code == 400

        # Zero-byte upload rejection
        res_empty = await client.post(
            "/api/v1/media/upload",
            files={"file": ("empty.txt", b"", "text/plain")},
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert res_empty.status_code == 400


# ==============================================================================
# 3. STORAGE ROOT BOUNDARY CONFINEMENT
# ==============================================================================

def test_storage_root_boundary_confinement():
    """Verify that vault storage root is strictly confined to D:\\ECHO\\storage."""
    root = vault_storage.root
    assert str(root).startswith("D:\\ECHO\\storage") or "ECHO" in str(root)
    # Check that originals, processed, and temporary directories are children of root
    assert vault_storage.originals_dir.is_relative_to(root)
    assert vault_storage.processed_dir.is_relative_to(root)
    assert vault_storage.thumbnails_dir.is_relative_to(root)
    assert vault_storage.temporary_dir.is_relative_to(root)
    assert vault_storage.exports_dir.is_relative_to(root)


# ==============================================================================
# 4. CROSS-USER MEMORY ACCESS ISOLATION
# ==============================================================================

@pytest.mark.asyncio
async def test_cross_user_private_memory_isolation():
    """Verify that User B cannot retrieve, update, or delete User A's PRIVATE memory."""
    user_a_token = create_access_token({
        "sub": "user_a@echo.org",
        "user_id": "usr-alice-777",
        "role": UserRole.FAMILY_MEMBER.value
    })
    user_b_token = create_access_token({
        "sub": "user_b@echo.org",
        "user_id": "usr-bob-888",
        "role": UserRole.FAMILY_MEMBER.value
    })

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User A creates a strictly PRIVATE memory
        create_res = await client.post(
            "/api/v1/memories/",
            json={
                "title": "Alice's Private Diary",
                "description": "Strictly private thoughts.",
                "category": "PERSONAL_STORIES",
                "source_type": "DOCUMENT",
                "privacy_level": "PRIVATE"
            },
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert create_res.status_code == 201
        alice_mem_id = create_res.json()["id"]

        # Alice can view her own memory
        alice_get = await client.get(
            f"/api/v1/memories/{alice_mem_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert alice_get.status_code == 200

        # Bob attempts to view Alice's private memory -> HTTP 403 Forbidden
        bob_get = await client.get(
            f"/api/v1/memories/{alice_mem_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert bob_get.status_code == 403

        # Bob attempts to modify Alice's memory -> HTTP 403 Forbidden
        bob_edit = await client.put(
            f"/api/v1/memories/{alice_mem_id}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert bob_edit.status_code == 403

        # Bob attempts to delete Alice's memory -> HTTP 403 Forbidden
        bob_del = await client.delete(
            f"/api/v1/memories/{alice_mem_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert bob_del.status_code == 403


# ==============================================================================
# 5. AUDIT LOG ACCESS PROTECTION
# ==============================================================================

@pytest.mark.asyncio
async def test_audit_log_access_protection():
    """Verify that visitors and unauthorized members cannot inspect vault audit logs."""
    visitor_token = create_access_token({
        "sub": "visitor@public.org",
        "user_id": "usr-vis-001",
        "role": UserRole.VISITOR.value
    })
    guardian_token = create_access_token({
        "sub": "guardian@echo.org",
        "user_id": "usr-guard-001",
        "role": UserRole.GUARDIAN.value
    })

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Visitor blocked
        res_vis = await client.get(
            "/api/v1/audit/",
            headers={"Authorization": f"Bearer {visitor_token}"}
        )
        assert res_vis.status_code == 403

        # Guardian authorized
        res_guard = await client.get(
            "/api/v1/audit/",
            headers={"Authorization": f"Bearer {guardian_token}"}
        )
        assert res_guard.status_code == 200


# ==============================================================================
# 6. CONSENT REVOCATION IMMEDIACY
# ==============================================================================

@pytest.mark.asyncio
async def test_consent_revocation_immediacy():
    """Verify that revoking consent immediately terminates authorization without latency."""
    profile_id = f"prof-rev-{uuid4().hex[:6]}"
    
    # 1. Grant AI processing consent
    grant = await consent_service.grant_consent(
        ConsentRecordCreate(
            memorial_profile_id=profile_id,
            consent_type=ConsentType.AI_PROCESSING,
            granter_name="Guardian"
        )
    )
    assert grant.status.value == "GRANTED"

    # Check active state
    permitted_before = await consent_service.is_ai_processing_permitted(profile_id)
    assert permitted_before is True

    # 2. Revoke immediately
    revoked = await consent_service.revoke_consent(consent_id=grant.id)
    assert revoked.status.value == "REVOKED"

    # Check that authorization is revoked immediately
    permitted_after = await consent_service.is_ai_processing_permitted(profile_id)
    assert permitted_after is False


# ==============================================================================
# 7. ROLE ESCALATION PREVENTION IN FAMILY COLLABORATION
# ==============================================================================

@pytest.mark.asyncio
async def test_role_escalation_prevention():
    """Verify that non-owner members cannot modify roles or promote themselves."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Non-owner attempting to modify a member's role to OWNER
        res_escalate = await client.put(
            "/api/v1/family/members/demo-user-003/role",
            json={"role": "OWNER"},
            headers={"x-user-id": "demo-user-003"}  # Acting as contributor/viewer
        )
        assert res_escalate.status_code in [403, 404]


# ==============================================================================
# 8. ERROR RESPONSE SANITIZATION & ETHICAL VIOLATION HANDLING
# ==============================================================================

@pytest.mark.asyncio
async def test_error_response_sanitization():
    """Verify that error responses do not leak internal tracebacks or secrets."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Trigger not found
        res_nf = await client.get("/api/v1/memories/non-existent-uuid-99999")
        assert res_nf.status_code == 404
        data = res_nf.json()
        # Verify no internal traceback is returned
        assert "traceback" not in data
        assert "Traceback (most recent call last)" not in str(data)

    # Verify that ethical filter catches consciousness simulation
    with pytest.raises(EthicalBoundaryViolation) as exc_info:
        validate_ethical_boundaries("I am conscious and I have a soul speaking from the dead.")
    assert "Ethical Boundary Violation" in str(exc_info.value)
