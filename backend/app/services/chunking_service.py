"""Configurable Text Chunking Service for Multimodal Evidence.

Preserves exact source mapping, byte/character offsets, evidence IDs,
provenance status, and confidence levels across chunks.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4
import re
from datetime import datetime, timezone

from models.retrieval import EvidenceChunk
from models.enums import ProvenanceStatus, ConfidenceLevel


class ChunkingService:
    """Chunks documents, OCR text, transcripts, and stories with complete evidentiary traceability."""

    def __init__(self, default_chunk_size: int = 400, default_overlap: int = 50):
        self.default_chunk_size = default_chunk_size
        self.default_overlap = default_overlap

    def chunk_text(
        self,
        text: str,
        memorial_profile_id: str = "default-profile-001",
        memory_id: Optional[str] = None,
        media_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        source_reference: str = "Primary Archive",
        provenance: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED,
        confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED,
        confidence_score: float = 1.0,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[EvidenceChunk]:
        """Split text into overlapping chunks while tracking start/end character offsets."""
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        c_size = chunk_size or self.default_chunk_size
        c_overlap = overlap or self.default_overlap
        
        # Ensure valid window bounds
        if c_overlap >= c_size:
            c_overlap = max(0, c_size // 4)

        step = max(1, c_size - c_overlap)
        chunks: List[EvidenceChunk] = []
        chunk_index = 0
        total_len = len(clean_text)

        start = 0
        while start < total_len:
            end = min(start + c_size, total_len)
            
            # If not at the very end, try to break cleanly on whitespace/sentence
            if end < total_len:
                boundary = clean_text.rfind(" ", start, end)
                if boundary > start + (c_size // 2):
                    end = boundary

            chunk_content = clean_text[start:end].strip()
            if chunk_content:
                chunk = EvidenceChunk(
                    chunk_id=str(uuid4()),
                    memorial_profile_id=memorial_profile_id,
                    memory_id=memory_id,
                    media_id=media_id,
                    evidence_id=evidence_id,
                    chunk_index=chunk_index,
                    text=chunk_content,
                    start_offset=start,
                    end_offset=end,
                    source_reference=source_reference,
                    provenance=provenance,
                    confidence=confidence,
                    confidence_score=confidence_score,
                    created_at=datetime.now(timezone.utc)
                )
                chunks.append(chunk)
                chunk_index += 1

            if end >= total_len:
                break
            start = start + step

        return chunks

    def chunk_memory_narrative(
        self,
        memory_id: str,
        memorial_profile_id: str,
        title: str,
        description: str,
        narrative: Optional[str] = None,
        provenance: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED,
        confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED,
        confidence_score: float = 1.0
    ) -> List[EvidenceChunk]:
        """Chunk a memory's title, description, and narrative as traceable units."""
        combined_text = f"{title}\n\n{description}"
        if narrative:
            combined_text += f"\n\n{narrative}"

        return self.chunk_text(
            text=combined_text,
            memorial_profile_id=memorial_profile_id,
            memory_id=memory_id,
            source_reference=f"Memory: {title}",
            provenance=provenance,
            confidence=confidence,
            confidence_score=confidence_score
        )
