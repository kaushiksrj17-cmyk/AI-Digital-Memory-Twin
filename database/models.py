"""SQLAlchemy Database Models for ECHO Memory Vault.

Compatible with both PostgreSQL and local SQLite.
Defines models for:
- memories
- media
- memory_people
- memory_locations
- consent_records
- audit_logs
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    Float,
    DateTime,
    JSON,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List, Dict, Any
from uuid import uuid4

from database.base import Base


class MemoryRecord(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    narrative: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Categories & Origin
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True, default="OTHER")
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True, default="FAMILY_STORY")
    
    # Confidence & Verification
    confidence: Mapped[str] = mapped_column(String(30), nullable=False, default="VERIFIED")
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False, index=True, default="PENDING_REVIEW")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Privacy & Consent
    privacy_level: Mapped[str] = mapped_column(String(30), nullable=False, index=True, default="PRIVATE")
    consent_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    consent_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Dates & Spatial
    date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    approximate_date: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Storage & Asset (Relative Paths Only)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    processing_status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")
    
    # Lifecycle & Soft State
    archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    uploaded_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # People and Tags (Stored as JSON array for SQLite/Postgres compatibility)
    people_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    tags_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    provenance_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)
    custom_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)


class MediaRecord(Base):
    __tablename__ = "media"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False, default="DOCUMENT")
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    relative_storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sha256_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    captured_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    privacy_level: Mapped[str] = mapped_column(String(30), default="PRIVATE")
    processing_status: Mapped[str] = mapped_column(String(30), default="COMPLETED")
    uploaded_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    metadata_extracted: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)


class MemoryPersonRecord(Base):
    __tablename__ = "memory_people"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memory_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    person_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    person_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class MemoryLocationRecord(Base):
    __tablename__ = "memory_locations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memory_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)


class ConsentRecordModel(Base):
    __tablename__ = "consent_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="demo-user-001")
    granter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    granter_relationship: Mapped[str] = mapped_column(String(100), default="Guardian")
    consent_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(255), default="STANDARD_ARCHIVE")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="GRANTED")
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    media_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    document_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLogRecord(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    actor: Mapped[str] = mapped_column(String(64), default="system", index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    result: Mapped[str] = mapped_column(String(30), default="SUCCESS")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)


# ==============================================================================
# Phase 3 Multimodal AI Memory Processing Tables
# ==============================================================================

class ProcessingJobRecord(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    media_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    processor: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    processing_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", index=True)
    processing_version: Mapped[str] = mapped_column(String(50), default="echo-processor-v1.0")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EvidenceRecordModel(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    media_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    structured_value: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    source_reference: Mapped[str] = mapped_column(String(255), default="Primary Archive")
    provenance_status: Mapped[str] = mapped_column(String(50), nullable=False, default="DIRECTLY_OBSERVED", index=True)
    confidence: Mapped[str] = mapped_column(String(30), nullable=False, default="VERIFIED", index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    extraction_method: Mapped[str] = mapped_column(String(100), default="direct_extraction")
    processor_version: Mapped[str] = mapped_column(String(50), default="echo-processor-v1.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ExtractedTextRecord(Base):
    __tablename__ = "extracted_text"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    media_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_format: Mapped[str] = mapped_column(String(20), default="TXT")
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TranscriptRecord(Base):
    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    media_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="en")
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TranscriptSegmentRecord(Base):
    __tablename__ = "transcript_segments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    transcript_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    speaker: Mapped[Optional[str]] = mapped_column(String(100), default="Speaker 1")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    language: Mapped[Optional[str]] = mapped_column(String(20), default="en")


class KeyframeRecord(Base):
    __tablename__ = "keyframes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    media_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    relative_storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EntityRecord(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    media_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    value: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED", index=True)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    extraction_method: Mapped[str] = mapped_column(String(100), default="heuristic_ner")
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class EventRecord(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    media_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    event_type: Mapped[str] = mapped_column(String(50), index=True, default="OTHER")
    date: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    approximate_date: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    people_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED")
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class MediaMetadataRecord(Base):
    __tablename__ = "media_metadata"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    media_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    technical_metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ==============================================================================
# Phase 4 Memory DNA, Knowledge Graph & Vector Retrieval Tables
# ==============================================================================

class MemoryDNARecord(Base):
    """Aggregated Memory DNA document record."""
    __tablename__ = "memory_dna"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default="default-profile-001")
    person_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_references_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class MemoryDNAItemRecord(Base):
    """Granular evidence-grounded fact item in Memory DNA."""
    __tablename__ = "memory_dna_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    memory_dna_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    key: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    value_json: Mapped[Any] = mapped_column(JSON, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_memory_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    source_media_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    source_evidence_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED", index=True)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    verification_status: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MemoryDNAVersionRecord(Base):
    """Historical snapshot of Memory DNA for reproducibility and audit."""
    __tablename__ = "memory_dna_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memory_dna_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    dna_snapshot_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    changed_by: Mapped[str] = mapped_column(String(64), default="system")
    change_reason: Mapped[str] = mapped_column(Text, default="Memory DNA build/update")
    source_evidence_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class GraphNodeRecord(Base):
    """Persistent entity or artifact node in the local knowledge graph."""
    __tablename__ = "graph_nodes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    label: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    properties_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    source_memory_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    source_evidence_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED", index=True)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class GraphRelationshipRecord(Base):
    """Evidence-backed relationship edge in the local knowledge graph."""
    __tablename__ = "graph_relationships"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    source_node: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    target_node: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    properties_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    source_evidence_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    source_memory_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED", index=True)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EntityAliasRecord(Base):
    """Aliases and conservative entity resolution mapping."""
    __tablename__ = "entity_aliases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    canonical_entity_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    alias_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), default="PERSON")
    similarity_score: Mapped[float] = mapped_column(Float, default=1.0)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_possible_duplicate: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ContradictionRecordModel(Base):
    """Documented conflicting claims for future Memory Guardian review."""
    __tablename__ = "contradictions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    subject: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    claim_a: Mapped[str] = mapped_column(Text, nullable=False)
    claim_b: Mapped[str] = mapped_column(Text, nullable=False)
    source_a: Mapped[str] = mapped_column(String(255), nullable=False)
    source_b: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence_a: Mapped[float] = mapped_column(Float, default=1.0)
    confidence_b: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class EvidenceChunkRecord(Base):
    """Text chunk preserving exact document offsets and evidence provenance."""
    __tablename__ = "evidence_chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    media_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    evidence_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_reference: Mapped[str] = mapped_column(String(255), default="Primary Archive")
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED", index=True)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class EmbeddingRecordModel(Base):
    """Indexed vector registry metadata. Does not store raw vector blobs if Qdrant configured."""
    __tablename__ = "embedding_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    vector_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    media_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    evidence_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    chunk_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), default="TEXT")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_reference: Mapped[str] = mapped_column(String(255), default="Primary Archive")
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED", index=True)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class RetrievalLogRecord(Base):
    """Retrieval query analytics and provenance tracking."""
    __tablename__ = "retrieval_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    query_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_mode: Mapped[str] = mapped_column(String(30), nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, default=5)
    candidate_count: Mapped[int] = mapped_column(Integer, default=0)
    returned_count: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    vector_candidates: Mapped[int] = mapped_column(Integer, default=0)
    keyword_candidates: Mapped[int] = mapped_column(Integer, default=0)
    graph_candidates: Mapped[int] = mapped_column(Integer, default=0)
    results_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ConversationSessionRecord(Base):
    """Conversation session metadata and topic summary."""
    __tablename__ = "conversation_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default-user-001")
    title: Mapped[str] = mapped_column(String(255), default="Memorial Dialogue Session")
    topic_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ConversationMessageRecord(Base):
    """Message turns with grounding confidence and Guardian audit status."""
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("conversation_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), index=True, default="assistant")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    guardian_status: Mapped[str] = mapped_column(String(30), default="PASS", index=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    retrieval_context_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    warnings_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ResponseClaimRecord(Base):
    """Factual claims extracted from generated responses with grounding status."""
    __tablename__ = "response_claims"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(String(64), ForeignKey("conversation_messages.id", ondelete="CASCADE"), index=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    predicate: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    object: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="SUPPORTED", index=True)
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    supporting_evidence_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ResponseSourceRecord(Base):
    """Structured, clickable source citations backing message assertions."""
    __tablename__ = "response_sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(String(64), ForeignKey("conversation_messages.id", ondelete="CASCADE"), index=True)
    source_title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="DOCUMENT")
    memory_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    media_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    evidence_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED")
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED")
    citation_label: Mapped[str] = mapped_column(String(100), default="Based on preserved evidence")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class GuardianResultRecord(Base):
    """Audit records of Memory Guardian reviews."""
    __tablename__ = "guardian_results"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    message_id: Mapped[str] = mapped_column(String(64), ForeignKey("conversation_messages.id", ondelete="CASCADE"), index=True)
    guardian_status: Mapped[str] = mapped_column(String(30), default="PASS", index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    violations_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    unsupported_claims_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    missing_evidence_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    recommended_action: Mapped[str] = mapped_column(String(50), default="DELIVER_RESPONSE")
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ConversationMetricRecord(Base):
    """Research evaluation telemetry for conversational RAG queries."""
    __tablename__ = "conversation_metrics"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    query_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    retrieval_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    generation_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    guardian_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    total_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    retrieved_evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    supporting_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    unsupported_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    contradiction_count: Mapped[int] = mapped_column(Integer, default=0)
    guardian_status: Mapped[str] = mapped_column(String(30), default="PASS")
    confidence_level: Mapped[str] = mapped_column(String(30), default="VERIFIED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


# ==============================================================================
# Phase 6 Voice Interaction & Memorial Voice Tables
# ==============================================================================

class VoiceProfileRecord(Base):
    """Authorized memorial voice profile metadata and consent lifecycle."""
    __tablename__ = "voice_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    owner_id: Mapped[str] = mapped_column(String(64), index=True, default="demo-user-001")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    voice_type: Mapped[str] = mapped_column(String(50), nullable=False, default="GENERIC_SYNTHETIC")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING_CONSENT", index=True)
    supported_languages_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=lambda: ["en", "ta", "hi"])
    provider_id: Mapped[str] = mapped_column(String(100), default="mock-tts")
    provider_voice_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    consent_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    consent_status: Mapped[str] = mapped_column(String(50), default="PENDING")
    retention_policy: Mapped[str] = mapped_column(String(100), default="STANDARD_ARCHIVE")
    sample_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    consent_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    disabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class VoiceSessionRecord(Base):
    """Voice interaction session state and dialogue turn context."""
    __tablename__ = "voice_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="default-profile-001")
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="demo-user-001")
    language: Mapped[str] = mapped_column(String(20), default="en")
    state: Mapped[str] = mapped_column(String(50), default="IDLE", index=True)
    voice_type: Mapped[str] = mapped_column(String(50), default="GENERIC_SYNTHETIC")
    voice_profile_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    conversation_session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    original_transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    edited_transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_transcript_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    input_audio_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    response_audio_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_guardian_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_metrics_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class VoiceAudioAssetRecord(Base):
    """Private, secure audio assets stored strictly within D:\\ECHO\\storage\\voice\\."""
    __tablename__ = "voice_audio_assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    relative_path: Mapped[str] = mapped_column(String(500), nullable=False)
    audio_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    sha256_checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    owner_id: Mapped[str] = mapped_column(String(64), default="demo-user-001", index=True)
    memorial_profile_id: Mapped[str] = mapped_column(String(64), default="default-profile-001", index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    voice_profile_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    is_temporary: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class VoiceSynthesisJobRecord(Base):
    """Synthesis event audit tracking for research compliance."""
    __tablename__ = "voice_synthesis_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    voice_profile_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    text_length: Mapped[int] = mapped_column(Integer, default=0)
    voice_type: Mapped[str] = mapped_column(String(50), default="GENERIC_SYNTHETIC")
    language: Mapped[str] = mapped_column(String(20), default="en")
    status: Mapped[str] = mapped_column(String(30), default="COMPLETED", index=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    block_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    audio_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class VoiceMetricRecord(Base):
    """Empirical research telemetry for voice processing queries."""
    __tablename__ = "voice_metrics"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    stt_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    tts_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    e2e_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    guardian_decision: Mapped[str] = mapped_column(String(30), default="PASS")
    is_consent_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_transcript_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    has_evidence: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


# ==============================================================================
# Phase 7 3D Memory Room and Memorial Avatar Tables
# ==============================================================================

class MemoryRoomConfigRecord(Base):
    """User and profile preferences for the 3D room environment."""
    __tablename__ = "memory_room_configs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, unique=True)
    theme: Mapped[str] = mapped_column(String(50), default="ARCHIVAL_WARM")
    ambient_light_intensity: Mapped[float] = mapped_column(Float, default=0.75)
    floor_material: Mapped[str] = mapped_column(String(50), default="hardwood_oak")
    wall_color: Mapped[str] = mapped_column(String(20), default="#1e293b")
    camera_position_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    show_labels: Mapped[bool] = mapped_column(Boolean, default=True)
    reduced_motion: Mapped[bool] = mapped_column(Boolean, default=False)
    audio_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AvatarConfigRecord(Base):
    """Ethical safeguards and rendering preferences for the 3D memorial presence avatar."""
    __tablename__ = "avatar_configs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    model_type: Mapped[str] = mapped_column(String(50), default="STYLIZED_GENERIC")
    display_name: Mapped[str] = mapped_column(String(100), default="Memorial Presence Guide")
    position_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    rotation_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    current_pose: Mapped[str] = mapped_column(String(50), default="IDLE_NEUTRAL")
    is_authorized: Mapped[bool] = mapped_column(Boolean, default=True)
    consent_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    asset_relative_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MemoryRoomMetricRecord(Base):
    """Empirical research telemetry for 3D room rendering performance and accessibility."""
    __tablename__ = "memory_room_metrics"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    init_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    selection_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    object_count: Mapped[int] = mapped_column(Integer, default=0)
    webgl_available: Mapped[bool] = mapped_column(Boolean, default=True)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


# ==============================================================================
# Phase 8 AI Life Timeline, Relationship Graph & Family Collaboration Tables
# ==============================================================================

class TimelineEventRecord(Base):
    """Chronological, evidence-grounded documented life events."""
    __tablename__ = "timeline_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="demo-profile-001")
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True, default="OTHER")
    
    # Chronology & Precision
    event_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    date_end: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_description: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_precision: Mapped[str] = mapped_column(String(30), nullable=False, default="EXACT")
    
    # Geography & Entities
    location_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    associated_people_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    associated_people_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    
    # Evidentiary Grounding
    linked_memory_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    evidence_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    source_type: Mapped[str] = mapped_column(String(50), default="DOCUMENT")
    
    # Confidence and Integrity
    confidence: Mapped[str] = mapped_column(String(30), nullable=False, default="VERIFIED")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False, default="VERIFIED", index=True)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED")
    is_ai_suggested: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Dispute Tracking
    is_disputed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    dispute_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    competing_evidence_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    
    # 3D Integration & Attribution
    memory_room_object_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(String(64), default="demo-user-001")
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RelationshipEdgeRecord(Base):
    """Evidence-backed relationship edges between entities in the knowledge graph."""
    __tablename__ = "relationship_edges"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="demo-profile-001")
    source_entity_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, default="PERSON")
    
    target_entity_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    target_entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, default="PERSON")
    
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    source_evidence_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    source_memory_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    provenance_status: Mapped[str] = mapped_column(String(50), default="DIRECTLY_OBSERVED")
    confidence: Mapped[str] = mapped_column(String(30), default="VERIFIED")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    verification_status: Mapped[str] = mapped_column(String(30), default="VERIFIED", index=True)
    
    is_disputed: Mapped[bool] = mapped_column(Boolean, default=False)
    dispute_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    competing_evidence_ids_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    
    created_by: Mapped[str] = mapped_column(String(64), default="demo-user-001")
    is_ai_suggested: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FamilyWorkspaceRecord(Base):
    """Archival family collaboration workspace."""
    __tablename__ = "family_workspaces"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, unique=True)
    owner_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FamilyMemberRecord(Base):
    """Authorized family members with 4-tier role-based access control."""
    __tablename__ = "family_members"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="CONTRIBUTOR", index=True)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    invited_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    relationship_to_subject: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FamilyInvitationRecord(Base):
    """Single-use invitations with cryptographically hashed tokens."""
    __tablename__ = "family_invitations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="CONTRIBUTOR")
    relationship_to_subject: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True)
    invited_by_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    invited_by_name: Mapped[str] = mapped_column(String(255), default="Memorial Guardian")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class FamilyContributionRecord(Base):
    """Memory contributions, corrections, and review decisions."""
    __tablename__ = "family_contributions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    contributor_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    contributor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contributor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contribution_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    proposed_content_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    original_content_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    supporting_evidence_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)
    contributor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[str] = mapped_column(String(30), default="SUPPORTED_INFERENCE")
    provenance: Mapped[str] = mapped_column(String(50), default="USER_PROVIDED")
    is_ai_suggested: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    reviewer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    review_decision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    version_history_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Phase8MetricRecord(Base):
    """Research telemetry for Phase 8 timeline, graph, and collaboration performance."""
    __tablename__ = "phase8_metrics"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    memorial_profile_id: Mapped[str] = mapped_column(String(64), index=True, default="demo-profile-001")
    timeline_retrieval_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    events_with_supporting_evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    events_awaiting_review_count: Mapped[int] = mapped_column(Integer, default=0)
    disputed_events_count: Mapped[int] = mapped_column(Integer, default=0)
    disputed_relationships_count: Mapped[int] = mapped_column(Integer, default=0)
    relationship_evidence_coverage_pct: Mapped[float] = mapped_column(Float, default=0.0)
    contribution_approval_count: Mapped[int] = mapped_column(Integer, default=0)
    contribution_rejection_count: Mapped[int] = mapped_column(Integer, default=0)
    review_turnaround_time_hours_avg: Mapped[float] = mapped_column(Float, default=0.0)
    unauthorized_access_attempts_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_entity_suggestions_count: Mapped[int] = mapped_column(Integer, default=0)
    contradiction_detection_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)





