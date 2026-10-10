"""Computer Vision Provider Interface and Implementations."""

from abc import abstractmethod
from typing import Optional, Dict, Any, List
from ai.providers.base import BaseAIProvider, ProviderStatus, ProviderHealth


class BaseVisionProvider(BaseAIProvider):
    """Abstract interface for image description, facial clustering, and artifact detection."""

    def __init__(self, name: str, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(name=name, category="Computer Vision", api_key=api_key, model=model)

    @abstractmethod
    async def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        pass


class MockVisionProvider(BaseVisionProvider):
    """Mock Computer Vision provider."""

    def __init__(self):
        super().__init__(name="MockVisionProvider", api_key="mock", model="mock-vision-v1")

    def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            name=self.name,
            category=self.category,
            status=ProviderStatus.MOCK_MODE,
            model=self.model,
            is_ready=True,
            message="Mock Computer Vision ready."
        )

    async def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        return {
            "description": "Historical black and white family portrait in an outdoor garden.",
            "detected_objects": ["person", "garden bench", "trees"],
            "detected_faces_count": 2,
            "estimated_era": "circa 1960s",
            "is_mock": True
        }
