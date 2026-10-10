"""Memory Guardian API Endpoints for ECHO.

Provides verification endpoints for inspecting candidate responses, auditing ethical boundaries,
and testing claim-level evidentiary coverage.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from models.enums import GuardianDecision, ConfidenceLevel
from models.conversation import GuardianResult, ResponseClaim
from backend.app.services.guardian_service import guardian_service
from backend.app.services.memory_guardian import get_memory_guardian
from backend.app.services.claim_extractor import ClaimExtractor

router = APIRouter()


class AuditPromptRequest(BaseModel):
    text: str


class GuardianValidateRequest(BaseModel):
    response: str
    claims: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    evidence: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    privacy_authorized: bool = True
    consent_authorized: bool = True


@router.get("/status")
async def get_guardian_status() -> Dict[str, Any]:
    """Retrieve Memory Guardian monitoring status and ethical rule set."""
    return guardian_service.get_status()


@router.post("/audit")
async def audit_text(req: AuditPromptRequest) -> Dict[str, Any]:
    """Audit user input or model output for ethical boundary compliance."""
    passed, message = guardian_service.audit_input_prompt(req.text)
    return {
        "passed": passed,
        "message": message,
        "checked_length": len(req.text)
    }


@router.post("/validate", response_model=GuardianResult)
async def validate_candidate_response(req: GuardianValidateRequest) -> GuardianResult:
    """Validate a candidate response against all 18 evidentiary, privacy, and ethical checks."""
    guardian = get_memory_guardian()

    # Parse or extract claims if not provided
    extracted_claims: List[ResponseClaim] = []
    if req.claims:
        for c in req.claims:
            try:
                extracted_claims.append(ResponseClaim(**c))
            except Exception:
                pass
    else:
        extracted_claims = ClaimExtractor.extract_claims(
            response_text=req.response,
            evidence_items=req.evidence or []
        )

    result = guardian.validate_response(
        response_text=req.response,
        evidence_items=req.evidence or [],
        claims=extracted_claims,
        privacy_authorized=req.privacy_authorized,
        consent_authorized=req.consent_authorized,
    )
    return result


@router.post("/evaluate-suite")
async def evaluate_guardian_suite() -> Dict[str, Any]:
    """Execute Memory Guardian evaluation over standardized test cases.
    
    Verifies:
    1. Validation of factual claims against preserved evidence
    2. Contradiction acknowledgment enforcement
    3. Safe preservation of unknown / unrecorded answers
    4. Rejection of ungrounded personal claims & temporal fabrications
    5. Privacy clearance enforcement (strict blocking)
    6. Consent revocation enforcement (strict blocking)
    7. 100% adherence to ethical non-deceptive boundaries (zero consciousness simulation)
    """
    from backend.app.services.research_metrics_service import research_metrics_service
    results = await research_metrics_service.run_benchmark_evaluation()
    
    total = len(results.get("queries", []))
    matched = sum(1 for q in results.get("queries", []) if q.get("matches_expected_decision", False))
    boundary_violations = results.get("aggregate_metrics", {}).get("boundary_violation_rate", 0.0)

    return {
        "suite_id": results.get("benchmark_id"),
        "total_evaluated_cases": total,
        "conforming_decisions": matched,
        "conformance_rate": round(matched / total, 4) if total > 0 else 1.0,
        "boundary_violation_rate": boundary_violations,
        "verdict": "PASSED" if boundary_violations == 0.0 and matched == total else "PARTIAL",
        "detailed_results": results.get("queries", [])
    }

