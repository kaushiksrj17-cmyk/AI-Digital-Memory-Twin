"""Memory Confidence Service.

Categorizes evidence reliability into the three canonical memorial states:
- GREEN (VERIFIED): Grounded in authenticated primary records.
- YELLOW (SUPPORTED_INFERENCE): Contextually deduced from correlated memories.
- RED (UNKNOWN_UNSUPPORTED): Unsupported or absent from archives.
"""

from typing import Dict, Any, List
from models.enums import ConfidenceLevel, VerificationStatus


class ConfidenceService:
    """Evaluates and assigns confidence levels to memories and assertions."""

    @staticmethod
    def calculate_confidence(
        has_primary_evidence: bool,
        verification_status: VerificationStatus,
        supporting_sources_count: int = 0
    ) -> ConfidenceLevel:
        if has_primary_evidence and verification_status in [
            VerificationStatus.VERIFIED_BY_DOCUMENT,
            VerificationStatus.VERIFIED_BY_FAMILY
        ]:
            return ConfidenceLevel.VERIFIED

        if supporting_sources_count > 0:
            return ConfidenceLevel.SUPPORTED_INFERENCE

        return ConfidenceLevel.UNKNOWN_UNSUPPORTED

    @staticmethod
    def get_confidence_metadata(level: ConfidenceLevel) -> Dict[str, Any]:
        """Provides UI color codes, badge labels, and descriptions."""
        mapping = {
            ConfidenceLevel.VERIFIED: {
                "level": "VERIFIED",
                "color_code": "#10B981",  # Emerald / Green
                "badge_class": "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
                "label": "Verified Evidence",
                "description": "Grounded in authenticated primary documents, photographs, or official records."
            },
            ConfidenceLevel.SUPPORTED_INFERENCE: {
                "level": "SUPPORTED_INFERENCE",
                "color_code": "#F59E0B",  # Amber / Yellow
                "badge_class": "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
                "label": "Supported Inference",
                "description": "Plausible contextual deduction corroborated by multiple intersecting records."
            },
            ConfidenceLevel.UNKNOWN_UNSUPPORTED: {
                "level": "UNKNOWN_UNSUPPORTED",
                "color_code": "#EF4444",  # Crimson / Red
                "badge_class": "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
                "label": "Unknown / Unsupported",
                "description": "Unrecorded in preserved archive. ECHO explicitly refuses to fabricate answers."
            }
        }
        return mapping[level]


confidence_service = ConfidenceService()
