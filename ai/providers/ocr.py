"""Optical Character Recognition (OCR) Provider Interface and Implementations."""

from abc import abstractmethod
from typing import Optional, Dict, Any
from ai.providers.base import BaseAIProvider, ProviderStatus, ProviderHealth


class BaseOCRProvider(BaseAIProvider):
    """Abstract interface for digitizing handwritten letters, diaries, and historical certificates."""

    def __init__(self, name: str, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(name=name, category="OCR", api_key=api_key, model=model)

    @abstractmethod
    async def extract_text(self, document_bytes: bytes) -> Dict[str, Any]:
        pass


class MockOCRProvider(BaseOCRProvider):
    """Mock OCR provider for offline tests."""

    def __init__(self):
        super().__init__(name="MockOCRProvider", api_key="mock", model="mock-ocr-v1")

    def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            name=self.name,
            category=self.category,
            status=ProviderStatus.MOCK_MODE,
            model=self.model,
            is_ready=True,
            message="Mock OCR extraction ready."
        )

    async def extract_text(self, document_bytes: bytes) -> Dict[str, Any]:
        return {
            "extracted_text": "Dearest Eleanor, The spring blossoms in Oxford have finally bloomed...",
            "confidence": 0.94,
            "detected_handwriting": True,
            "page_count": 1,
            "is_mock": True
        }
