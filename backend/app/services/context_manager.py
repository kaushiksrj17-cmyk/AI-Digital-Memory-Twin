"""Context Manager for Evidence-Grounded Conversational Memorial AI.

Assembles, ranks, deduplicates, and controls context windows from:
1. Retrieval Service (Vector + Keyword + Graph items)
2. Memory DNA (Categorized structured biographical facts)
3. Knowledge Graph (Entity neighborhoods & verified relations)
4. Memory Vault (Document metadata and primary narratives)
"""

from typing import List, Dict, Any, Optional
import hashlib

from models.enums import ConfidenceLevel, ProvenanceStatus, RetrievalMode
from models.retrieval import RetrievalQuery
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.memory_dna_service import get_memory_dna_service
from backend.app.services.knowledge_graph_service import KnowledgeGraphService


class ContextManager:
    """Orchestrates structured context compilation for LLM generation."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        graph_service: Optional[KnowledgeGraphService] = None,
        max_evidence_count: int = 5,
        max_character_budget: int = 4000,
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.dna_service = get_memory_dna_service()
        self.graph_service = graph_service or KnowledgeGraphService()
        self.max_evidence_count = max_evidence_count
        self.max_character_budget = max_character_budget

    def build_context_from_raw(
        self,
        retrieval_results: Optional[Dict[str, Any]] = None,
        dna_items: Optional[List[Dict[str, Any]]] = None,
        graph_context: Optional[List[Any]] = None,
    ):
        """Synchronously format raw components into a bounded context string and evidence list."""
        items = []
        context_parts = []
        raw_res = (retrieval_results or {}).get("results", [])
        seen_texts = set()
        total_chars = 0

        for r in raw_res:
            content = r.get("content") or r.get("text", "")
            if content in seen_texts:
                continue
            seen_texts.add(content)
            if len(items) >= self.max_evidence_count or total_chars + len(content) > self.max_character_budget:
                break
            items.append(r)
            total_chars += len(content)
            context_parts.append(f"Evidence Excerpt: {content}")

        if dna_items:
            context_parts.append("\n[DNA Core Attributes]:")
            for d in dna_items:
                context_parts.append(f"- {d.get('key')}: {d.get('value')}")

        if graph_context:
            context_parts.append("\n[Knowledge Graph Context]:")
            for g in graph_context:
                if isinstance(g, dict):
                    context_parts.append(f"- {g.get('subject')} {g.get('predicate')} {g.get('object')}")
                else:
                    context_parts.append(f"- {str(g)}")

        return "\n".join(context_parts), items

    def build_context(
        self,
        query: Optional[str] = None,
        memorial_profile_id: Optional[str] = None,
        top_k: int = 5,
        retrieval_mode: RetrievalMode = RetrievalMode.HYBRID,
        confidence_threshold: float = 0.4,
        max_total_chars: int = 4000,
        retrieval_results: Optional[Dict[str, Any]] = None,
        dna_items: Optional[List[Dict[str, Any]]] = None,
        graph_context: Optional[List[Any]] = None,
    ):
        if retrieval_results is not None:
            return self.build_context_from_raw(retrieval_results, dna_items, graph_context)
        return self._build_context_async(
            query=query or "",
            memorial_profile_id=memorial_profile_id or "default-profile-001",
            top_k=top_k,
            retrieval_mode=retrieval_mode,
            confidence_threshold=confidence_threshold,
            max_total_chars=max_total_chars,
        )

    async def _build_context_async(
        self,
        query: str,
        memorial_profile_id: str,
        top_k: int = 5,
        retrieval_mode: RetrievalMode = RetrievalMode.HYBRID,
        confidence_threshold: float = 0.4,
        max_total_chars: int = 4000,
    ) -> Dict[str, Any]:
        """Compile a deduplicated, privacy-checked context bundle for a query."""
        # 1. Execute Multi-strategy Evidence Retrieval
        retrieval_q = RetrievalQuery(
            query=query,
            memorial_profile_id=memorial_profile_id,
            top_k=top_k,
            retrieval_mode=retrieval_mode,
            confidence_threshold=confidence_threshold,
        )
        retrieval_resp = await self.retrieval_service.search(retrieval_q)

        evidence_items: List[Dict[str, Any]] = []
        seen_texts = set()
        accumulated_chars = 0

        # Filter and prioritize retrieval results
        for item in retrieval_resp.results:
            # Skip UNKNOWN items from serving as factual premises
            if item.confidence == ConfidenceLevel.UNKNOWN_UNSUPPORTED:
                continue

            clean_text = item.text.strip()
            text_hash = hashlib.sha256(clean_text.lower().encode("utf-8")).hexdigest()
            if text_hash in seen_texts:
                continue
            seen_texts.add(text_hash)

            item_len = len(clean_text)
            if accumulated_chars + item_len > max_total_chars:
                break

            accumulated_chars += item_len
            evidence_items.append({
                "result_id": item.result_id,
                "evidence_id": item.evidence_id,
                "memory_id": item.memory_id,
                "media_id": item.media_id,
                "chunk_id": item.chunk_id,
                "text": clean_text,
                "source_reference": item.source_reference,
                "provenance_status": item.provenance_status.value if hasattr(item.provenance_status, "value") else str(item.provenance_status),
                "confidence": item.confidence.value if hasattr(item.confidence, "value") else str(item.confidence),
                "score": item.score,
                "why_retrieved": item.why_retrieved,
                "score_breakdown": getattr(item, "score_breakdown", getattr(item, "score_components", {})),
            })

        # 2. Extract Relevant Memory DNA Items
        memory_dna_context: List[str] = []
        try:
            profile_dna = await self.dna_service.get_dna(memorial_profile_id)
            if profile_dna and profile_dna.items:
                q_lower = query.lower()
                for dna_item in profile_dna.items:
                    # Match DNA item by category, key, or value mention
                    val_str = str(dna_item.value).lower()
                    key_str = dna_item.key.lower()
                    cat_str = dna_item.category.value.lower() if hasattr(dna_item.category, "value") else str(dna_item.category).lower()

                    if any(term in q_lower for term in [key_str, val_str, cat_str]) or any(token in q_lower.split() for token in val_str.split()):
                        if dna_item.confidence != ConfidenceLevel.UNKNOWN_UNSUPPORTED:
                            memory_dna_context.append(
                                f"{dna_item.category}: {dna_item.key} = '{dna_item.value}' "
                                f"({dna_item.description or 'Documented in archive'}) [{dna_item.confidence}]"
                            )
                            if len(memory_dna_context) >= 5:
                                break
        except Exception:
            pass

        # 3. Extract Relevant Knowledge Graph Relationships
        graph_context: List[str] = []
        try:
            graph_results = await self.graph_service.search_graph(query, memorial_profile_id=memorial_profile_id)
            for edge in graph_results.relationships[:5]:
                src_node = await self.graph_service.get_node(edge.source_node)
                tgt_node = await self.graph_service.get_node(edge.target_node)
                src_name = src_node.label if src_node else edge.source_node
                tgt_name = tgt_node.label if tgt_node else edge.target_node
                graph_context.append(
                    f"{src_name} --[{edge.relationship_type}]--> {tgt_name} "
                    f"(Confidence: {edge.confidence})"
                )
        except Exception:
            pass

        has_evidence = bool(evidence_items or memory_dna_context or graph_context)

        return {
            "query": query,
            "memorial_profile_id": memorial_profile_id,
            "evidence_items": evidence_items,
            "memory_dna_context": memory_dna_context,
            "graph_context": graph_context,
            "retrieval_response": retrieval_resp,
            "has_evidence": has_evidence,
            "total_evidence_count": len(evidence_items) + len(memory_dna_context) + len(graph_context),
        }


_global_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    global _global_context_manager
    if _global_context_manager is None:
        _global_context_manager = ContextManager()
    return _global_context_manager
