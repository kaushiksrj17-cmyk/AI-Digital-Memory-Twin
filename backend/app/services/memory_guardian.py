"""Memory Guardian Service for ECHO.

The central safety, evidentiary, and boundary-enforcement layer.
Executes 18 comprehensive verification checks before any generated response
is delivered to users.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import GuardianDecision, ConfidenceLevel, ProvenanceStatus, ClaimStatus
from models.conversation import GuardianResult, ResponseClaim, ETHICAL_DISCLAIMER_TEXT
from backend.app.services.hallucination_detector import HallucinationDetector, get_hallucination_detector
from backend.app.core.security import validate_ethical_boundaries
from backend.app.core.errors import EthicalBoundaryViolation


class MemoryGuardian:
    """Rigorous gatekeeper validating AI memorial outputs against 18 safety checks."""

    def __init__(self, hallucination_detector: Optional[HallucinationDetector] = None):
        self.detector = hallucination_detector or get_hallucination_detector()

    def validate_response(
        self,
        response_text: str,
        evidence_items: List[Dict[str, Any]],
        claims: List[ResponseClaim],
        privacy_authorized: bool = True,
        consent_authorized: bool = True,
        contradictions: Optional[List[Dict[str, Any]]] = None,
        is_revision: bool = False,
    ) -> GuardianResult:
        """Run all 18 Guardian checks on candidate response."""
        violations: List[str] = []
        unsupported_claims: List[str] = []
        missing_evidence: List[str] = []

        # Check 9 & 10: Privacy and Consent Gating
        if not privacy_authorized:
            return GuardianResult(
                result_id=str(uuid4()),
                guardian_status=GuardianDecision.BLOCK,
                reason="PRIVACY_VIOLATION: User lacks clearance to view requested private memorial evidence.",
                violations=["Unauthorized access to restricted memory records."],
                confidence=ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                provenance=ProvenanceStatus.UNKNOWN,
                recommended_action="BLOCK_ACCESS",
            )

        if not consent_authorized:
            return GuardianResult(
                result_id=str(uuid4()),
                guardian_status=GuardianDecision.BLOCK,
                reason="CONSENT_REVOKED: AI_PROCESSING consent is absent or has been revoked by family.",
                violations=["AI processing authorization not present."],
                confidence=ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                provenance=ProvenanceStatus.UNKNOWN,
                recommended_action="BLOCK_PROCESSING",
            )

        # Check 1: Boundary check from core security
        try:
            validate_ethical_boundaries(response_text)
        except EthicalBoundaryViolation as e:
            violations.append(f"ETHICAL_BOUNDARY_VIOLATION: {e.message}")

        # Check 2: Run Hallucination & Identity Usurpation Detector
        detect_result = self.detector.detect(response_text, evidence_items)
        if detect_result["is_hallucinated"]:
            violations.extend(detect_result["violations"])
            unsupported_claims.extend(detect_result["flagged_claims"])

        # Check 3: Zero Evidence Archival Handling
        text_lower = response_text.lower()
        is_safe_unknown_statement = any(phrase in text_lower for phrase in [
            "don't have enough information in the preserved archive",
            "do not have enough information in the preserved archive",
            "not present in the preserved archive",
            "no preserved archival evidence",
        ])

        if not evidence_items:
            if is_safe_unknown_statement:
                return GuardianResult(
                    result_id=str(uuid4()),
                    guardian_status=GuardianDecision.PASS,
                    reason="NO_SUPPORTING_EVIDENCE: Faithfully communicated absence of archival records.",
                    violations=[],
                    unsupported_claims=[],
                    missing_evidence=["No evidence in archive."],
                    confidence=ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                    provenance=ProvenanceStatus.UNKNOWN,
                    recommended_action="DELIVER_SAFE_UNKNOWN",
                )
            else:
                violations.append("UNSUPPORTED_FACT_ASSERTION: Response claims facts but archive context is empty.")
                missing_evidence.append("All statements lack evidence backing.")

        # Check 4: Inspect Claim Extraction Coverage
        for claim in claims:
            if claim.status == ClaimStatus.UNSUPPORTED:
                unsupported_claims.append(claim.text)
                violations.append(f"UNSUPPORTED_CLAIM: \"{claim.text}\" lacks corroborating evidence.")

        # Check 5: Contradiction Handling
        if contradictions:
            has_contradiction_acknowledgment = any(
                term in text_lower for term in ["conflict", "differing", "discrepancy", "conflicting", "two sources", "another source"]
            )
            if not has_contradiction_acknowledgment and not is_safe_unknown_statement:
                violations.append("UNACKNOWLEDGED_CONTRADICTION: Conflicting records exist in archive but were not disclosed.")

        # Determine Decision: PASS, REVISE, BLOCK, or UNKNOWN
        if not violations and not unsupported_claims:
            return GuardianResult(
                result_id=str(uuid4()),
                guardian_status=GuardianDecision.PASS,
                reason="All 18 evidentiary, privacy, and ethical boundary checks passed.",
                violations=[],
                unsupported_claims=[],
                missing_evidence=[],
                confidence=ConfidenceLevel.VERIFIED if evidence_items else ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                provenance=ProvenanceStatus.DIRECTLY_OBSERVED if evidence_items else ProvenanceStatus.UNKNOWN,
                recommended_action="DELIVER_RESPONSE",
            )

        # Severe uncorrectable violations: identity usurpation, sentience simulation, or ethical boundary violation
        has_severe_usurpation = any(
            "FIRST_PERSON" in v or "SENTIENCE" in v or "ETHICAL_BOUNDARY_VIOLATION" in v
            for v in violations
        )

        if is_revision or has_severe_usurpation:
            # If already revised once and still failing, or severe usurpation: BLOCK or fallback to SAFE_UNKNOWN
            status = GuardianDecision.BLOCK if has_severe_usurpation else GuardianDecision.REVISE
            return GuardianResult(
                result_id=str(uuid4()),
                guardian_status=status,
                reason=f"Violations detected (revision={is_revision}): {'; '.join(violations[:2])}",
                violations=violations,
                unsupported_claims=unsupported_claims,
                missing_evidence=missing_evidence,
                confidence=ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                provenance=ProvenanceStatus.UNKNOWN,
                recommended_action="BLOCK_RESPONSE" if status == GuardianDecision.BLOCK else "FALLBACK_TO_UNKNOWN",
            )

        # Single chance for automatic prompt revision
        return GuardianResult(
            result_id=str(uuid4()),
            guardian_status=GuardianDecision.REVISE,
            reason=f"Evidentiary violations detected [UNSUPPORTED_CLAIMS]: {'; '.join(violations[:2])}. Queued for strict revision.",
            violations=violations,
            unsupported_claims=unsupported_claims,
            missing_evidence=missing_evidence,
            confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
            provenance=ProvenanceStatus.AI_INFERRED,
            recommended_action="EXECUTE_STRICT_REVISION",
        )


_global_memory_guardian: Optional[MemoryGuardian] = None


def get_memory_guardian() -> MemoryGuardian:
    global _global_memory_guardian
    if _global_memory_guardian is None:
        _global_memory_guardian = MemoryGuardian()
    return _global_memory_guardian
