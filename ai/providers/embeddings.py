"""Embedding Provider Interface and Implementations."""

from abc import abstractmethod
from typing import List, Optional
import hashlib
from ai.providers.base import BaseAIProvider, ProviderStatus, ProviderHealth


class BaseEmbeddingProvider(BaseAIProvider):
    """Abstract interface for dense vector embeddings."""

    def __init__(self, name: str, api_key: Optional[str] = None, model: Optional[str] = None, dimension: int = 1536):
        super().__init__(name=name, category="Embeddings", api_key=api_key, model=model)
        self.dimension = dimension

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        pass


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic in-memory embedding generator for offline testing."""

    def __init__(self, dimension: int = 1536):
        super().__init__(name="MockEmbeddingProvider", api_key="mock_key", model="mock-embed-v1", dimension=dimension)

    def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            name=self.name,
            category=self.category,
            status=ProviderStatus.MOCK_MODE,
            model=self.model,
            is_ready=True,
            message="Deterministic mock embedding provider active."
        )

    def _generate_deterministic_vector(self, text: str) -> List[float]:
        # Generate pseudo-embedding using SHA-256 seed so same text gives identical vectors
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        vec = []
        for i in range(self.dimension):
            val = ((seed + i * 31) % 1000) / 1000.0 - 0.5
            vec.append(val)
        # Normalize
        norm = sum(x * x for x in vec) ** 0.5
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    async def get_embedding(self, text: str) -> List[float]:
        return self._generate_deterministic_vector(text)

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_deterministic_vector(t) for t in texts]
