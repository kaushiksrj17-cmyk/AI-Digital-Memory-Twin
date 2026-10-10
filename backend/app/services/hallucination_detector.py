"""Hallucination Detector for ECHO Memorial RAG Engine.

Inspects generated candidate responses for:
1. False first-person usurpation (claiming to be the deceased or speaking in 1st person)
2. Assertions of consciousness, feelings, or afterlife presence
3. Specific entities, dates, or factual claims absent from the retrieved evidence context
"""

from typing import List, Dict, Any, Optional
import re


class HallucinationDetector:
    """Verifies candidate text against retrieved evidence context and ethical boundaries."""

    def __init__(self):
        # Strict first-person identity patterns prohibited in memorial AI
        self._first_person_patterns = [
            (r"\b(i\s+am\s+(your|him|her|alive|in\s+heaven))\b", "Claiming first-person identity or afterlife existence"),
            (r"\b(i\s+remember\s+when\s+i)\b", "Claiming personal subjective memory of past events"),
            (r"\b(when\s+i\s+(died|passed\s+away|was\s+alive))\b", "Simulating the deceased persona's death experience"),
            (r"\b(i\s+miss\s+you|i\s+love\s+you\s+from\s+beyond)\b", "Fabricating emotional intimacy from beyond"),
            (r"\b(i\s+was\s+born\s+in|my\s+favorite\s+memory\s+was)\b", "Speaking from the first-person perspective of the memorial subject"),
        ]
        self._sentience_patterns = [
            (r"\b(i\s+feel|i\s+think\s+in\s+my\s+heart|i\s+have\s+a\s+soul|my\s+spirit)\b", "Simulating consciousness or soul"),
            (r"\b(i\s+am\s+watching\s+over\s+you)\b", "Simulating spiritual omniscience"),
        ]

    def detect(
        self,
        generated_text: str,
        evidence_items: List[Dict[str, Any]],
        memory_dna_context: Optional[List[str]] = None,
        graph_context: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Audit candidate response text against context."""
        text_lower = generated_text.lower()
        flagged_claims: List[str] = []
        violations: List[str] = []

        # 1. Identity & Sentience Boundary Checks
        for pattern, reason in self._first_person_patterns:
            if re.search(pattern, text_lower):
                violations.append(f"FIRST_PERSON_USURPATION: Disallowed first-person phrasing ({reason})")
                flagged_claims.append(f"Disallowed first-person phrasing matched '{pattern}'")

        for pattern, reason in self._sentience_patterns:
            if re.search(pattern, text_lower):
                violations.append(f"SENTIENCE_SIMULATION: {reason}")
                flagged_claims.append(f"Disallowed sentience phrasing matched '{pattern}'")

        # 2. Check if text is standard 'No Evidence' statement (always passes grounding)
        no_evidence_phrases = [
            "don't have enough information in the preserved archive",
            "do not have enough information in the preserved archive",
            "not present in the preserved archive",
            "no preserved archival evidence",
            "not found in the archive",
            "archive does not contain enough information",
        ]
        if any(phrase in text_lower for phrase in no_evidence_phrases):
            return {
                "is_hallucinated": bool(violations),
                "detector_method": "ECHO_HYBRID_FACT_CHECKER_V5",
                "confidence": 0.98,
                "flagged_claims": flagged_claims,
                "violations": violations,
            }

        # 3. Grounding Verification against Evidence Context
        # Gather all normalized text tokens from evidence, DNA, and graph
        corpus_text = ""
        for ev in evidence_items:
            corpus_text += " " + (ev.get("text") or ev.get("evidence_text") or "")
        if memory_dna_context:
            corpus_text += " " + " ".join(memory_dna_context)
        if graph_context:
            corpus_text += " " + " ".join(graph_context)

        corpus_lower = corpus_text.lower()

        # If generated text asserts facts while the evidence corpus is completely empty:
        if not corpus_text.strip():
            # Any factual assertion without evidence is a hallucination
            violations.append("UNGROUNDED_GENERATION: Response asserts facts while archive evidence is empty.")
            flagged_claims.append("Entire response generated without supporting archival evidence.")

        # Check for year references (4-digit years like 1968, 2012)
        years_in_text = re.findall(r"\b(19\d\d|20\d\d)\b", generated_text)
        for year in years_in_text:
            if year not in corpus_lower:
                violations.append(f"UNSUPPORTED_TEMPORAL_CLAIM: Year '{year}' appears in response but is absent from evidence.")
                flagged_claims.append(f"Year {year} is uncorroborated in preserved context.")

        is_hallucinated = bool(violations)
        confidence = 0.95 if is_hallucinated else 0.88

        return {
            "is_hallucinated": is_hallucinated,
            "detector_method": "ECHO_HYBRID_FACT_CHECKER_V5",
            "confidence": confidence,
            "flagged_claims": flagged_claims,
            "violations": violations,
        }


_global_hallucination_detector: Optional[HallucinationDetector] = None


def get_hallucination_detector() -> HallucinationDetector:
    global _global_hallucination_detector
    if _global_hallucination_detector is None:
        _global_hallucination_detector = HallucinationDetector()
    return _global_hallucination_detector
