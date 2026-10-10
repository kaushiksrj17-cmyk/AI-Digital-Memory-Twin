"""Provenance Engine for ECHO Conversational Memorial AI.

Synthesizes clickable, provenance-backed source citations from archival evidence
without exposing physical server filesystem paths or sensitive private metadata.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4

from models.enums import SourceType, ProvenanceStatus, ConfidenceLevel
from models.conversation import ResponseSource


class ProvenanceEngine:
    """Formats structured evidence citations for conversational turns."""

    @staticmethod
    def generate_sources(evidence_items: List[Dict[str, Any]]) -> List[ResponseSource]:
        """Convert retrieved evidence records into structured ResponseSource objects."""
        sources: List[ResponseSource] = []
        seen_refs = set()

        for ev in evidence_items:
            ref = ev.get("source_reference") or "Archival Document"
            if ref in seen_refs:
                continue
            seen_refs.add(ref)

            # Determine appropriate SourceType from payload or reference
            src_type_str = ev.get("source_type") or "DOCUMENT"
            src_type = SourceType.DOCUMENT
            if "photo" in ref.lower() or "image" in ref.lower():
                src_type = SourceType.ORIGINAL_PHOTO
            elif "audio" in ref.lower() or "tape" in ref.lower() or "voice" in ref.lower():
                src_type = SourceType.ORIGINAL_AUDIO
            elif "video" in ref.lower() or "recording" in ref.lower():
                src_type = SourceType.ORIGINAL_VIDEO
            elif "story" in ref.lower():
                src_type = SourceType.FAMILY_STORY

            # Determine ProvenanceStatus
            prov_str = ev.get("provenance_status", "DIRECTLY_OBSERVED")
            try:
                prov_status = ProvenanceStatus(prov_str)
            except Exception:
                prov_status = ProvenanceStatus.DIRECTLY_OBSERVED

            # Determine ConfidenceLevel
            conf_str = ev.get("confidence", "VERIFIED")
            try:
                conf_level = ConfidenceLevel(conf_str)
            except Exception:
                conf_level = ConfidenceLevel.VERIFIED

            evidence_text = ev.get("text") or ev.get("evidence_text") or ""
            # Clean any accidental server path leakage
            clean_text = evidence_text.replace("D:\\ECHO\\", "").replace("d:/echo/", "")

            src_id = ev.get("id") or ev.get("source_id") or str(uuid4())
            ev_id = ev.get("id") or ev.get("evidence_id") or ev.get("result_id")
            sources.append(
                ResponseSource(
                    source_id=src_id,
                    source_title=ref,
                    source_type=src_type,
                    memory_id=ev.get("memory_id"),
                    media_id=ev.get("media_id"),
                    evidence_id=ev_id,
                    evidence_text=clean_text[:400],
                    provenance_status=prov_status,
                    confidence=conf_level,
                    citation_label=f"Based on {ref}",
                    source_url=f"/evidence?id={src_id}",
                )
            )

        return sources


_global_provenance_engine: Optional[ProvenanceEngine] = None


def get_provenance_engine() -> ProvenanceEngine:
    global _global_provenance_engine
    if _global_provenance_engine is None:
        _global_provenance_engine = ProvenanceEngine()
    return _global_provenance_engine
