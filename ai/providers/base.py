"""AI Provider Base Architecture.

Defines status reporting, key verification, and graceful degradation
when third-party API credentials are not supplied.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ProviderStatus(str, Enum):
    CONFIGURED = "CONFIGURED"
    UNCONFIGURED = "UNCONFIGURED"  # Missing credentials
    MOCK_MODE = "MOCK_MODE"        # Safe local mock provider active
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"


class ProviderHealth(BaseModel):
    name: str
    category: str
    status: ProviderStatus
    model: Optional[str] = None
    is_ready: bool = False
    message: str = "Ready"


class BaseAIProvider(ABC):
    """Abstract base class for all pluggable AI providers."""

    def __init__(self, name: str, category: str, api_key: Optional[str] = None, model: Optional[str] = None):
        self.name = name
        self.category = category
        self.api_key = api_key
        self.model = model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    @abstractmethod
    def get_health(self) -> ProviderHealth:
        """Return provider readiness and credential status."""
        pass
