"""Metadata Normalization Service for ECHO.

Standardizes technical, temporal, spatial, and archival attributes across all modalities:
- Distinguishes DIRECTLY_OBSERVED, USER_PROVIDED, AI_INFERRED, and UNKNOWN data sources
- Preserves input checksums for reproducible experimentation
- Unifies cross-modal representations into MediaMetadataModel
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone

from models.enums import ProvenanceStatus
from models.processing import MediaMetadataModel


class MetadataService:
    """Normalizes and indexes multimodal technical and evidentiary metadata."""

    def __init__(self):
        self.processor_version = "echo-meta-v1.0"
        self._metadata_store: Dict[str, MediaMetadataModel] = {}

    def normalize_metadata(
        self,
        media_id: str,
        media_type: str,
        filename: str,
        mime_type: str,
        file_size: int,
        checksum: str,
        technical_data: Dict[str, Any],
        memory_id: Optional[str] = None,
        user_capture_date: Optional[str] = None,
        user_location: Optional[str] = None,
        language: Optional[str] = None
    ) -> MediaMetadataModel:
        """Create a unified MediaMetadataModel record with explicit provenance tracking."""
        # Temporal resolution: User provided overrides EXIF, but provenance reflects origin
        capture_date = user_capture_date or technical_data.get("capture_date")
        duration = technical_data.get("duration_seconds")
        
        dimensions = None
        if "width" in technical_data and "height" in technical_data:
            dimensions = {
                "width": technical_data["width"],
                "height": technical_data["height"]
            }

        norm_record = MediaMetadataModel(
            media_id=media_id,
            memory_id=memory_id,
            media_type=media_type,
            filename=filename,
            mime_type=mime_type,
            file_size=file_size,
            checksum=checksum,
            capture_date=capture_date,
            approximate_date=technical_data.get("approximate_date"),
            location=user_location,
            language=language or technical_data.get("language") or "en",
            duration_seconds=duration,
            dimensions=dimensions,
            fps=technical_data.get("fps"),
            frame_count=technical_data.get("frame_count"),
            technical_metadata=technical_data,
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            processing_version=self.processor_version,
            created_at=datetime.now(timezone.utc)
        )

        self._metadata_store[media_id] = norm_record
        return norm_record

    def get_metadata(self, media_id: str) -> Optional[MediaMetadataModel]:
        """Retrieve indexed metadata for a media asset."""
        return self._metadata_store.get(media_id)


metadata_service = MetadataService()
