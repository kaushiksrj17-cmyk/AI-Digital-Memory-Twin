"""Vector Database Abstraction Interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class VectorSearchResult(BaseModel):
    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None


class BaseVectorDatabase(ABC):
    """Abstract interface for vector database storage and semantic retrieval."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize collection/index."""
        pass

    @abstractmethod
    async def upsert(
        self,
        id: str,
        vector: List[float],
        payload: Dict[str, Any]
    ) -> bool:
        """Upsert a vector along with metadata payload."""
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search nearest neighbors for query vector."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete vector entry by ID."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return provider connection and collection status."""
        pass
