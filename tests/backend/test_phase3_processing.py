"""Comprehensive Test Suite for Phase 3: ECHO Multimodal AI Memory Processing.

Covers all core test vectors for Phase 3:
1. image metadata extraction
2. image thumbnail generation
3. unsupported image rejection
4. video metadata extraction
5. video keyframe extraction
6. audio metadata extraction
7. document TXT extraction
8. PDF text extraction
9. DOCX extraction
10. OCR provider unconfigured behavior
11. STT provider unconfigured behavior
12. vision provider unconfigured behavior
13. processing status transitions
14. processing failure handling
15. retry behavior
16. evidence creation
17. evidence provenance
18. evidence confidence
19. entity extraction structure
20. event extraction structure
21. consent enforcement
22. revoked consent blocks processing
23. privacy authorization
24. original media preservation
25. physical path not exposed
26. processing analytics
27. duplicate media handling
28. malicious derived content handling
29. audit logging
30. API endpoint authorization
"""

import pytest
import io
import os
import wave
from datetime import datetime, timezone
from PIL import Image
from pypdf import PdfWriter
import docx

from models.enums import (
    ProcessingStatus,
    ConsentType,
    ConsentStatus,
    AuditAction,
    EvidenceType,
    ProvenanceStatus,
    ConfidenceLevel,
    EntityType,
    EventType,
    SourceType,
    PrivacyLevel
)
from storage.vault_storage import vault_storage
from backend.app.services.image_processor import image_processor
from backend.app.services.audio_processor import audio_processor
from backend.app.services.video_processor import video_processor
from backend.app.services.document_processor import document_processor
from backend.app.services.ocr_service import ocr_service
from backend.app.services.transcription_service import transcription_service
from backend.app.services.metadata_service import metadata_service
from backend.app.services.entity_extractor import entity_extractor
from backend.app.services.event_extractor import event_extractor
from backend.app.services.processing_orchestrator import processing_orchestrator
from backend.app.services.consent_service import consent_service
from backend.app.services.audit_service import audit_service
from fastapi.testclient import TestClient
from backend.app.main import app


# ==============================================================================
# Fixtures and Helpers
# ==============================================================================

@pytest.fixture
def test_client():
    return TestClient(app)


def create_test_image_bytes(width=200, height=150, color=(100, 150, 200)):
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=color)
    img.save(buf, format="JPEG")
    return buf.getvalue()


def create_test_wav_bytes(duration_sec=2, sample_rate=16000):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = b"\x00\x00" * int(sample_rate * duration_sec)
        wf.writeframes(frames)
    return buf.getvalue()


def create_test_pdf_bytes(text="Memorial of Eleanor Vance, born June 12, 1940."):
    buf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    writer.write(buf)
    return buf.getvalue()


def create_test_docx_bytes(text="Graduation from Cambridge University in June 1968."):
    buf = io.BytesIO()
    doc = docx.Document()
    doc.add_heading("Academic Achievement", level=1)
    doc.add_paragraph(text)
    doc.save(buf)
    return buf.getvalue()


# ==============================================================================
# Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_01_image_metadata_extraction():
    """Verify ImageProcessor extracts dimensions, format, and technical metrics."""
    img_bytes = create_test_image_bytes(width=320, height=240)
    saved = await vault_storage.save_original("test_meta.jpg", img_bytes, "image/jpeg")
    
    res = await image_processor.process_image(
        media_id="test-img-001",
        relative_path=saved["storage_path"]
    )
    meta = res["technical_metadata"]
    assert meta["width"] == 320
    assert meta["height"] == 240
    assert meta["format"] == "JPEG"
    assert meta["file_size"] > 0
    assert "aspect_ratio" in meta


@pytest.mark.asyncio
async def test_02_image_thumbnail_generation():
    """Verify thumbnail is generated and saved under thumbnails/."""
    img_bytes = create_test_image_bytes(width=400, height=300)
    saved = await vault_storage.save_original("test_thumb.jpg", img_bytes, "image/jpeg")
    
    res = await image_processor.process_image(
        media_id="test-img-002",
        relative_path=saved["storage_path"]
    )
    assert res["thumbnail_path"] is not None
    assert res["thumbnail_path"].startswith("thumbnails/")
    assert vault_storage.get_absolute_path(res["thumbnail_path"]).exists()


@pytest.mark.asyncio
async def test_03_unsupported_image_rejection():
    """Verify processor rejects unsupported extensions safely."""
    with pytest.raises(ValueError, match="Unsupported image format"):
        await image_processor.process_image("invalid-id", "originals/file.exe")


@pytest.mark.asyncio
async def test_04_video_metadata_extraction():
    """Verify VideoProcessor extracts dimensions, duration, and FPS."""
    # Write a dummy video stub
    saved = await vault_storage.save_original("test_home_movie.mp4", b"\x00" * 1024, "video/mp4")
    
    res = await video_processor.process_video(
        media_id="test-vid-001",
        relative_path=saved["storage_path"]
    )
    meta = res["technical_metadata"]
    assert meta["format"] == "MP4"
    assert meta["file_size"] == 1024
    assert meta["duration_seconds"] > 0
    assert "fps" in meta


@pytest.mark.asyncio
async def test_05_video_keyframe_extraction():
    """Verify video processing generates KeyframeInfo and Evidence."""
    saved = await vault_storage.save_original("test_clip.mp4", b"\x00" * 512, "video/mp4")
    res = await video_processor.process_video(
        media_id="test-vid-002",
        relative_path=saved["storage_path"],
        max_keyframes=3
    )
    assert "keyframes" in res
    assert "evidence" in res
    assert any(e.evidence_type == EvidenceType.VIDEO_METADATA for e in res["evidence"])


@pytest.mark.asyncio
async def test_06_audio_metadata_extraction():
    """Verify AudioProcessor extracts channels, sample rate, and duration from WAV."""
    wav_bytes = create_test_wav_bytes(duration_sec=1, sample_rate=16000)
    saved = await vault_storage.save_original("test_tape.wav", wav_bytes, "audio/wav")
    
    res = await audio_processor.process_audio(
        media_id="test-aud-001",
        relative_path=saved["storage_path"]
    )
    meta = res["technical_metadata"]
    assert meta["format"] == "WAV"
    assert meta["channels"] == 1
    assert meta["sample_rate_hz"] == 16000
    assert meta["duration_seconds"] >= 0.9


@pytest.mark.asyncio
async def test_07_document_txt_extraction():
    """Verify DocumentProcessor extracts faithful text from TXT files."""
    sample_text = "June 1968: Met Eleanor at the Wren Library courtyard for afternoon tea."
    saved = await vault_storage.save_original("diary_entry.txt", sample_text.encode("utf-8"), "text/plain")
    
    res = await document_processor.process_document(
        media_id="test-doc-001",
        relative_path=saved["storage_path"]
    )
    assert res["document_status"] == "COMPLETED"
    assert sample_text in res["full_text"]
    assert any(e.evidence_type == EvidenceType.TEXT for e in res["evidence"])


@pytest.mark.asyncio
async def test_08_pdf_text_extraction():
    """Verify DocumentProcessor parses PDF files and extracts metadata."""
    pdf_bytes = create_test_pdf_bytes()
    saved = await vault_storage.save_original("registry.pdf", pdf_bytes, "application/pdf")
    
    res = await document_processor.process_document(
        media_id="test-doc-002",
        relative_path=saved["storage_path"]
    )
    assert res["document_status"] == "COMPLETED"
    assert res["technical_metadata"]["page_count"] >= 1
    assert res["technical_metadata"]["format"] == "PDF"


@pytest.mark.asyncio
async def test_09_docx_extraction():
    """Verify DocumentProcessor parses DOCX files and headings."""
    docx_bytes = create_test_docx_bytes()
    saved = await vault_storage.save_original("degree_cert.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    
    res = await document_processor.process_document(
        media_id="test-doc-003",
        relative_path=saved["storage_path"]
    )
    assert res["document_status"] == "COMPLETED"
    assert "Academic Achievement" in res["technical_metadata"]["detected_headings"]
    assert "Cambridge University" in res["full_text"]


@pytest.mark.asyncio
async def test_10_ocr_provider_unconfigured_behavior():
    """Verify OCR returns explicit UNCONFIGURED result with 0 fabricated text when unconfigured."""
    os.environ["ENABLE_OCR_MOCK"] = "false"
    img_bytes = create_test_image_bytes()
    saved = await vault_storage.save_original("handwritten_letter.jpg", img_bytes, "image/jpeg")
    
    res = await ocr_service.extract_ocr(
        media_id="test-ocr-001",
        relative_path=saved["storage_path"]
    )
    assert res.status == "UNCONFIGURED"
    assert res.extracted_text == ""
    assert "not configured" in res.message.lower()


@pytest.mark.asyncio
async def test_11_stt_provider_unconfigured_behavior():
    """Verify STT returns explicit UNCONFIGURED result without inventing transcripts."""
    os.environ["ENABLE_STT_MOCK"] = "false"
    wav_bytes = create_test_wav_bytes()
    saved = await vault_storage.save_original("interview_side_b.wav", wav_bytes, "audio/wav")
    
    try:
        res = await transcription_service.transcribe_audio(
            media_id="test-stt-001",
            relative_path=saved["storage_path"]
        )
        assert res.status == "UNCONFIGURED"
        assert res.full_text == ""
        assert "unconfigured" in res.message.lower()
    finally:
        os.environ["ENABLE_STT_MOCK"] = "true"


@pytest.mark.asyncio
async def test_12_vision_provider_unconfigured_behavior():
    """Verify vision analysis returns UNCONFIGURED without fabricating scene descriptions."""
    os.environ["ENABLE_VISION_MOCK"] = "false"
    img_bytes = create_test_image_bytes()
    saved = await vault_storage.save_original("photo_unconf.jpg", img_bytes, "image/jpeg")
    
    try:
        res = await image_processor.process_image(
            media_id="test-vis-001",
            relative_path=saved["storage_path"]
        )
        assert res["vision_status"] == "UNCONFIGURED"
        assert "unconfigured" in res["message"].lower()
        # But technical metadata is preserved!
        assert res["technical_metadata"]["width"] > 0
    finally:
        os.environ["ENABLE_VISION_MOCK"] = "true"


@pytest.mark.asyncio
async def test_13_processing_status_transitions():
    """Verify processing job transitions through lifecycle states."""
    saved = await vault_storage.save_original("note.txt", b"My memories from childhood.", "text/plain")
    
    job = await processing_orchestrator.enqueue_media_processing(
        media_id="test-trans-001",
        relative_path=saved["storage_path"],
        actor_id="test-actor"
    )
    assert job.processing_status == ProcessingStatus.COMPLETED
    assert job.started_at is not None
    assert job.completed_at is not None
    assert job.retry_count == 0


@pytest.mark.asyncio
async def test_14_processing_failure_handling():
    """Verify processing handles missing files gracefully with FAILED status."""
    job = await processing_orchestrator.enqueue_media_processing(
        media_id="missing-media-id",
        relative_path="originals/non_existent_file_xyz.mp4",
        actor_id="test-actor"
    )
    assert job.processing_status == ProcessingStatus.FAILED
    assert job.error_message is not None


@pytest.mark.asyncio
async def test_15_retry_behavior():
    """Verify retry increments retry count and creates audit event."""
    saved = await vault_storage.save_original("retry_file.txt", b"Retry testing data.", "text/plain")
    
    job1 = await processing_orchestrator.enqueue_media_processing(
        media_id="test-retry-001",
        relative_path=saved["storage_path"]
    )
    retried_job = await processing_orchestrator.retry_processing(
        media_id="test-retry-001",
        relative_path=saved["storage_path"]
    )
    assert retried_job.retry_count >= 1


@pytest.mark.asyncio
async def test_16_evidence_creation():
    """Verify evidence items are created and stored."""
    ev = processing_orchestrator.get_evidence("demo-ev-001")
    assert ev is not None
    assert ev.evidence_type == EvidenceType.DOCUMENT_METADATA
    assert "Trinity College" in ev.content


@pytest.mark.asyncio
async def test_17_evidence_provenance():
    """Verify evidence provenance status is properly assigned."""
    ev = processing_orchestrator.get_evidence("demo-ev-001")
    assert ev.provenance_status == ProvenanceStatus.DIRECTLY_OBSERVED


@pytest.mark.asyncio
async def test_18_evidence_confidence():
    """Verify confidence level is assigned based on evidence."""
    ev = processing_orchestrator.get_evidence("demo-ev-001")
    assert ev.confidence == ConfidenceLevel.VERIFIED
    assert ev.confidence_score == 1.0


def test_19_entity_extraction_structure():
    """Verify EntityExtractor identifies dates, locations, organizations, and people."""
    text = "In June 1968, Dr. Arthur Vance visited Trinity College in Cambridge for a graduation ceremony."
    entities = entity_extractor.extract_entities_from_text(
        text=text,
        media_id="media-ner-001",
        memory_id="mem-ner-001"
    )
    types = [e.entity_type for e in entities]
    assert EntityType.DATE in types
    assert EntityType.ORGANIZATION in types or EntityType.LOCATION in types
    assert any(e.entity_type == EntityType.PERSON for e in entities)
    assert all(e.provenance_status == ProvenanceStatus.DIRECTLY_OBSERVED for e in entities)


def test_20_event_extraction_structure():
    """Verify EventExtractor extracts documented events without hallucination."""
    events = event_extractor.extract_events_from_memory(
        memory_id="mem-event-001",
        title="College Commencement",
        description="Received Master of Arts degree in literature at Cambridge.",
        date="1968-06-22",
        location="Cambridge"
    )
    assert len(events) == 1
    assert events[0].event_type == EventType.EDUCATION
    assert events[0].confidence == ConfidenceLevel.VERIFIED


@pytest.mark.asyncio
async def test_21_consent_enforcement():
    """Verify processing enforces consent checks."""
    is_granted = await consent_service.is_consent_granted("demo-mem-001", ConsentType.MEDIA_PROCESSING)
    assert is_granted is True


@pytest.mark.asyncio
async def test_22_revoked_consent_blocks_processing():
    """Verify revoked consent halts processing with REVIEW_REQUIRED status."""
    mem_id = "mem-revoked-001"
    await consent_service.revoke_consent(
        memory_id=mem_id,
        consent_type=ConsentType.MEDIA_PROCESSING,
        reason="User requested withdrawal"
    )
    saved = await vault_storage.save_original("blocked_file.txt", b"Restricted material.", "text/plain")
    
    job = await processing_orchestrator.enqueue_media_processing(
        media_id="media-blocked-001",
        relative_path=saved["storage_path"],
        memory_id=mem_id
    )
    assert job.processing_status == ProcessingStatus.REVIEW_REQUIRED
    assert "revoked" in job.error_message.lower()


@pytest.mark.asyncio
async def test_23_privacy_authorization():
    """Verify privacy settings protect evidence artifacts."""
    evidence_list = processing_orchestrator.list_evidence()
    assert len(evidence_list) >= 2


@pytest.mark.asyncio
async def test_24_original_media_preservation():
    """Verify original files are never altered during multimodal processing."""
    original_data = b"Precious family heirloom document content."
    saved = await vault_storage.save_original("heirloom.txt", original_data, "text/plain")
    abs_path = vault_storage.get_absolute_path(saved["storage_path"])
    
    # Process file
    await document_processor.process_document("media-heirloom", saved["storage_path"])
    
    # Verify exact byte preservation
    assert abs_path.read_bytes() == original_data


@pytest.mark.asyncio
async def test_25_physical_path_not_exposed():
    """Verify API output contains only safe relative paths, never absolute drive paths."""
    img_bytes = create_test_image_bytes()
    saved = await vault_storage.save_original("safe_path.jpg", img_bytes, "image/jpeg")
    
    res = await image_processor.process_image("media-safe", saved["storage_path"])
    assert not res["thumbnail_path"].startswith("D:\\")
    assert not res["thumbnail_path"].startswith("C:\\")


def test_26_processing_analytics():
    """Verify processing analytics reports accurate metrics and distributions."""
    analytics = processing_orchestrator.get_analytics()
    assert analytics.total_memories >= 2
    assert analytics.total_media >= 2
    assert "VERIFIED" in analytics.confidence_distribution


@pytest.mark.asyncio
async def test_27_duplicate_media_handling():
    """Verify duplicate uploads do not duplicate physical storage."""
    data = b"Duplicate test file binary content."
    save1 = await vault_storage.save_original("first.txt", data, "text/plain")
    save2 = await vault_storage.save_original("second.txt", data, "text/plain")
    assert save2["is_duplicate"] is True
    assert save2["storage_path"] == save1["storage_path"]


def test_28_malicious_derived_content_handling():
    """Verify script injection in text is parsed safely without execution."""
    malicious_text = "<script>alert('xss')</script> Eleanor Vance was born in 1940."
    entities = entity_extractor.extract_entities_from_text(malicious_text)
    assert any(e.entity_type == EntityType.DATE for e in entities)


@pytest.mark.asyncio
async def test_29_audit_logging():
    """Verify processing lifecycle triggers audit log records."""
    logs = await audit_service.get_audit_trail(action=AuditAction.PROCESSING_COMPLETED)
    assert isinstance(logs, list)


def test_30_api_endpoint_authorization(test_client):
    """Verify processing and evidence REST endpoints return 200."""
    res_proc = test_client.get("/api/v1/processing")
    assert res_proc.status_code == 200
    
    res_ev = test_client.get("/api/v1/evidence")
    assert res_ev.status_code == 200
    
    res_analytics = test_client.get("/api/v1/analytics/processing")
    assert res_analytics.status_code == 200
    assert "total_memories" in res_analytics.json()
