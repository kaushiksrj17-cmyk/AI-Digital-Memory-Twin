"""Claim Extractor and Evidence Mapper for ECHO Memorial AI.

Decomposes generated response texts into atomic factual claims
and maps each claim to supporting archival evidence IDs.
"""

from typing import List, Dict, Any, Optional
import re
from uuid import uuid4

from models.enums import ClaimStatus, ConfidenceLevel
from models.conversation import ResponseClaim


class ClaimExtractor:
    """Extracts factual assertions and verifies evidence coverage."""

    @staticmethod
    def extract_claims(
        response_text: str,
        evidence_items: List[Dict[str, Any]],
        message_id: Optional[str] = None,
        contradictions: Optional[List[Dict[str, Any]]] = None,
    ) -> List[ResponseClaim]:
        """Extract sentence-level claims and map to supporting evidence IDs."""
        claims: List[ResponseClaim] = []

        # Split response into distinct sentences
        raw_sentences = re.split(r"(?<=[.!?])\s+", response_text.strip())
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]

        # Ignore standard disclaimers, evidentiary meta-commentary, or no-evidence phrases
        disclaimer_markers = [
            "ai-generated memorial representation",
            "does not recreate consciousness",
            "don't have enough information",
            "do not have enough information",
            "not present in the preserved archive",
            "both accounts remain preserved",
            "accounts remain preserved",
            "conflicting accounts",
            "archival records reflect conflicting",
        ]

        contradiction_subjects = [c.get("subject", "").lower() for c in (contradictions or []) if c.get("subject")]

        for sent in sentences:
            sent_lower = sent.lower()
            if any(marker in sent_lower for marker in disclaimer_markers):
                continue

            # Identify candidate subject/predicate
            subject = None
            if "studied" in sent_lower or "degree" in sent_lower:
                subject = "education"
            elif "worked" in sent_lower or "company" in sent_lower or "job" in sent_lower:
                subject = "career"
            elif "born" in sent_lower:
                subject = "birth"
            elif "married" in sent_lower or "wedding" in sent_lower:
                subject = "marriage"
            elif "travel" in sent_lower or "visited" in sent_lower:
                subject = "travel"
            else:
                subject = "biography"

            # Check for contradiction overlap
            is_contradicted = any(subj in sent_lower for subj in contradiction_subjects)

            # Match against evidence items
            supporting_ids: List[str] = []
            sent_tokens = set(re.findall(r"\w+", sent_lower)) - {"the", "a", "an", "is", "was", "in", "at", "to", "and", "of", "for", "on", "with"}

            for ev in evidence_items:
                ev_text = (ev.get("text") or ev.get("evidence_text") or "").lower()
                ev_tokens = set(re.findall(r"\w+", ev_text))
                common_tokens = sent_tokens.intersection(ev_tokens)

                # If significant overlap, record supporting evidence ID
                if len(common_tokens) >= 2 or (len(sent_tokens) <= 3 and len(common_tokens) >= 1):
                    ev_id = ev.get("id") or ev.get("evidence_id") or ev.get("result_id") or "ev-unspecified"
                    supporting_ids.append(ev_id)

            # Determine claim status
            if is_contradicted:
                status = ClaimStatus.CONTRADICTED
                confidence = ConfidenceLevel.SUPPORTED_INFERENCE
                confidence_score = 0.5
            elif supporting_ids:
                status = ClaimStatus.SUPPORTED
                confidence = ConfidenceLevel.VERIFIED
                confidence_score = 0.95
            else:
                status = ClaimStatus.UNSUPPORTED
                confidence = ConfidenceLevel.UNKNOWN_UNSUPPORTED
                confidence_score = 0.0

            claims.append(
                ResponseClaim(
                    claim_id=str(uuid4()),
                    message_id=message_id,
                    text=sent,
                    subject=subject,
                    predicate=None,
                    object=None,
                    supporting_evidence_ids=supporting_ids,
                    confidence=confidence,
                    confidence_score=confidence_score,
                    status=status,
                    notes=f"Found {len(supporting_ids)} matching evidence items."
                )
            )

        return claims


_global_claim_extractor: Optional[ClaimExtractor] = None


def get_claim_extractor() -> ClaimExtractor:
    global _global_claim_extractor
    if _global_claim_extractor is None:
        _global_claim_extractor = ClaimExtractor()
    return _global_claim_extractor
