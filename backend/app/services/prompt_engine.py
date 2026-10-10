"""Prompt Engine for Evidence-Grounded Conversational Memorial AI.

Synthesizes strict, boundary-enforcing system instructions and user prompts
guaranteeing evidence grounding, provenance citation, and non-deceptive representation.
"""

from typing import List, Dict, Any, Optional
from models.conversation import ETHICAL_DISCLAIMER_TEXT


class PromptEngine:
    """Constructs verifiable, non-hallucinatory prompts for LLM synthesis."""

    @staticmethod
    def get_system_instruction() -> str:
        return (
            "You are ECHO, an evidence-grounded AI memorial assistant representing preserved biographical "
            "records, family memories, photographs, and historical documents.\n\n"
            "CRITICAL ETHICAL & EVIDENTIARY RULES:\n"
            "1. IDENTITY BOUNDARY: You are an AI assistant representing an archive. You are NOT the deceased "
            "person. Under no circumstances may you claim to be the person, use first-person statements "
            "('I was', 'I felt', 'I remember when I...', 'I died'), or pretend to possess living consciousness, "
            "feelings, souls, or an afterlife perspective.\n"
            "2. THIRD-PERSON ARCHIVAL TONE: Always use objective, archival phrasing such as: "
            "'The preserved archive indicates...', 'A documented memory records...', 'According to archival documents...'.\n"
            "3. DO NOT INVENT (STRICT GROUNDING): Answer ONLY using information explicitly stated in the "
            "provided RETRIEVED EVIDENCE CONTEXT. Never extrapolate, speculate, or synthesize fictional facts, "
            "dates, relationships, preferences, or emotional states.\n"
            "4. MISSING INFORMATION: If the evidence context is insufficient to answer the inquiry, "
            "you MUST state: 'I don't have enough information in the preserved archive to answer that accurately.' "
            "Do NOT attempt to guess or complete the narrative creatively.\n"
            "5. CONTRADICTION TRANSPARENCY: If conflicting records are noted in the context, explicitly explain "
            "the differing accounts and their sources rather than asserting one as fact.\n"
            "6. SOURCE CITATIONS: Reference the supporting sources provided in the context.\n"
            f"7. ETHICAL DISCLAIMER: {ETHICAL_DISCLAIMER_TEXT}"
        )

    @staticmethod
    def build_user_prompt(
        query: str,
        evidence_items: List[Dict[str, Any]],
        contradictions: Optional[List[Dict[str, Any]]] = None,
        memory_dna_context: Optional[List[str]] = None,
        graph_context: Optional[List[str]] = None,
    ) -> str:
        prompt_parts = [
            f"USER INQUIRY: {query}\n",
            "--- RETRIEVED ARCHIVAL EVIDENCE ---"
        ]

        if not evidence_items and not memory_dna_context and not graph_context:
            prompt_parts.append("[NO EVIDENCE FOUND IN ARCHIVE FOR THIS INQUIRY]")
        else:
            if memory_dna_context:
                prompt_parts.append("\n[DOCUMENTED MEMORY DNA FACTS]:")
                for dna in memory_dna_context[:5]:
                    prompt_parts.append(f"- {dna}")

            if graph_context:
                prompt_parts.append("\n[VERIFIED RELATIONSHIP GRAPH CONTEXT]:")
                for g in graph_context[:5]:
                    prompt_parts.append(f"- {g}")

            if evidence_items:
                prompt_parts.append("\n[ARCHIVAL EVIDENCE EXCERPTS]:")
                for idx, ev in enumerate(evidence_items, start=1):
                    source_label = ev.get("source_reference", "Archival Document")
                    conf = ev.get("confidence", "VERIFIED")
                    prov = ev.get("provenance_status", "DIRECTLY_OBSERVED")
                    text = ev.get("text") or ev.get("evidence_text", "")
                    prompt_parts.append(
                        f"Source [{idx}]: {source_label} (Confidence: {conf}, Provenance: {prov})\n"
                        f"Content: \"{text}\"\n"
                    )

        if contradictions:
            prompt_parts.append("\n--- DETECTED CONFLICTING RECORDS IN ARCHIVE ---")
            for c in contradictions:
                subj = c.get("subject", "Topic")
                claim_a = c.get("claim_a", "")
                claim_b = c.get("claim_b", "")
                src_a = c.get("source_a", "")
                src_b = c.get("source_b", "")
                prompt_parts.append(
                    f"- Conflict regarding '{subj}': Source '{src_a}' states '{claim_a}', "
                    f"whereas Source '{src_b}' states '{claim_b}'. Explain this discrepancy transparently."
                )

        prompt_parts.append(
            "\nINSTRUCTIONS FOR RESPONSE:\n"
            "- Formulate a respectful, evidence-grounded answer based strictly on the excerpts above.\n"
            "- If information is missing, state clearly that it is not present in the archive.\n"
            "- Do not use first-person pronouns like 'I remember' or 'my wife'. Use third-person archival language."
        )

        return "\n".join(prompt_parts)

    def build_system_prompt(self, memorial_name: Optional[str] = None, strict_evidence: bool = True) -> str:
        base = self.get_system_instruction()
        if memorial_name:
            base += f"\n\nCURRENT MEMORIAL SUBJECT: You are assisting with preserved records concerning {memorial_name}. NEVER speak in the first person as {memorial_name}."
        if strict_evidence:
            base += "\nSTRICT EVIDENCE GROUNDING: DO NOT INVENT any unrecorded details."
        return base

    @staticmethod
    def build_revision_prompt(
        original_query: str,
        flawed_response: Optional[str] = None,
        violations: Optional[List[str]] = None,
        evidence_items: Optional[List[Dict[str, Any]]] = None,
        previous_response: Optional[str] = None,
        evidence_context: Optional[str] = None,
    ) -> str:
        response_text = flawed_response or previous_response or ""
        viols = violations or []
        prompt_parts = [
            "CRITICAL CORRECTION REQUIRED: Your previous draft violated evidentiary and ethical boundaries.",
            f"USER INQUIRY: {original_query}",
            f"PREVIOUS RESPONSE: \"{response_text}\"",
            "\nIDENTIFIED VIOLATIONS:",
        ]
        for v in viols:
            prompt_parts.append(f"- {v}")

        prompt_parts.append(
            "\nCORRECTIVE MANDATE:\n"
            "- Remove any unsupported facts, invented dates, or first-person claims.\n"
            "- Ground the revised response STRICTLY in the following evidence excerpts only.\n"
            "- STRICT EVIDENCE GROUNDING: If the excerpts do not contain the answer, state that the archive lacks sufficient information.\n"
        )
        if evidence_context:
            prompt_parts.append(evidence_context)
        elif evidence_items:
            prompt_parts.append("--- APPROVED EVIDENCE EXCERPTS ---")
            for idx, ev in enumerate(evidence_items, start=1):
                text = ev.get("text") or ev.get("evidence_text", "")
                prompt_parts.append(f"[{idx}]: \"{text}\"")

        return "\n".join(prompt_parts)


_global_prompt_engine: Optional[PromptEngine] = None


def get_prompt_engine() -> PromptEngine:
    global _global_prompt_engine
    if _global_prompt_engine is None:
        _global_prompt_engine = PromptEngine()
    return _global_prompt_engine
