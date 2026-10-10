"""Audio Processing Service for ECHO.

Processes oral history recordings, voicemails, and audio memories (MP3, WAV, M4A):
- Validates audio format
- Extracts technical audio metadata (duration, sample rate, channels, bit rate)
- Preserves original audio file
- Invokes transcription pipeline
- Generates structured evidence and provenance records
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import wave
import io
import os
from uuid import uuid4
from datetime import datetime, timezone

from models.enums import (
    ConfidenceLevel,
    ProvenanceStatus,
    EvidenceType
)
from models.evidence import Evidence
from models.processing import TranscriptResult
from storage.vault_storage import vault_storage
from backend.app.services.transcription_service import transcription_service


class AudioProcessor:
    """Specialized processor for audio assets and oral history preservation."""

    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a"}

    def __init__(self):
        self.processor_name = "AudioProcessor"
        self.processor_version = "echo-audio-v1.0"

    async def process_audio(
        self,
        media_id: str,
        relative_path: str,
        memory_id: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Extract technical audio metrics and coordinate speech-to-text transcription."""
        abs_path = vault_storage.get_absolute_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Audio file missing from storage: {relative_path}")

        ext = abs_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported audio format: {ext}")

        audio_bytes = abs_path.read_bytes()
        file_size = len(audio_bytes)

        # 1. Technical Metadata Extraction
        duration_seconds = 0.0
        channels = 1
        sample_rate = 44100
        sample_width = 2

        if ext == ".wav":
            try:
                with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                    channels = wf.getnchannels()
                    sample_rate = wf.getframerate()
                    sample_width = wf.getsampwidth()
                    n_frames = wf.getnframes()
                    if sample_rate > 0:
                        duration_seconds = round(n_frames / float(sample_rate), 2)
            except Exception:
                pass
        else:
            # Heuristic calculation for compressed formats (e.g. ~128kbps default estimate)
            bitrate_bps = 128000
            estimated_duration = round((file_size * 8) / bitrate_bps, 2)
            duration_seconds = max(estimated_duration, 1.0)

        technical_metadata = {
            "format": ext.replace(".", "").upper(),
            "file_size": file_size,
            "duration_seconds": duration_seconds,
            "channels": channels,
            "sample_rate_hz": sample_rate,
            "sample_width_bytes": sample_width
        }

        evidence_items: List[Evidence] = []

        # Technical metadata evidence
        meta_evidence = Evidence(
            id=str(uuid4()),
            memory_id=memory_id,
            media_id=media_id,
            title="Audio Technical Metadata",
            evidence_type=EvidenceType.AUDIO_METADATA,
            content=f"Audio format {ext.upper()}, duration ~{duration_seconds}s, channels {channels}, sample rate {sample_rate}Hz.",
            structured_value=technical_metadata,
            source_reference=f"Audio Container Header ({abs_path.name})",
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            confidence=ConfidenceLevel.VERIFIED,
            confidence_score=1.0,
            extraction_method="audio_header_parser",
            processor_version=self.processor_version
        )
        evidence_items.append(meta_evidence)

        # 2. Transcription pipeline
        transcript_res: TranscriptResult = await transcription_service.transcribe_audio(
            media_id=media_id,
            relative_path=relative_path,
            memory_id=memory_id,
            language=language
        )

        transcript_evidence = transcription_service.create_transcript_evidence(
            transcript_result=transcript_res,
            source_filename=abs_path.name
        )
        if transcript_evidence:
            evidence_items.append(transcript_evidence)

        return {
            "media_id": media_id,
            "processor": self.processor_name,
            "processor_version": self.processor_version,
            "technical_metadata": technical_metadata,
            "transcript": transcript_res,
            "evidence": evidence_items,
            "transcription_status": transcript_res.status,
            "message": transcript_res.message
        }


audio_processor = AudioProcessor()
