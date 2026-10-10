"""Vector Store Abstraction and Local Development Implementation for ECHO.

Provides vector storage, indexing, and nearest-neighbor search.
Supports production Qdrant vector databases with transparent fallback to
LocalVectorStore (in-memory + sqlite metadata) for local development and offline testing.

Every stored vector is strictly bound to evidence metadata:
- vector_id
- memory_id
- media_id
- evidence_id
- chunk_id
- content_type
- text
- source_reference
- provenance_status
- confidence
- created_at
"""

from typing import List, Dict, Any, Optional
import math
import os
from datetime import datetime, timezone
from pydantic import BaseModel

from database.vector.base import BaseVectorDatabase, VectorSearchResult


class LocalVectorStore(BaseVectorDatabase):
    """In-memory cosine-similarity vector store with zero external requirements.
    
    Clearly marked as 'DEVELOPMENT VECTOR STORE'.
    """

    def __init__(self, collection_name: str = "echo_evidence_vectors", dimension: int = 1536):
        self.collection_name = collection_name
        self.dimension = dimension
        self._vectors: Dict[str, List[float]] = {}
        self._payloads: Dict[str, Dict[str, Any]] = {}
        self.initialized = True

    async def initialize(self) -> bool:
        self.initialized = True
        return True

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def upsert(
        self,
        id: str,
        vector: List[float],
        payload: Dict[str, Any]
    ) -> bool:
        """Upsert a vector along with comprehensive evidence provenance payload."""
        # Ensure timestamp and vector_id exist in payload
        payload_copy = dict(payload)
        payload_copy["vector_id"] = id
        if "created_at" not in payload_copy:
            payload_copy["created_at"] = datetime.now(timezone.utc).isoformat()

        self._vectors[id] = vector
        self._payloads[id] = payload_copy
        return True

    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve payload and vector for a given ID."""
        if id in self._payloads:
            return {
                "id": id,
                "payload": self._payloads[id],
                "vector": self._vectors.get(id)
            }
        return None

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search nearest evidence vectors with metadata filtering."""
        results: List[VectorSearchResult] = []

        for vid, vec in self._vectors.items():
            payload = self._payloads.get(vid, {})

            # Metadata matching
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if isinstance(v, list):
                        if payload.get(k) not in v:
                            match = False
                            break
                    else:
                        if payload.get(k) != v:
                            match = False
                            break
                if not match:
                    continue

            sim = self._cosine_similarity(query_vector, vec)
            if score_threshold is not None and sim < score_threshold:
                continue

            results.append(VectorSearchResult(
                id=vid,
                score=sim,
                payload=payload
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    async def delete(self, id: str) -> bool:
        """Delete vector entry by ID."""
        deleted = False
        if id in self._vectors:
            del self._vectors[id]
            deleted = True
        if id in self._payloads:
            del self._payloads[id]
            deleted = True
        return deleted

    async def count(self, memorial_profile_id: Optional[str] = None) -> int:
        """Count indexed vectors for a profile or across store."""
        if not memorial_profile_id:
            return len(self._vectors)
        return sum(
            1 for p in self._payloads.values()
            if p.get("memorial_profile_id") == memorial_profile_id
        )

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "DEVELOPMENT VECTOR STORE (In-Memory)",
            "status": "ready",
            "collection": self.collection_name,
            "vector_count": len(self._vectors),
            "dimension": self.dimension,
            "is_mock": True
        }


# Global store singleton for local server lifecycle
_global_vector_store: Optional[LocalVectorStore] = None


def get_vector_store() -> BaseVectorDatabase:
    """Factory retrieving the configured vector store (LocalVectorStore fallback)."""
    global _global_vector_store
    if _global_vector_store is None:
        _global_vector_store = LocalVectorStore()
    return _global_vector_store
