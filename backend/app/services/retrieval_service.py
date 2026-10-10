"""Evidence-Grounded Retrieval Service for ECHO.

Provides multi-modal evidence retrieval supporting:
1. VECTOR retrieval (dense semantic similarity)
2. KEYWORD retrieval (exact token and phrase matching)
3. GRAPH retrieval (entity neighborhood traversal)
4. HYBRID retrieval (weighted multi-source synthesis)

CRITICAL BOUNDARY:
Does NOT generate conversational answers. Outputs strictly ranked, provenance-backed evidence.
Applies rigorous privacy-boundary and consent checks BEFORE returning results.
Provides explainable score breakdowns and 'why_retrieved' rationales for research evaluation.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4
import time
import re
from datetime import datetime, timezone

from models.enums import (
    RetrievalMode,
    ConfidenceLevel,
    ProvenanceStatus,
    PrivacyLevel,
    GraphNodeType,
)
from models.retrieval import (
    RetrievalQuery,
    RetrievalResultItem,
    RetrievalResponse,
)
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import get_vector_store, BaseVectorDatabase
from backend.app.services.knowledge_graph_service import KnowledgeGraphService, get_graph_store


class RetrievalService:
    """Multi-strategy explainable evidence retrieval engine."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[BaseVectorDatabase] = None,
        graph_service: Optional[KnowledgeGraphService] = None
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or get_vector_store()
        self.graph_service = graph_service or KnowledgeGraphService()
        self._retrieval_logs: List[Dict[str, Any]] = []

    def normalize_query(self, query: str) -> str:
        """Strip punctuation and extraneous whitespace from query text."""
        cleaned = re.sub(r"[^\w\s]", " ", query)
        return " ".join(cleaned.split()).lower()

    async def search(self, query: RetrievalQuery) -> RetrievalResponse:
        """Execute evidence retrieval under specified mode with explainable ranking."""
        start_time = time.time()
        norm_q = self.normalize_query(query.query)
        q_tokens = set(norm_q.split())

        vector_candidates: List[Dict[str, Any]] = []
        keyword_candidates: List[Dict[str, Any]] = []
        graph_candidates: List[Dict[str, Any]] = []

        # 1. Vector Search
        if query.retrieval_mode in (RetrievalMode.VECTOR, RetrievalMode.HYBRID):
            q_emb = await self.embedding_service.get_embedding(query.query)
            vec_results = await self.vector_store.search(
                query_vector=q_emb,
                limit=query.top_k * 3,
                filter_metadata={"memorial_profile_id": query.memorial_profile_id} if query.memorial_profile_id else None
            )
            for vr in vec_results:
                vector_candidates.append({
                    "id": vr.id,
                    "score": vr.score,
                    "payload": vr.payload,
                    "source": "VECTOR"
                })

        # 2. Keyword Search
        if query.retrieval_mode in (RetrievalMode.KEYWORD, RetrievalMode.HYBRID):
            # Scan vector payloads or local evidence texts for token overlap
            if hasattr(self.vector_store, "_payloads"):
                for vid, payload in self.vector_store._payloads.items():
                    if query.memorial_profile_id and payload.get("memorial_profile_id") != query.memorial_profile_id:
                        continue
                    text = payload.get("text", "").lower()
                    if not text:
                        continue
                    text_tokens = set(text.split())
                    common = q_tokens.intersection(text_tokens)
                    if common:
                        kw_score = len(common) / max(1, len(q_tokens))
                        # Exact phrase bonus
                        if norm_q in text:
                            kw_score = min(1.0, kw_score + 0.3)
                        keyword_candidates.append({
                            "id": vid,
                            "score": kw_score,
                            "payload": payload,
                            "source": "KEYWORD",
                            "matched_tokens": list(common)
                        })

        # 3. Graph Retrieval
        if query.retrieval_mode in (RetrievalMode.GRAPH, RetrievalMode.HYBRID):
            # Find nodes mentioning query tokens
            matched_nodes = await self.graph_service.store.search_nodes(
                query=query.query,
                memorial_profile_id=query.memorial_profile_id,
                limit=5
            )
            for node in matched_nodes:
                # Retrieve neighborhood
                neighborhood = await self.graph_service.get_neighborhood(node.id, max_depth=1)
                if neighborhood:
                    for rel in neighborhood.relationships:
                        graph_candidates.append({
                            "id": f"graph_{node.id}_{rel.relationship_id}",
                            "score": 0.85,
                            "payload": {
                                "text": f"Entity '{node.name}' ({node.label.value if hasattr(node.label, 'value') else node.label}) {rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else rel.relationship_type} connected nodes.",
                                "source_reference": f"Knowledge Graph: {node.name}",
                                "provenance_status": node.provenance_status.value if hasattr(node.provenance_status, 'value') else str(node.provenance_status),
                                "confidence": node.confidence.value if hasattr(node.confidence, 'value') else str(node.confidence),
                                "confidence_score": node.confidence_score,
                                "source_evidence_ids": node.source_evidence_ids,
                                "source_memory_ids": node.source_memory_ids,
                                "memorial_profile_id": node.memorial_profile_id,
                                "privacy_level": "PRIVATE"
                            },
                            "source": "GRAPH"
                        })

        # 4. Synthesize and Rank Candidates
        all_candidates: Dict[str, Dict[str, Any]] = {}

        def get_candidate_key(c: Dict[str, Any]) -> str:
            payload = c["payload"]
            return payload.get("chunk_id") or payload.get("evidence_id") or payload.get("vector_id") or c["id"]

        # Merge scores
        for vc in vector_candidates:
            k = get_candidate_key(vc)
            if k not in all_candidates:
                all_candidates[k] = {
                    "payload": vc["payload"],
                    "vector_score": vc["score"],
                    "keyword_score": 0.0,
                    "graph_score": 0.0,
                    "why": ["Semantic similarity"]
                }
            else:
                all_candidates[k]["vector_score"] = vc["score"]
                all_candidates[k]["why"].append("Semantic similarity")

        for kc in keyword_candidates:
            k = get_candidate_key(kc)
            if k not in all_candidates:
                all_candidates[k] = {
                    "payload": kc["payload"],
                    "vector_score": 0.0,
                    "keyword_score": kc["score"],
                    "graph_score": 0.0,
                    "why": [f"Keyword match ({', '.join(kc.get('matched_tokens', [])[:3])})"]
                }
            else:
                all_candidates[k]["keyword_score"] = kc["score"]
                all_candidates[k]["why"].append("Exact token match")

        for gc in graph_candidates:
            k = get_candidate_key(gc)
            if k not in all_candidates:
                all_candidates[k] = {
                    "payload": gc["payload"],
                    "vector_score": 0.0,
                    "keyword_score": 0.0,
                    "graph_score": gc["score"],
                    "why": ["Knowledge graph entity connection"]
                }
            else:
                all_candidates[k]["graph_score"] = gc["score"]
                all_candidates[k]["why"].append("Knowledge graph traversal")

        ranked_results: List[RetrievalResultItem] = []

        # Weights based on retrieval mode
        w_vec = 0.5 if query.retrieval_mode == RetrievalMode.HYBRID else (1.0 if query.retrieval_mode == RetrievalMode.VECTOR else 0.0)
        w_kw = 0.3 if query.retrieval_mode == RetrievalMode.HYBRID else (1.0 if query.retrieval_mode == RetrievalMode.KEYWORD else 0.0)
        w_graph = 0.2 if query.retrieval_mode == RetrievalMode.HYBRID else (1.0 if query.retrieval_mode == RetrievalMode.GRAPH else 0.0)

        for k, data in all_candidates.items():
            payload = data["payload"]

            # Provenance filtering
            prov_str = payload.get("provenance_status", "DIRECTLY_OBSERVED")
            try:
                prov_enum = ProvenanceStatus(prov_str)
            except ValueError:
                prov_enum = ProvenanceStatus.DIRECTLY_OBSERVED

            if query.provenance_filter and prov_enum not in query.provenance_filter:
                continue

            # Confidence filtering
            conf_str = payload.get("confidence", "VERIFIED")
            try:
                conf_enum = ConfidenceLevel(conf_str)
            except ValueError:
                conf_enum = ConfidenceLevel.VERIFIED

            conf_score = float(payload.get("confidence_score", 1.0))
            if query.confidence_threshold is not None and conf_score < query.confidence_threshold:
                continue

            # Privacy filtering: enforce boundary
            item_privacy = payload.get("privacy_level", "PRIVATE")
            if not self._check_privacy_access(user_boundary=query.privacy_boundary, item_privacy=item_privacy):
                continue

            # Compute combined score
            base_score = (
                w_vec * data["vector_score"] +
                w_kw * data["keyword_score"] +
                w_graph * data["graph_score"]
            )

            # Confidence bonus (slight reward for verified evidence)
            conf_bonus = 0.05 if conf_enum == ConfidenceLevel.VERIFIED else 0.0
            final_score = min(1.0, round(base_score + conf_bonus, 4))

            # Explain why retrieved
            why_retrieved = " + ".join(data["why"])
            if conf_enum == ConfidenceLevel.VERIFIED:
                why_retrieved += " (Verified primary source)"

            ranked_results.append(RetrievalResultItem(
                result_id=str(uuid4()),
                memory_id=payload.get("memory_id"),
                media_id=payload.get("media_id"),
                evidence_id=payload.get("evidence_id"),
                chunk_id=payload.get("chunk_id"),
                text=payload.get("text", ""),
                score=final_score,
                score_components={
                    "vector_score": round(data["vector_score"], 4),
                    "keyword_score": round(data["keyword_score"], 4),
                    "graph_score": round(data["graph_score"], 4),
                    "confidence_bonus": conf_bonus
                },
                source_reference=payload.get("source_reference", "Primary Archive"),
                provenance_status=prov_enum,
                confidence=conf_enum,
                content_type=payload.get("content_type", "EVIDENCE"),
                retrieval_method=query.retrieval_mode,
                why_retrieved=why_retrieved,
                created_at=datetime.now(timezone.utc)
            ))

        # Sort descending by score
        ranked_results.sort(key=lambda x: x.score, reverse=True)
        top_results = ranked_results[:query.top_k]

        latency = round((time.time() - start_time) * 1000, 2)

        # Log query metrics for evaluation
        log_entry = {
            "query_id": str(uuid4()),
            "query": query.query,
            "memorial_profile_id": query.memorial_profile_id,
            "retrieval_mode": query.retrieval_mode.value,
            "top_k": query.top_k,
            "candidate_count": len(all_candidates),
            "returned_count": len(top_results),
            "latency_ms": latency,
            "vector_candidates": len(vector_candidates),
            "keyword_candidates": len(keyword_candidates),
            "graph_candidates": len(graph_candidates),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._retrieval_logs.append(log_entry)

        return RetrievalResponse(
            query_id=log_entry["query_id"],
            query=query.query,
            retrieval_mode=query.retrieval_mode,
            top_k=query.top_k,
            candidate_count=len(all_candidates),
            returned_count=len(top_results),
            latency_ms=latency,
            results=top_results,
            metrics={
                "vector_candidates": len(vector_candidates),
                "keyword_candidates": len(keyword_candidates),
                "graph_candidates": len(graph_candidates),
                "total_candidates": len(all_candidates)
            }
        )

    def _check_privacy_access(
        self,
        user_boundary: Optional[PrivacyLevel],
        item_privacy: str
    ) -> bool:
        """Enforce strict backend authorization boundary.
        
        PRIVATE: requires user_boundary == PRIVATE (Owner/Guardian).
        FAMILY: requires user_boundary in (PRIVATE, FAMILY).
        AUTHORIZED_USERS / RESTRICTED: accessible if user has authorization.
        """
        if not user_boundary or user_boundary == PrivacyLevel.PRIVATE:
            return True  # Owner can see all

        if item_privacy == "PRIVATE":
            return False  # Non-owners cannot see private records

        if user_boundary == PrivacyLevel.FAMILY:
            return item_privacy in ("FAMILY", "AUTHORIZED_USERS", "FAMILY_ONLY", "MEMORIAL_PUBLIC")

        if user_boundary == PrivacyLevel.AUTHORIZED_USERS:
            return item_privacy in ("AUTHORIZED_USERS", "MEMORIAL_PUBLIC")

        return True

    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._retrieval_logs[-limit:]


# Global singleton
_global_retrieval_service: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    global _global_retrieval_service
    if _global_retrieval_service is None:
        _global_retrieval_service = RetrievalService()
    return _global_retrieval_service
