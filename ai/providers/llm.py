"""Large Language Model (LLM) Provider Interface and Implementations.

CRITICAL ETHICAL CONSTRAINT:
No LLM provider may ever claim to possess consciousness, claim to be the deceased,
or fabricate statements outside documented evidence.
"""

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

from ai.providers.base import BaseAIProvider, ProviderStatus, ProviderHealth
from models.provenance import ProvenanceRecord
from models.conversation import ETHICAL_DISCLAIMER_TEXT


class LLMGenerationRequest(BaseModel):
    prompt: str
    system_instruction: Optional[str] = None
    evidence_context: List[str] = []
    temperature: float = 0.2
    max_tokens: int = 1000


class LLMGenerationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    content: str
    ethical_disclaimer: str = ETHICAL_DISCLAIMER_TEXT
    is_grounded: bool = True
    provider_name: str
    model_name: str
    citations: List[ProvenanceRecord] = []
    confidence_score: float = 1.0


class BaseLLMProvider(BaseAIProvider):
    """Abstract interface for LLM synthesis."""

    def __init__(self, name: str, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(name=name, category="LLM", api_key=api_key, model=model)

    @abstractmethod
    async def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        pass


class MockLLMProvider(BaseLLMProvider):
    """Safe offline mock LLM provider for tests and development without API keys."""

    def __init__(self, model: str = "echo-mock-llm-v1"):
        super().__init__(name="MockLLMProvider", api_key="mock_key", model=model)

    def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            name=self.name,
            category=self.category,
            status=ProviderStatus.MOCK_MODE,
            model=self.model,
            is_ready=True,
            message="Mock LLM active (offline/deterministic mode)."
        )

    async def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        # Ground response strictly in provided evidence
        if request.evidence_context:
            context_summary = " ".join(request.evidence_context[:2])
            response_text = (
                f"Based on preserved archival records, {context_summary} "
                f"[Documented in archive]."
            )
        else:
            response_text = (
                "No preserved archival evidence is currently on record regarding this query. "
                "ECHO does not fabricate or infer undocumented memories."
            )

        return LLMGenerationResponse(
            content=response_text,
            is_grounded=bool(request.evidence_context),
            provider_name=self.name,
            model_name=self.model or "echo-mock-llm-v1",
            citations=[],
            confidence_score=1.0 if request.evidence_context else 0.0
        )


class GeminiLLMProvider(BaseLLMProvider):
    """Gemini LLM Provider adapter."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        super().__init__(name="GoogleGeminiProvider", api_key=api_key, model=model)

    def get_health(self) -> ProviderHealth:
        if not self.is_configured:
            return ProviderHealth(
                name=self.name,
                category=self.category,
                status=ProviderStatus.UNCONFIGURED,
                model=self.model,
                is_ready=False,
                message="GEMINI_API_KEY is not set. Configure in .env to activate."
            )
        return ProviderHealth(
            name=self.name,
            category=self.category,
            status=ProviderStatus.CONFIGURED,
            model=self.model,
            is_ready=True,
            message="Gemini API credentials verified."
        )

    async def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        if not self.is_configured:
            raise RuntimeError(
                "Gemini provider is unconfigured. Set LLM_API_KEY in environment or switch to mock provider."
            )
        # Real integration in Phase 6 / RAG phase
        raise NotImplementedError("Live provider generation will be activated in Phase 6.")
