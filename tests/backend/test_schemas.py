"""Schema Validation Tests for Core Memory Entities."""

import sys
sys.path.insert(0, r"D:\ECHO")

from models import (
    ConfidenceLevel,
    VerificationStatus,
    SourceType,
    Memory,
    MemoryCreate,
    ProvenanceRecord,
    MemorialProfile,
    ETHICAL_DISCLAIMER_TEXT
)


def test_confidence_enum_values():
    """Verify three canonical confidence levels."""
    assert ConfidenceLevel.VERIFIED == "VERIFIED"
    assert ConfidenceLevel.SUPPORTED_INFERENCE == "SUPPORTED_INFERENCE"
    assert ConfidenceLevel.UNKNOWN_UNSUPPORTED == "UNKNOWN_UNSUPPORTED"


def test_memory_creation_with_provenance():
    """Verify Memory schema accepts spatiotemporal data and provenance citations."""
    provenance = ProvenanceRecord(
        source_id="doc-test-1",
        source_type=SourceType.DOCUMENT,
        source_title="Test Archive Certificate",
        source_reference="Box 4, Item 2",
        evidence_text="Sample authenticated transcript text",
        confidence=ConfidenceLevel.VERIFIED
    )

    mem = Memory(
        memorial_profile_id="prof-123",
        title="Test Archival Memory",
        narrative="Grounded account of event.",
        confidence=ConfidenceLevel.VERIFIED,
        verification_status=VerificationStatus.VERIFIED_BY_DOCUMENT,
        provenance_records=[provenance]
    )

    assert mem.confidence == ConfidenceLevel.VERIFIED
    assert len(mem.provenance_records) == 1
    assert mem.provenance_records[0].source_id == "doc-test-1"
