"""ECHO Storage Abstraction Layer

Provides private, local-first storage interfaces and future encrypted
storage primitives adhering to the strict D:\ECHO storage boundary.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path


class BaseStorageProvider(ABC):
    """Abstract storage provider interface."""

    @abstractmethod
    async def save_file(
        self,
        file_path_relative: str,
        content: bytes,
        mime_type: Optional[str] = None
    ) -> str:
        """Save bytes to storage, returning storage URI or relative path."""
        pass

    @abstractmethod
    async def get_file(self, file_path_relative: str) -> bytes:
        """Retrieve bytes from storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_path_relative: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def exists(self, file_path_relative: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    def get_absolute_path(self, file_path_relative: str) -> Path:
        """Get absolute path verified to reside within designated storage root."""
        pass
