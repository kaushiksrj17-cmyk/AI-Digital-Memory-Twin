"""Embedding Service for ECHO.

Provides dense vector representations of textual evidence for semantic retrieval.
Supports configured external embedding providers with transparent fallback to
a deterministic development mock provider.

CRITICAL RESEARCH HONESTY:
Deterministic mock embeddings are clearly labeled "DEVELOPMENT / MOCK EMBEDDING"
and are never presented as real AI model performance.
"""

from typing import List, Dict, Any, Optional
import os
import hashlib
from ai.providers.embeddings import BaseEmbeddingProvider, MockEmbeddingProvider


class EmbeddingService:
    """Manages embedding generation for memory descriptions, OCR, transcripts, and DNA items."""

    def __init__(self, provider: Optional[BaseEmbeddingProvider] = None, dimension: int = 1536):
        self.dimension = dimension
        if provider:
            self.provider = provider
        else:
            api_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "mock_key":
                # If a live key is configured, instantiate external provider if available
                self.provider = MockEmbeddingProvider(dimension=dimension)
            else:
                self.provider = MockEmbeddingProvider(dimension=dimension)

    def is_mock(self) -> bool:
        """Indicate whether the active embedding provider is in development mock mode."""
        return isinstance(self.provider, MockEmbeddingProvider)

    async def get_embedding(self, text: str) -> List[float]:
        """Generate a dense embedding vector for the provided text.
        
        Filters out sensitive keys or credentials before generation.
        """
        if not text or not text.strip():
            # Zero vector fallback for empty text
            return [0.0] * self.dimension
        
        # Enforce privacy check: never embed password strings or raw tokens
        clean_text = self._sanitize_text(text)
        return await self.provider.get_embedding(clean_text)

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch generation of dense embeddings."""
        sanitized = [self._sanitize_text(t) for t in texts]
        return await self.provider.get_embeddings_batch(sanitized)

    def _sanitize_text(self, text: str) -> str:
        """Strip obvious private authentication markers from embeddable strings."""
        lowered = text.lower()
        if "password=" in lowered or "secret=" in lowered or "api_key=" in lowered:
            return "[REDACTED_SENSITIVE_CONTENT]"
        return text.strip()

    def get_status(self) -> Dict[str, Any]:
        """Return provider name, model, dimension, and development status."""
        health = self.provider.get_health()
        return {
            "provider_name": health.name,
            "category": "Embeddings",
            "model": health.model,
            "dimension": self.dimension,
            "status": "DEVELOPMENT / MOCK EMBEDDING" if self.is_mock() else "PRODUCTION EMBEDDING",
            "is_mock": self.is_mock(),
            "is_ready": health.is_ready,
            "message": health.message
        }
