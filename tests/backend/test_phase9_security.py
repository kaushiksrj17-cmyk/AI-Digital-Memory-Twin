"""Phase 9 Security Hardening and Access Control Test Suite for ECHO.

Validates:
1. Authentication, JWT token lifecycle, hashing, and signature validation
2. Role-Based Access Control (RBAC) permissions matrix and role enforcement
3. Privacy boundaries (PRIVATE, FAMILY, AUTHORIZED_USERS, PUBLIC)
4. Secure file upload validation, extension whitelisting, and path traversal prevention
5. Secrets redaction in audit logs and API responses
6. Security status, roles, access-check, and audit summary endpoints
"""

import pytest
from httpx import AsyncClient, ASGITransport
import os
from pathlib import Path

from backend.app.main import app
from backend.app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    has_permission,
    can_access_privacy_level,
    UserRole,
    Permission,
    ROLE_PERMISSIONS
)
from storage.vault_storage import (
    vault_storage,
    UnsupportedFileTypeError,
    FileSizeLimitExceededError,
    MaliciousPathError
)
from backend.app.services.audit_service import audit_service
from models.enums import PrivacyLevel, AuditAction


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_password_hashing_and_verification():
    """Verify bcrypt password hashing and verification."""
    password = "SecretMemorialPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


@pytest.mark.asyncio
async def test_access_token_creation_and_decoding():
    """Verify JWT access token creation, claims encoding, and decoding."""
    payload = {
        "sub": "guardian@echo-memorial.org",
        "role": UserRole.GUARDIAN.value,
        "user_id": "usr-001"
    }
    token = create_access_token(payload)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "guardian@echo-memorial.org"
    assert decoded["role"] == UserRole.GUARDIAN.value
    assert decoded["user_id"] == "usr-001"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_invalid_token_decoding():
    """Verify that forged, malformed, or tampered tokens return None."""
    assert decode_access_token("not.a.valid.jwt.token") is None
    assert decode_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.badpayload.badsig") is None


@pytest.mark.asyncio
async def test_rbac_role_permissions():
    """Verify RBAC permissions matrix across all user roles."""
    # Vault owner has full permissions
    assert has_permission(UserRole.VAULT_OWNER.value, Permission.READ_PRIVATE) is True
    assert has_permission(UserRole.VAULT_OWNER.value, Permission.DELETE_MEMORY) is True
    assert has_permission(UserRole.VAULT_OWNER.value, Permission.MANAGE_CONSENT) is True
    assert has_permission(UserRole.VAULT_OWNER.value, Permission.ADMIN) is True

    # Guardian has custody permissions but not arbitrary admin
    assert has_permission(UserRole.GUARDIAN.value, Permission.READ_PRIVATE) is True
    assert has_permission(UserRole.GUARDIAN.value, Permission.MANAGE_CONSENT) is True

    # Family member can read family & public, but not private vault
    assert has_permission(UserRole.FAMILY_MEMBER.value, Permission.READ_FAMILY) is True
    assert has_permission(UserRole.FAMILY_MEMBER.value, Permission.READ_PRIVATE) is False
    assert has_permission(UserRole.FAMILY_MEMBER.value, Permission.DELETE_MEMORY) is False

    # Researcher can view public & research metrics, run evaluations, but cannot delete or edit
    assert has_permission(UserRole.RESEARCHER.value, Permission.VIEW_RESEARCH) is True
    assert has_permission(UserRole.RESEARCHER.value, Permission.RUN_EVALUATION) is True
    assert has_permission(UserRole.RESEARCHER.value, Permission.READ_PRIVATE) is False
    assert has_permission(UserRole.RESEARCHER.value, Permission.WRITE_MEMORY) is False

    # Visitor can only read public
    assert has_permission(UserRole.VISITOR.value, Permission.READ_PUBLIC) is True
    assert has_permission(UserRole.VISITOR.value, Permission.READ_FAMILY) is False
    assert has_permission(UserRole.VISITOR.value, Permission.WRITE_MEMORY) is False


@pytest.mark.asyncio
async def test_privacy_boundary_clearance():
    """Verify privacy boundaries prevent unauthorized role access."""
    # PRIVATE boundary
    assert can_access_privacy_level(UserRole.VAULT_OWNER.value, PrivacyLevel.PRIVATE) is True
    assert can_access_privacy_level(UserRole.GUARDIAN.value, PrivacyLevel.PRIVATE) is True
    assert can_access_privacy_level(UserRole.FAMILY_MEMBER.value, PrivacyLevel.PRIVATE) is False
    assert can_access_privacy_level(UserRole.RESEARCHER.value, PrivacyLevel.PRIVATE) is False
    assert can_access_privacy_level(UserRole.VISITOR.value, PrivacyLevel.PRIVATE) is False

    # FAMILY boundary
    assert can_access_privacy_level(UserRole.VAULT_OWNER.value, PrivacyLevel.FAMILY) is True
    assert can_access_privacy_level(UserRole.GUARDIAN.value, PrivacyLevel.FAMILY) is True
    assert can_access_privacy_level(UserRole.FAMILY_MEMBER.value, PrivacyLevel.FAMILY) is True
    assert can_access_privacy_level(UserRole.RESEARCHER.value, PrivacyLevel.FAMILY) is False
    assert can_access_privacy_level(UserRole.VISITOR.value, PrivacyLevel.FAMILY) is False

    # AUTHORIZED_USERS boundary
    assert can_access_privacy_level(UserRole.RESEARCHER.value, "AUTHORIZED_USERS") is True
    assert can_access_privacy_level(UserRole.VISITOR.value, "AUTHORIZED_USERS") is False

    # MEMORIAL_PUBLIC boundary
    assert can_access_privacy_level(UserRole.VISITOR.value, "MEMORIAL_PUBLIC") is True


@pytest.mark.asyncio
async def test_secure_file_upload_whitelist_and_sanitization():
    """Verify file upload rejection of executable/dangerous extensions and path traversal."""
    # Disallowed dangerous extension
    with pytest.raises(UnsupportedFileTypeError):
        await vault_storage.save_original(
            original_filename="malicious_payload.exe",
            content=b"MZ\x90\x00\x03\x00\x00\x00",
            mime_type="application/x-msdownload"
        )

    # Path traversal attack detection
    with pytest.raises(MaliciousPathError):
        vault_storage.get_absolute_path("../../../../../windows/system32/cmd.exe")

    with pytest.raises(MaliciousPathError):
        await vault_storage.save_file("../../escape.txt", b"hack")

    # Valid image upload succeeds within D:\ECHO\storage
    result = await vault_storage.save_original(
        original_filename="security_test_photo.jpg",
        content=b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 200,
        mime_type="image/jpeg"
    )
    assert result["checksum"] is not None
    assert "originals/" in result["storage_path"]
    assert "D:" not in result["storage_path"]  # Safe relative path only


@pytest.mark.asyncio
async def test_secrets_redaction_in_audit_logs():
    """Verify passwords, authorization tokens, and API secrets are never logged."""
    dirty_meta = {
        "user_email": "guardian@echo-memorial.org",
        "password": "SuperSecretPassword123!",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "api_key": "sk-proj-super-secret-key",
        "normal_field": "1968 graduation folio"
    }

    log = await audit_service.record_event(
        action=AuditAction.VIEW,
        actor="test-actor",
        resource="Vault:SecretCheck",
        metadata=dirty_meta
    )

    clean = log.metadata
    assert clean["password"] == "[REDACTED]"
    assert clean["access_token"] == "[REDACTED]"
    assert clean["api_key"] == "[REDACTED]"
    assert clean["normal_field"] == "1968 graduation folio"
    assert clean["user_email"] == "guardian@echo-memorial.org"


@pytest.mark.asyncio
async def test_security_api_endpoints():
    """Test security endpoints for posture status, roles, access-check, and audit summary."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # GET /api/v1/security/status
        res = await ac.get("/api/v1/security/status")
        assert res.status_code == 200
        data = res.json()
        assert data["is_local_isolated"] is True
        assert data["zero_cloud_leakage"] is True
        assert data["rbac_active"] is True
        assert "vault_owner" in data["supported_roles"]

        # GET /api/v1/security/roles
        res_roles = await ac.get("/api/v1/security/roles")
        assert res_roles.status_code == 200
        roles_data = res_roles.json()
        assert "vault_owner" in roles_data["roles"]
        assert "researcher" in roles_data["roles"]

        # POST /api/v1/security/check-access
        # Vault owner -> PRIVATE: allowed
        res_check1 = await ac.post("/api/v1/security/check-access", json={
            "role": "vault_owner",
            "privacy_level": "PRIVATE"
        })
        assert res_check1.status_code == 200
        assert res_check1.json()["allowed"] is True

        # Family member -> PRIVATE: denied
        res_check2 = await ac.post("/api/v1/security/check-access", json={
            "role": "family_member",
            "privacy_level": "PRIVATE"
        })
        assert res_check2.status_code == 200
        assert res_check2.json()["allowed"] is False

        # GET /api/v1/security/audit-summary
        res_audit = await ac.get("/api/v1/security/audit-summary")
        assert res_audit.status_code == 200
        assert "total_audit_events" in res_audit.json()


@pytest.mark.asyncio
async def test_auth_login_with_roles_and_token_verification():
    """Test auth login with role assignment and token verification."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Login as researcher
        res = await ac.post("/api/v1/auth/login", json={
            "email": "dr.vance.researcher@cambridge.ac.uk",
            "password": "ValidPassword123!"
        })
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body
        token = body["access_token"]
        assert body["user"]["role"] == UserRole.RESEARCHER.value

        # Verify token
        res_v = await ac.post("/api/v1/auth/verify", json={"token": token})
        assert res_v.status_code == 200
        assert res_v.json()["valid"] is True
        assert res_v.json()["claims"]["role"] == UserRole.RESEARCHER.value

        # Call /me with token
        res_me = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 200
        assert res_me.json()["role"] == UserRole.RESEARCHER.value
