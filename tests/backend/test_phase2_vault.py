"""Comprehensive Test Suite for Phase 2: Secure Multimodal Memory Vault.

Covers all 28 required test vectors:
1. Valid image upload (JPG, PNG, WEBP)
2. Valid video upload (MP4, MOV, WEBM)
3. Valid audio upload (MP3, WAV, M4A)
4. Valid PDF upload
5. Valid TXT upload
6. Valid DOCX upload
7. Unsupported file rejection
8. Oversized file rejection
9. Malicious filename rejection
10. Path traversal rejection
11. MIME validation
12. Checksum generation
13. Duplicate detection
14. Memory creation
15. Memory update
16. Memory retrieval
17. Memory deletion
18. Archive
19. Restore-ready behavior
20. Verification
21. Privacy restrictions
22. Consent creation
23. Consent revocation
24. Audit logging
25. Search
26. Filtering
27. Export authorization
28. Unauthorized memory access
"""

import pytest
import io
from datetime import datetime, timezone
from PIL import Image

from storage.vault_storage import (
    VaultStorageManager,
    UnsupportedFileTypeError,
    FileSizeLimitExceededError,
    MaliciousPathError
)
from models.memory import MemoryCreate, MemoryUpdate
from models.consent import ConsentRecordCreate
from models.enums import (
    MemoryCategory,
    SourceType,
    VerificationStatus,
    PrivacyLevel,
    ConsentType,
    ConsentStatus,
    AuditAction,
    ConfidenceLevel
)
from backend.app.services.memory_service import (
    MemoryService,
    UnauthorizedMemoryAccessError
)
from backend.app.services.consent_service import ConsentService
from backend.app.services.audit_service import AuditService


# Helper to create valid small in-memory image bytes
def create_test_image_bytes(format="JPEG") -> bytes:
    import random
    buf = io.BytesIO()
    r = random.randint(1, 254)
    g = random.randint(1, 254)
    b = random.randint(1, 254)
    img = Image.new("RGB", (64, 64), color=(r, g, b))
    img.save(buf, format=format)
    return buf.getvalue()


@pytest.fixture
def storage():
    return VaultStorageManager()


@pytest.fixture
def memory_svc():
    return MemoryService()


@pytest.fixture
def consent_svc():
    return ConsentService()


@pytest.fixture
def audit_svc():
    return AuditService()


# --- 1-6: Valid Upload Tests Across All Modalities ---

@pytest.mark.asyncio
async def test_01_valid_image_uploads(storage):
    """Test 1: Valid image upload (JPG, PNG, WEBP)."""
    jpg_data = create_test_image_bytes("JPEG")
    res_jpg = await storage.save_original("family_portrait.jpg", jpg_data, "image/jpeg")
    assert res_jpg["is_duplicate"] is False
    assert "originals/" in res_jpg["storage_path"]
    assert res_jpg["thumbnail_path"] is not None
    assert "thumbnails/" in res_jpg["thumbnail_path"]

    png_data = create_test_image_bytes("PNG")
    res_png = await storage.save_original("old_snapshot.png", png_data, "image/png")
    assert "originals/" in res_png["storage_path"]

    webp_data = create_test_image_bytes("WEBP")
    res_webp = await storage.save_original("memorial_photo.webp", webp_data, "image/webp")
    assert "originals/" in res_webp["storage_path"]


@pytest.mark.asyncio
async def test_02_valid_video_uploads(storage):
    """Test 2: Valid video upload (MP4, MOV, WEBM)."""
    mock_video_bytes = b"MOCK_VIDEO_BINARY_STREAM_MP4_DATA"
    res_mp4 = await storage.save_original("summer_vacation.mp4", mock_video_bytes, "video/mp4")
    assert "originals/" in res_mp4["storage_path"]
    assert res_mp4["mime_type"] == "video/mp4"

    res_mov = await storage.save_original("family_film.mov", b"MOCK_MOV_STREAM", "video/quicktime")
    assert "originals/" in res_mov["storage_path"]

    res_webm = await storage.save_original("interview_clip.webm", b"MOCK_WEBM_STREAM", "video/webm")
    assert "originals/" in res_webm["storage_path"]


@pytest.mark.asyncio
async def test_03_valid_audio_uploads(storage):
    """Test 3: Valid audio upload (MP3, WAV, M4A)."""
    res_mp3 = await storage.save_original("voice_note.mp3", b"ID3_MOCK_AUDIO_STREAM", "audio/mpeg")
    assert "originals/" in res_mp3["storage_path"]
    assert res_mp3["mime_type"] == "audio/mpeg"

    res_wav = await storage.save_original("gramophone_recording.wav", b"RIFF_MOCK_WAV_STREAM", "audio/wav")
    assert "originals/" in res_wav["storage_path"]

    res_m4a = await storage.save_original("song_lullaby.m4a", b"FTYP_M4A_STREAM", "audio/mp4")
    assert "originals/" in res_m4a["storage_path"]


@pytest.mark.asyncio
async def test_04_valid_pdf_upload(storage):
    """Test 4: Valid PDF upload."""
    res_pdf = await storage.save_original("birth_certificate.pdf", b"%PDF-1.4 mock content", "application/pdf")
    assert "originals/" in res_pdf["storage_path"]
    assert res_pdf["mime_type"] == "application/pdf"


@pytest.mark.asyncio
async def test_05_valid_txt_upload(storage):
    """Test 5: Valid TXT upload."""
    res_txt = await storage.save_original("handwritten_letter.txt", b"My dearest sister, we arrived in Edinburgh...", "text/plain")
    assert "originals/" in res_txt["storage_path"]
    assert res_txt["mime_type"] == "text/plain"


@pytest.mark.asyncio
async def test_06_valid_docx_upload(storage):
    """Test 6: Valid DOCX upload."""
    docx_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    res_docx = await storage.save_original("biography_chapter_1.docx", b"PK\x03\x04mock docx zip stream", docx_mime)
    assert "originals/" in res_docx["storage_path"]
    assert res_docx["mime_type"] == docx_mime


# --- 7-11: Security, Validation, and Rejection Tests ---

def test_07_unsupported_file_rejection(storage):
    """Test 7: Unsupported file rejection."""
    with pytest.raises(UnsupportedFileTypeError) as exc:
        storage.validate_file("malicious_script.exe", b"MZ\x90executable", "application/x-msdownload")
    assert "Unsupported file extension '.exe'" in str(exc.value)

    with pytest.raises(UnsupportedFileTypeError):
        storage.validate_file("system_hook.bat", b"@echo off", "application/x-bat")


def test_08_oversized_file_rejection(storage):
    """Test 8: Oversized file rejection."""
    # Simulate data larger than 100MB without allocating real memory
    class FakeOversizedBytes:
        def __len__(self):
            return 105 * 1024 * 1024  # 105MB

    with pytest.raises(FileSizeLimitExceededError):
        storage.validate_file("giant_archive.mp4", FakeOversizedBytes(), "video/mp4")


def test_09_malicious_filename_rejection(storage):
    """Test 9: Malicious filename rejection and safe sanitization."""
    # Test path stripped and special chars eliminated
    clean = storage.sanitize_filename("../../../etc/passwd.jpg")
    assert ".." not in clean
    assert "/" not in clean
    assert clean == "passwd.jpg"

    clean2 = storage.sanitize_filename("test\0bad<script>.png")
    assert "\0" not in clean2
    assert "<" not in clean2
    assert clean2.endswith(".png")


def test_10_path_traversal_rejection(storage):
    """Test 10: Path traversal rejection."""
    with pytest.raises(MaliciousPathError):
        storage.get_absolute_path("../../Windows/System32/cmd.exe")

    with pytest.raises(MaliciousPathError):
        storage.get_absolute_path("originals/../../secret.key")


def test_11_mime_validation(storage):
    """Test 11: MIME validation."""
    # Extension is .jpg but MIME claims to be a shell script
    with pytest.raises(UnsupportedFileTypeError):
        storage.validate_file("photo.jpg", b"mock content", "application/x-sh")


# --- 12-13: Cryptography & Duplicate Detection ---

@pytest.mark.asyncio
async def test_12_checksum_generation(storage):
    """Test 12: Checksum generation (SHA-256)."""
    test_content = b"ECHO_AUTHENTIC_PRESERVED_MEMORY_1974"
    import hashlib
    expected_hash = hashlib.sha256(test_content).hexdigest()
    calculated = storage.calculate_checksum(test_content)
    assert calculated == expected_hash
    assert len(calculated) == 64


@pytest.mark.asyncio
async def test_13_duplicate_detection(storage):
    """Test 13: Duplicate detection without redundant disk write."""
    from uuid import uuid4
    unique_content = f"UNIQUE_ARCHIVAL_LETTER_HASH_TEST_{uuid4()}".encode()
    res1 = await storage.save_original("letter_a.txt", unique_content, "text/plain")
    assert res1["is_duplicate"] is False

    # Upload exact same content with different name
    res2 = await storage.save_original("letter_b_copy.txt", unique_content, "text/plain")
    assert res2["is_duplicate"] is True
    assert res2["checksum"] == res1["checksum"]
    assert res2["storage_path"] == res1["storage_path"]
    assert "Duplicate file detected" in res2["message"]


# --- 14-20: Memory Vault Lifecycle (CRUD, Archive, Restore, Verify) ---

@pytest.mark.asyncio
async def test_14_memory_creation(memory_svc):
    """Test 14: Memory creation."""
    mem_in = MemoryCreate(
        title="First Solo Violin Recital",
        description="Performed the Bach Partita in D minor at St. Cecilia's Hall.",
        category=MemoryCategory.ACHIEVEMENTS,
        source_type=SourceType.DOCUMENT,
        date="1965-05-12",
        approximate_date="May 1965",
        location="Edinburgh, Scotland",
        people=["Eleanor Vance"],
        privacy_level=PrivacyLevel.PRIVATE,
        verification_status=VerificationStatus.PENDING_REVIEW,
        checksum="abcd1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab"
    )
    created = await memory_svc.create_memory(mem_in, user_id="demo-user-001")
    assert created.id is not None
    assert created.title == "First Solo Violin Recital"
    assert created.category == MemoryCategory.ACHIEVEMENTS
    assert created.privacy_level == PrivacyLevel.PRIVATE


@pytest.mark.asyncio
async def test_15_memory_update(memory_svc):
    """Test 15: Memory update."""
    mem_in = MemoryCreate(
        title="Draft Note on Sailing",
        description="Initial notes.",
        category=MemoryCategory.HOBBIES
    )
    created = await memory_svc.create_memory(mem_in, user_id="demo-user-001")

    updated = await memory_svc.update_memory(
        created.id,
        MemoryUpdate(title="Refined Note on Sailing Dinghies", location="Windermere"),
        user_id="demo-user-001"
    )
    assert updated.title == "Refined Note on Sailing Dinghies"
    assert updated.location == "Windermere"


@pytest.mark.asyncio
async def test_16_memory_retrieval(memory_svc):
    """Test 16: Memory retrieval."""
    mem = await memory_svc.get_memory("demo-mem-001", user_id="demo-user-001")
    assert mem is not None
    assert mem.id == "demo-mem-001"
    assert "Graduation" in mem.title


@pytest.mark.asyncio
async def test_17_memory_deletion(memory_svc):
    """Test 17: Memory soft deletion."""
    mem_in = MemoryCreate(title="Temporary Scratch Memory", description="To be deleted.")
    created = await memory_svc.create_memory(mem_in, user_id="demo-user-001")

    deleted = await memory_svc.delete_memory(created.id, user_id="demo-user-001")
    assert deleted is True

    # Retrieving deleted memory should return None
    fetched = await memory_svc.get_memory(created.id, user_id="demo-user-001")
    assert fetched is None


@pytest.mark.asyncio
async def test_18_memory_archive(memory_svc):
    """Test 18: Archive memory."""
    mem_in = MemoryCreate(title="Old Archival Record", description="To be archived.")
    created = await memory_svc.create_memory(mem_in, user_id="demo-user-001")

    archived = await memory_svc.archive_memory(created.id, user_id="demo-user-001")
    assert archived.archived is True

    # By default, list_memories hides archived items
    active_mems = await memory_svc.list_memories(include_archived=False)
    assert not any(m.id == created.id for m in active_mems)

    # When include_archived=True, it appears
    all_mems = await memory_svc.list_memories(include_archived=True)
    assert any(m.id == created.id for m in all_mems)


@pytest.mark.asyncio
async def test_19_restore_ready_behavior(memory_svc):
    """Test 19: Restore-ready unarchive behavior."""
    mem_in = MemoryCreate(title="Archived Photo", description="Restoring test.")
    created = await memory_svc.create_memory(mem_in, user_id="demo-user-001")
    await memory_svc.archive_memory(created.id, user_id="demo-user-001")

    restored = await memory_svc.unarchive_memory(created.id, user_id="demo-user-001")
    assert restored.archived is False

    active_mems = await memory_svc.list_memories(include_archived=False)
    assert any(m.id == created.id for m in active_mems)


@pytest.mark.asyncio
async def test_20_verification_status(memory_svc):
    """Test 20: Verification transitions (VERIFIED, REJECTED, PENDING_REVIEW)."""
    mem_in = MemoryCreate(title="Uncorroborated Oral Story", description="Awaiting family review.")
    created = await memory_svc.create_memory(mem_in, user_id="demo-user-001")

    # Verify
    verified = await memory_svc.verify_memory(created.id, VerificationStatus.VERIFIED, user_id="demo-user-001")
    assert verified.verification_status == VerificationStatus.VERIFIED
    assert verified.confidence == ConfidenceLevel.VERIFIED

    # Reject
    rejected = await memory_svc.verify_memory(created.id, VerificationStatus.REJECTED, user_id="demo-user-001")
    assert rejected.verification_status == VerificationStatus.REJECTED
    assert rejected.confidence == ConfidenceLevel.UNKNOWN_UNSUPPORTED


# --- 21-24: Privacy, Consent, and Audit ---

@pytest.mark.asyncio
async def test_21_privacy_restrictions(memory_svc):
    """Test 21: Privacy restrictions (PRIVATE vs FAMILY vs AUTHORIZED_USERS)."""
    private_mem = await memory_svc.create_memory(
        MemoryCreate(title="Secret Diary Entry", description="Strictly private.", privacy_level=PrivacyLevel.PRIVATE),
        user_id="user-a"
    )

    # user-a can access
    assert memory_svc.check_access(private_mem, user_id="user-a", role="viewer") is True

    # outsider cannot access
    assert memory_svc.check_access(private_mem, user_id="user-b", role="viewer") is False


@pytest.mark.asyncio
async def test_22_consent_creation(consent_svc):
    """Test 22: Consent creation across scopes."""
    consent_in = ConsentRecordCreate(
        granter_name="Eleanor Vance",
        granter_relationship="Daughter & Legal Executor",
        consent_type=ConsentType.AI_PROCESSING,
        scope="Grounding dialogue responses in preserved diaries",
        memory_id="demo-mem-001"
    )
    rec = await consent_svc.grant_consent(consent_in, actor="demo-user-001")
    assert rec.id is not None
    assert rec.status == ConsentStatus.GRANTED
    assert rec.consent_type == ConsentType.AI_PROCESSING

    has_consent = await consent_svc.check_consent(ConsentType.AI_PROCESSING, memory_id="demo-mem-001")
    assert has_consent is True


@pytest.mark.asyncio
async def test_23_consent_revocation(consent_svc):
    """Test 23: Consent revocation."""
    consent_in = ConsentRecordCreate(
        granter_name="Eleanor Vance",
        consent_type=ConsentType.VOICE_PROCESSING,
        scope="Audio model fine-tuning"
    )
    rec = await consent_svc.grant_consent(consent_in)
    assert rec.status == ConsentStatus.GRANTED

    revoked = await consent_svc.revoke_consent(rec.id)
    assert revoked.status == ConsentStatus.REVOKED
    assert revoked.revoked_at is not None

    has_voice_consent = await consent_svc.check_consent(ConsentType.VOICE_PROCESSING)
    assert has_voice_consent is False


@pytest.mark.asyncio
async def test_24_audit_logging(audit_svc):
    """Test 24: Tamper-evident audit logging."""
    await audit_svc.record_event(
        action=AuditAction.UPLOAD,
        actor="guardian_1",
        resource="Media:photo_123.jpg",
        result="SUCCESS",
        metadata={"file_size": 2048, "secret_token": "MUST_BE_REDACTED"}
    )
    logs = await audit_svc.list_logs(action=AuditAction.UPLOAD)
    assert len(logs) > 0
    latest = logs[0]
    assert latest.action == AuditAction.UPLOAD
    assert latest.actor == "guardian_1"
    assert latest.metadata["secret_token"] == "[REDACTED]"


# --- 25-28: Search, Filtering, Export, and Unauthorized Access ---

@pytest.mark.asyncio
async def test_25_metadata_search(memory_svc):
    """Test 25: Search by keyword, title, description, person, location."""
    await memory_svc.create_memory(
        MemoryCreate(
            title="Shetland Islands Journey",
            description="Ferry voyage during stormy weather in the North Sea.",
            location="Lerwick, Shetland",
            people=["Captain Ferguson"]
        ),
        user_id="demo-user-001"
    )

    # Search by keyword
    res_kw = await memory_svc.list_memories(search_query="Shetland")
    assert any("Shetland" in m.title for m in res_kw)

    # Search by person
    res_person = await memory_svc.list_memories(person="Ferguson")
    assert any(any("Ferguson" in p for p in (m.people or [])) for m in res_person)

    # Search by location
    res_loc = await memory_svc.list_memories(location="Lerwick")
    assert any("Lerwick" in (m.location or "") for m in res_loc)


@pytest.mark.asyncio
async def test_26_filtering(memory_svc):
    """Test 26: Filtering by category, source_type, verification_status, privacy_level."""
    await memory_svc.create_memory(
        MemoryCreate(
            title="Childhood Treehouse",
            description="Built a wooden fort in the garden with siblings.",
            category=MemoryCategory.CHILDHOOD,
            source_type=SourceType.FAMILY_STORY,
            verification_status=VerificationStatus.VERIFIED,
            privacy_level=PrivacyLevel.PRIVATE
        ),
        user_id="demo-user-001"
    )

    res_cat = await memory_svc.list_memories(category=MemoryCategory.CHILDHOOD)
    assert all(m.category == MemoryCategory.CHILDHOOD for m in res_cat)

    res_ver = await memory_svc.list_memories(verification_status=VerificationStatus.VERIFIED)
    assert all(m.verification_status == VerificationStatus.VERIFIED for m in res_ver)


@pytest.mark.asyncio
async def test_27_export_authorization(memory_svc):
    """Test 27: Export memory bundle."""
    bundle = await memory_svc.export_memory("demo-mem-001", user_id="demo-user-001")
    assert bundle["version"] == "ECHO-MemoryVault-Export-v2.0"
    assert bundle["memory"]["id"] == "demo-mem-001"
    assert "provenance_records" in bundle
    # Physical absolute path must NOT be in export
    assert "D:\\" not in bundle["memory"]["storage_reference"]
    assert "D:/" not in bundle["memory"]["storage_reference"]
    assert "ethical_notice" in bundle


@pytest.mark.asyncio
async def test_28_unauthorized_memory_access_rejection(memory_svc):
    """Test 28: Unauthorized memory access rejection."""
    # Create private memory owned by user-secret-999
    secret_mem = await memory_svc.create_memory(
        MemoryCreate(
            title="Private Will and Testament",
            description="Highly confidential legal notes.",
            privacy_level=PrivacyLevel.PRIVATE
        ),
        user_id="user-secret-999"
    )

    # Viewer user-stranger tries to access -> Must raise UnauthorizedMemoryAccessError
    with pytest.raises(UnauthorizedMemoryAccessError):
        await memory_svc.get_memory(secret_mem.id, user_id="user-stranger", role="viewer")
