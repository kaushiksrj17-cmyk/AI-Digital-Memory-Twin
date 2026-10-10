"""Provider Factory.

Initializes configured AI providers according to environment settings,
automatically resolving to unconfigured or mock providers when keys are missing.
Never falsely claims that real external AI processing has completed.
"""

from typing import Dict, Any, List
import os

from ai.providers.base import BaseAIProvider, ProviderHealth
from ai.providers.llm import BaseLLMProvider, MockLLMProvider, GeminiLLMProvider
from ai.providers.embeddings import BaseEmbeddingProvider, MockEmbeddingProvider
from ai.providers.stt import BaseSTTProvider, MockSTTProvider
from ai.providers.tts import BaseTTSProvider, MockTTSProvider
from ai.providers.vision import BaseVisionProvider, MockVisionProvider
from ai.providers.ocr import BaseOCRProvider, MockOCRProvider


class AIProviderRegistry:
    """Central registry and factory for all multimodal AI providers."""

    def __init__(self):
        self.llm_provider: BaseLLMProvider = self._resolve_llm()
        self.embedding_provider: BaseEmbeddingProvider = self._resolve_embedding()
        self.stt_provider: BaseSTTProvider = MockSTTProvider()
        self.tts_provider: BaseTTSProvider = MockTTSProvider()
        self.vision_provider: BaseVisionProvider = MockVisionProvider()
        self.ocr_provider: BaseOCRProvider = MockOCRProvider()

    def _resolve_llm(self) -> BaseLLMProvider:
        provider_type = os.getenv("LLM_PROVIDER", "mock").lower()
        api_key = os.getenv("LLM_API_KEY", "")
        model = os.getenv("LLM_MODEL", "gemini-1.5-pro")

        if provider_type == "gemini":
            return GeminiLLMProvider(api_key=api_key, model=model)
        return MockLLMProvider(model="echo-mock-llm-v1")

    def _resolve_embedding(self) -> BaseEmbeddingProvider:
        return MockEmbeddingProvider(dimension=1536)

    def get_llm(self) -> BaseLLMProvider:
        return self.llm_provider

    def get_stt(self) -> BaseSTTProvider:
        return self.stt_provider

    def get_tts(self) -> BaseTTSProvider:
        return self.tts_provider

    def get_embedding(self) -> BaseEmbeddingProvider:
        return self.embedding_provider

    def get_vision(self) -> BaseVisionProvider:
        return self.vision_provider

    def get_ocr(self) -> BaseOCRProvider:
        return self.ocr_provider

    def get_all_health(self) -> List[ProviderHealth]:
        """Aggregate health and credential status across all AI subsystems."""
        return [
            self.llm_provider.get_health(),
            self.embedding_provider.get_health(),
            self.stt_provider.get_health(),
            self.tts_provider.get_health(),
            self.vision_provider.get_health(),
            self.ocr_provider.get_health()
        ]


# Global singleton registry instance
provider_registry = AIProviderRegistry()
