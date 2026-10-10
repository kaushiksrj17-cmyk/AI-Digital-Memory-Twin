"""Multimodal Processing Job and Derivation Models for ECHO.

Defines schemas for:
- Processing jobs (Queue & Execution tracking)
- Media metadata extraction
- OCR results
- Audio transcription and segments
- Video keyframe representations
- Processing analytics & throughput metrics
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import (
    ProcessingStatus,
    SourceType,
    ConfidenceLevel,
    ProvenanceStatus,
    EvidenceType
)


class ProcessingJobBase(BaseModel):
    media_id: str = Field(..., description="Target media ID")
    memory_id: Optional[str] = Field(None, description="Associated memory ID if linked")
    processor: str = Field(..., description="Processor engine or pipeline (e.g. image_processor, document_processor)")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    processing_version: str = Field(default="echo-processor-v1.0")
    retry_count: int = Field(default=0, ge=0)
    error_message: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class ProcessingJobCreate(ProcessingJobBase):
    pass


class ProcessingJob(ProcessingJobBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class MediaMetadataModel(BaseModel):
    media_id: str
    memory_id: Optional[str] = None
    media_type: str
    filename: str
    mime_type: str
    file_size: int
    checksum: str
    capture_date: Optional[str] = None
    approximate_date: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    duration_seconds: Optional[float] = None
    dimensions: Optional[Dict[str, int]] = None  # {"width": 1920, "height": 1080}
    fps: Optional[float] = None
    frame_count: Optional[int] = None
    technical_metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    processing_version: str = "echo-processor-v1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OCRResult(BaseModel):
    media_id: str
    memory_id: Optional[str] = None
    status: str = "COMPLETED"  # COMPLETED or UNCONFIGURED
    extracted_text: str = ""
    pages: List[Dict[str, Any]] = Field(default_factory=list)
    language: str = "en"
    supported_languages: List[str] = Field(default_factory=lambda: ["en", "ta", "hi"])
    confidence: float = 1.0
    provenance: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    extraction_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: Optional[str] = None


class TranscriptSegment(BaseModel):
    segment_id: str = Field(default_factory=lambda: str(uuid4()))
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str] = "Speaker 1"
    confidence: float = 1.0
    language: str = "en"


class TranscriptResult(BaseModel):
    media_id: str
    memory_id: Optional[str] = None
    status: str = "COMPLETED"  # COMPLETED or UNCONFIGURED
    full_text: str = ""
    segments: List[TranscriptSegment] = Field(default_factory=list)
    language: str = "en"
    duration_seconds: Optional[float] = None
    confidence_score: float = 1.0
    provenance: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KeyframeInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    media_id: str
    memory_id: Optional[str] = None
    frame_number: int
    timestamp_seconds: float
    relative_storage_path: str
    description: Optional[str] = None
    provenance: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProcessingAnalytics(BaseModel):
    total_memories: int = 0
    total_media: int = 0
    pending_jobs: int = 0
    processing_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    review_required_jobs: int = 0
    images_processed: int = 0
    videos_processed: int = 0
    audio_transcribed: int = 0
    documents_processed: int = 0
    ocr_processed: int = 0
    confidence_distribution: Dict[str, int] = Field(default_factory=lambda: {
        "VERIFIED": 0,
        "SUPPORTED_INFERENCE": 0,
        "UNKNOWN_UNSUPPORTED": 0
    })
    modality_breakdown: Dict[str, int] = Field(default_factory=dict)
    average_latency_ms: float = 0.0
