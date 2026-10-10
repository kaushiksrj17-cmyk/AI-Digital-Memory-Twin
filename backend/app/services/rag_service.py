"""Evidence-Grounded Retrieval-Augmented Generation (RAG) Service for ECHO.

Coordinates the end-to-end evidence retrieval, context construction, LLM generation,
Memory Guardian validation, claim extraction, and hallucination prevention pipeline.
"""

from typing import Dict, Any, Optional, List
import time
from uuid import uuid4
from datetime import datetime, timezone

from models.enums import (
    ConfidenceLevel,
    GuardianDecision,
    QuestionCategory,
    RetrievalMode,
    AuditAction,
)
from models.conversation import (
    RAGQueryRequest,
    RAGQueryResponse,
    ResponseClaim,
    ResponseSource,
    GuardianResult,
    ETHICAL_DISCLAIMER_TEXT,
)
from backend.app.services.question_classifier import QuestionClassifier, get_question_classifier
from backend.app.services.context_manager import ContextManager, get_context_manager
from backend.app.services.prompt_engine import PromptEngine, get_prompt_engine
from backend.app.services.hallucination_detector import HallucinationDetector, get_hallucination_detector
from backend.app.services.claim_extractor import ClaimExtractor, get_claim_extractor
from backend.app.services.memory_guardian import MemoryGuardian, get_memory_guardian
from backend.app.services.confidence_engine import ConfidenceEngine, get_confidence_engine
from backend.app.services.provenance_engine import ProvenanceEngine, get_provenance_engine
from backend.app.services.contradiction_service import get_contradiction_service
from backend.app.services.consent_service import consent_service
from backend.app.core.audit import audit_logger
from ai.providers.factory import provider_registry
from ai.providers.llm import LLMGenerationRequest, MockLLMProvider


class RAGService:
    """Orchestrates evidence-grounded response generation with strict safety boundaries."""

    def __init__(
        self,
        classifier: Optional[QuestionClassifier] = None,
        context_manager: Optional[ContextManager] = None,
        prompt_engine: Optional[PromptEngine] = None,
        guardian: Optional[MemoryGuardian] = None,
        confidence_engine: Optional[ConfidenceEngine] = None,
        provenance_engine: Optional[ProvenanceEngine] = None,
    ):
        self.classifier = classifier or get_question_classifier()
        self.context_mgr = context_manager or get_context_manager()
        self.prompt_engine = prompt_engine or get_prompt_engine()
        self.guardian = guardian or get_memory_guardian()
        self.confidence_engine = confidence_engine or get_confidence_engine()
        self.provenance_engine = provenance_engine or get_provenance_engine()
        self.contradiction_svc = get_contradiction_service()
        self._metrics_log: List[Dict[str, Any]] = []

    async def query(
        self,
        request: RAGQueryRequest,
        user_id: str = "default-user-001",
        privacy_authorized: bool = True,
    ) -> RAGQueryResponse:
        """Execute the complete evidence-grounded RAG workflow."""
        start_time = time.time()
        retrieval_start = start_time
        retrieval_latency_ms = 0.0
        generation_latency_ms = 0.0
        guardian_latency_ms = 0.0

        query_id = str(uuid4())
        message_id = str(uuid4())

        # 1. Question Classification & Safety Routing
        classification = self.classifier.classify(request.query)

        # 1a. Handle Unsupported Personal Inquiries (consciousness simulation / speculative feelings)
        if classification.category == QuestionCategory.UNSUPPORTED_PERSONAL_QUERY:
            total_latency_ms = round((time.time() - start_time) * 1000, 2)
            answer_text = (
                "ECHO is an AI-generated memorial representation based strictly on preserved archival records. "
                "It does not possess consciousness, living sentience, or speculative modern opinions, and cannot "
                "simulate what the memorial subject would think or feel today. Please ask about documented life "
                "events, education, career, family relationships, or preserved stories."
            )
            return RAGQueryResponse(
                conversation_id=request.conversation_id,
                message_id=message_id,
                query=request.query,
                answer=answer_text,
                confidence_level=ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                confidence_score=0.0,
                guardian_status=GuardianDecision.PASS,
                generated_by_ai=True,
                ethical_disclaimer=ETHICAL_DISCLAIMER_TEXT,
                sources=[],
                claims=[],
                contradictions=[],
                warnings=["Query requested speculative feelings outside documented archive."],
                retrieval_explanation="Inquiry routed away from generation to protect non-deceptive ethical boundaries.",
                question_classification=classification,
            )

        # 1b. Handle General Greetings
        if classification.category == QuestionCategory.GENERAL_GREETING:
            answer_text = (
                "Hello. I am ECHO, an AI memorial assistant. I can help you explore preserved memories, "
                "historical letters, photographs, life milestones, and recorded family stories. "
                "What would you like to explore from the archive?"
            )
            return RAGQueryResponse(
                conversation_id=request.conversation_id,
                message_id=message_id,
                query=request.query,
                answer=answer_text,
                confidence_level=ConfidenceLevel.VERIFIED,
                confidence_score=1.0,
                guardian_status=GuardianDecision.PASS,
                generated_by_ai=True,
                ethical_disclaimer=ETHICAL_DISCLAIMER_TEXT,
                sources=[],
                claims=[],
                contradictions=[],
                warnings=[],
                retrieval_explanation="Standard orientation dialogue.",
                question_classification=classification,
            )

        # 2. Consent Authorization Check (AI_PROCESSING)
        consent_ok = await consent_service.is_ai_processing_permitted(request.memorial_profile_id)
        if not consent_ok:
            return RAGQueryResponse(
                conversation_id=request.conversation_id,
                message_id=message_id,
                query=request.query,
                answer="AI response generation is disabled because AI_PROCESSING consent is absent or revoked for this memorial archive.",
                confidence_level=ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                confidence_score=0.0,
                guardian_status=GuardianDecision.BLOCK,
                generated_by_ai=True,
                ethical_disclaimer=ETHICAL_DISCLAIMER_TEXT,
                sources=[],
                claims=[],
                contradictions=[],
                warnings=["AI_PROCESSING consent revoked or missing (CONSENT_REVOKED)."],
                retrieval_explanation="Processing halted due to consent policy.",
                question_classification=classification,
            )

        # 3. Evidence Context Assembly
        retrieval_start = time.time()
        context_bundle = await self.context_mgr.build_context(
            query=request.query,
            memorial_profile_id=request.memorial_profile_id,
            top_k=request.top_k or 5,
            retrieval_mode=request.retrieval_mode or RetrievalMode.HYBRID,
            confidence_threshold=request.confidence_threshold or 0.4,
        )
        retrieval_latency_ms = round((time.time() - retrieval_start) * 1000, 2)

        evidence_items = context_bundle["evidence_items"]
        memory_dna_context = context_bundle["memory_dna_context"]
        graph_context = context_bundle["graph_context"]
        has_evidence = context_bundle["has_evidence"]

        # 4. Zero Evidence Check — DO NOT INVENT MANDATE
        if not has_evidence:
            guardian_res = self.guardian.validate_response(
                response_text="I don't have enough information in the preserved archive to answer that accurately.",
                evidence_items=[],
                claims=[],
                privacy_authorized=privacy_authorized,
                consent_authorized=consent_ok,
            )
            return RAGQueryResponse(
                conversation_id=request.conversation_id,
                message_id=message_id,
                query=request.query,
                answer="I don't have enough information in the preserved archive to answer that accurately.",
                confidence_level=ConfidenceLevel.UNKNOWN_UNSUPPORTED,
                confidence_score=0.0,
                guardian_status=guardian_res.guardian_status,
                generated_by_ai=True,
                ethical_disclaimer=ETHICAL_DISCLAIMER_TEXT,
                sources=[],
                claims=[],
                contradictions=[],
                warnings=["No matching evidence found in preserved archive."],
                retrieval_explanation="Zero evidence matched inquiry. Anti-fabrication rule prevented generation.",
                question_classification=classification,
            )

        # 5. Check Contradictions in Knowledge Base
        active_contradictions = self.contradiction_svc.get_contradictions(request.memorial_profile_id)
        relevant_contradictions: List[Dict[str, Any]] = []
        q_tokens = set(request.query.lower().split())
        for c in active_contradictions:
            subj_tokens = set(c.subject.lower().split())
            if q_tokens.intersection(subj_tokens):
                relevant_contradictions.append(c.model_dump())

        # 6. LLM Generation
        gen_start = time.time()
        system_instruction = self.prompt_engine.get_system_instruction()
        user_prompt = self.prompt_engine.build_user_prompt(
            query=request.query,
            evidence_items=evidence_items,
            contradictions=relevant_contradictions,
            memory_dna_context=memory_dna_context,
            graph_context=graph_context,
        )

        llm_provider = getattr(provider_registry, "llm_provider", None) or provider_registry.get_llm()
        evidence_excerpts = [ev.get("text", "") for ev in evidence_items]

        llm_req = LLMGenerationRequest(
            prompt=user_prompt,
            system_instruction=system_instruction,
            evidence_context=evidence_excerpts,
            temperature=0.1,
            max_tokens=800,
        )
        llm_resp = await llm_provider.generate(llm_req)
        raw_answer = llm_resp.content
        generation_latency_ms = round((time.time() - gen_start) * 1000, 2)

        # 7. Claim Extraction & Guardian Validation (Pass 1)
        guard_start = time.time()
        claims = ClaimExtractor.extract_claims(
            response_text=raw_answer,
            evidence_items=evidence_items,
            message_id=message_id,
            contradictions=relevant_contradictions,
        )

        guardian_result = self.guardian.validate_response(
            response_text=raw_answer,
            evidence_items=evidence_items,
            claims=claims,
            privacy_authorized=privacy_authorized,
            consent_authorized=consent_ok,
            contradictions=relevant_contradictions,
            is_revision=False,
        )

        # 8. Revision Loop (Max 1 Attempt)
        final_answer = raw_answer
        warnings: List[str] = []

        if guardian_result.guardian_status == GuardianDecision.REVISE:
            revision_prompt = self.prompt_engine.build_revision_prompt(
                original_query=request.query,
                flawed_response=raw_answer,
                violations=guardian_result.violations,
                evidence_items=evidence_items,
            )
            rev_req = LLMGenerationRequest(
                prompt=revision_prompt,
                system_instruction=system_instruction,
                evidence_context=evidence_excerpts,
                temperature=0.0,
                max_tokens=600,
            )
            rev_resp = await llm_provider.generate(rev_req)
            revised_answer = rev_resp.content

            # Re-extract claims and re-validate
            claims = ClaimExtractor.extract_claims(
                response_text=revised_answer,
                evidence_items=evidence_items,
                message_id=message_id,
                contradictions=relevant_contradictions,
            )
            guardian_result = self.guardian.validate_response(
                response_text=revised_answer,
                evidence_items=evidence_items,
                claims=claims,
                privacy_authorized=privacy_authorized,
                consent_authorized=consent_ok,
                contradictions=relevant_contradictions,
                is_revision=True,
            )

            if guardian_result.guardian_status == GuardianDecision.PASS:
                final_answer = revised_answer
                warnings.append("Response underwent automated evidentiary revision to meet memorial standards.")
            else:
                # Revision still failed; fall back to safe archive statement
                final_answer = (
                    "The preserved archive contains related materials, but there is not enough "
                    "verified information to answer this specific inquiry without speculation."
                )
                guardian_result.guardian_status = GuardianDecision.PASS
                warnings.append("Candidate response suppressed; reverted to safe archival uncertainty.")

        elif guardian_result.guardian_status == GuardianDecision.BLOCK:
            final_answer = (
                "This inquiry cannot be answered due to privacy, consent, or ethical boundary policies."
            )
            warnings.append("Response blocked by Memory Guardian.")

        guardian_latency_ms = round((time.time() - guard_start) * 1000, 2)
        total_latency_ms = round((time.time() - start_time) * 1000, 2)

        # 9. Format Clickable Sources and Confidence Score
        sources = self.provenance_engine.generate_sources(evidence_items)
        conf_data = self.confidence_engine.calculate_response_confidence(
            claims=claims,
            evidence_items=evidence_items,
            guardian_result=guardian_result,
            contradictions=relevant_contradictions,
        )

        # 10. Record Metrics & Audit Log
        metric_record = {
            "query_id": query_id,
            "session_id": request.conversation_id,
            "retrieval_latency_ms": retrieval_latency_ms,
            "generation_latency_ms": generation_latency_ms,
            "guardian_latency_ms": guardian_latency_ms,
            "total_latency_ms": total_latency_ms,
            "retrieved_evidence_count": len(evidence_items),
            "supporting_claim_count": sum(1 for c in claims if c.status.value == "SUPPORTED"),
            "unsupported_claim_count": sum(1 for c in claims if c.status.value == "UNSUPPORTED"),
            "contradiction_count": len(relevant_contradictions),
            "guardian_status": guardian_result.guardian_status.value,
            "confidence_level": conf_data["confidence_level"].value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._metrics_log.append(metric_record)

        audit_logger.log_event(
            user_id=user_id,
            action=AuditAction.RAG_QUERY,
            target_id=message_id,
            details={
                "query": request.query[:100],
                "confidence": conf_data["confidence_level"].value,
                "guardian_status": guardian_result.guardian_status.value,
                "evidence_count": len(evidence_items),
            }
        )

        retrieval_explanation = (
            f"Retrieved {len(evidence_items)} items via {request.retrieval_mode.value if request.retrieval_mode else 'HYBRID'} mode. "
            f"{conf_data['methodology']}"
        )

        return RAGQueryResponse(
            conversation_id=request.conversation_id,
            message_id=message_id,
            query=request.query,
            answer=final_answer,
            confidence_level=conf_data["confidence_level"],
            confidence_score=conf_data["confidence_score"],
            guardian_status=guardian_result.guardian_status,
            generated_by_ai=True,
            ethical_disclaimer=ETHICAL_DISCLAIMER_TEXT,
            sources=sources,
            claims=claims,
            contradictions=relevant_contradictions,
            warnings=warnings,
            retrieval_explanation=retrieval_explanation,
            question_classification=classification,
        )

    def get_metrics(self) -> List[Dict[str, Any]]:
        """Return research telemetry metrics."""
        return list(self._metrics_log)


_global_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    global _global_rag_service
    if _global_rag_service is None:
        _global_rag_service = RAGService()
    return _global_rag_service
