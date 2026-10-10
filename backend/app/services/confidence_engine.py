"""Confidence Engine for ECHO Conversational Memorial AI.

Calculates grounded confidence ratings and numerical credibility scores
derived from claim verification coverage, source pedigree, and absence of conflict.
"""

from typing import List, Dict, Any, Optional
from models.enums import ConfidenceLevel, ClaimStatus, GuardianDecision
from models.conversation import ResponseClaim, GuardianResult


class ConfidenceEngine:
    """Calculates explainable confidence metrics for RAG responses."""

    @staticmethod
    def calculate_response_confidence(
        claims: List[ResponseClaim],
        evidence_items: List[Dict[str, Any]],
        guardian_result: Optional[GuardianResult] = None,
        contradictions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Compute tri-state level and normalized score [0.0 - 1.0]."""
        # If blocked or no evidence is present:
        if guardian_result and guardian_result.guardian_status == GuardianDecision.BLOCK:
            return {
                "confidence_level": ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                "confidence_score": 0.0,
                "methodology": "Blocked by Memory Guardian.",
            }

        if not evidence_items:
            return {
                "confidence_level": ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                "confidence_score": 0.0,
                "methodology": "Zero supporting evidence found in archive.",
            }

        if not claims:
            return {
                "confidence_level": ConfidenceLevel.SUPPORTED_INFERENCE,
                "confidence_score": 0.5,
                "methodology": "General statement grounded in background archive context.",
            }

        total_claims = len(claims)
        supported_count = sum(1 for c in claims if c.status == ClaimStatus.SUPPORTED)
        partial_count = sum(1 for c in claims if c.status == ClaimStatus.PARTIALLY_SUPPORTED)
        unsupported_count = sum(1 for c in claims if c.status == ClaimStatus.UNSUPPORTED)
        contradicted_count = sum(1 for c in claims if c.status == ClaimStatus.CONTRADICTED)

        # Baseline score calculation: weighted claim support
        base_score = ((supported_count * 1.0) + (partial_count * 0.6)) / max(1, total_claims)

        # Penalty for unaddressed contradictions
        if contradictions or contradicted_count > 0:
            base_score = max(0.4, base_score - 0.2)

        # Penalty for unsupported claims
        if unsupported_count > 0:
            base_score = max(0.1, base_score - (0.3 * unsupported_count))

        # Assign Tri-State Category
        if base_score >= 0.85 and unsupported_count == 0 and not contradictions:
            level = ConfidenceLevel.VERIFIED
        elif base_score >= 0.40:
            level = ConfidenceLevel.SUPPORTED_INFERENCE
        else:
            level = ConfidenceLevel.UNKNOWN_UNSUPPORTED

        return {
            "confidence_level": level,
            "confidence_score": round(base_score, 2),
            "methodology": (
                f"Confidence Methodology: Evaluated {total_claims} claims: {supported_count} fully supported, "
                f"{partial_count} partial, {unsupported_count} unsupported, "
                f"{contradicted_count} conflicting."
            ),
        }

    def calculate_confidence(
        self,
        evidence_items: List[Dict[str, Any]],
        claims: List[ResponseClaim],
        contradictions: Optional[List[Dict[str, Any]]] = None,
        guardian_result: Optional[GuardianResult] = None,
    ):
        """Helper returning (confidence_level, confidence_score, methodology)."""
        res = self.calculate_response_confidence(
            claims=claims,
            evidence_items=evidence_items,
            guardian_result=guardian_result,
            contradictions=contradictions,
        )
        methodology = res["methodology"]
        if contradictions:
            methodology += " Contradiction penalty applied."
        return res["confidence_level"], res["confidence_score"], methodology


_global_confidence_engine: Optional[ConfidenceEngine] = None


def get_confidence_engine() -> ConfidenceEngine:
    global _global_confidence_engine
    if _global_confidence_engine is None:
        _global_confidence_engine = ConfidenceEngine()
    return _global_confidence_engine
