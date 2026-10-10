"""In-memory Mock Vector Provider for testing and offline development."""

from typing import List, Dict, Any, Optional
import math
from database.vector.base import BaseVectorDatabase, VectorSearchResult


class MockVectorDatabase(BaseVectorDatabase):
    """In-memory cosine similarity vector database with zero external dependencies."""

    def __init__(self, collection_name: str = "echo_evidence_vectors", dimension: int = 1536):
        self.collection_name = collection_name
        self.dimension = dimension
        self._store: Dict[str, Dict[str, Any]] = {}
        self.initialized = True

    async def initialize(self) -> bool:
        self.initialized = True
        return True

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def upsert(self, id: str, vector: List[float], payload: Dict[str, Any]) -> bool:
        self._store[id] = {
            "vector": vector,
            "payload": payload
        }
        return True

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        results: List[VectorSearchResult] = []
        for vid, entry in self._store.items():
            # Check metadata filters
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if entry["payload"].get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            score = self._cosine_similarity(query_vector, entry["vector"])
            if score_threshold is not None and score < score_threshold:
                continue

            results.append(VectorSearchResult(
                id=vid,
                score=score,
                payload=entry["payload"]
            ))

        # Sort descending by score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    async def delete(self, id: str) -> bool:
        if id in self._store:
            del self._store[id]
            return True
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "MockVectorDatabase (In-Memory)",
            "status": "ready",
            "collection": self.collection_name,
            "count": len(self._store),
            "dimension": self.dimension
        }
