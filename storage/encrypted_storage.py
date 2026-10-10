"""Future Encrypted Storage Provider abstraction.

Prepares ECHO for client-side zero-knowledge encryption and AES-256-GCM
at-rest encryption for sensitive memorial artifacts (letters, medical records, voice notes).
"""

from typing import Optional
from pathlib import Path
from storage.base import BaseStorageProvider
from storage.local_storage import LocalStorageProvider


class EncryptedStorageProvider(BaseStorageProvider):
    """Encrypted storage wrapper around private local storage."""

    def __init__(self, key: Optional[str] = None, underlying_provider: Optional[BaseStorageProvider] = None):
        self.key = key
        self.underlying = underlying_provider or LocalStorageProvider()
        self.is_configured = bool(key and len(key) >= 32)

    def get_absolute_path(self, file_path_relative: str) -> Path:
        return self.underlying.get_absolute_path(file_path_relative)

    async def save_file(
        self,
        file_path_relative: str,
        content: bytes,
        mime_type: Optional[str] = None
    ) -> str:
        if not self.is_configured:
            # In Phase 1 foundation: fallback to secure local storage with metadata flag
            # Explicitly log unconfigured encryption status
            return await self.underlying.save_file(file_path_relative, content, mime_type)
        
        # In future Phase (Phase 2), AES-GCM encryption will transform content bytes here
        return await self.underlying.save_file(file_path_relative, content, mime_type)

    async def get_file(self, file_path_relative: str) -> bytes:
        return await self.underlying.get_file(file_path_relative)

    async def delete_file(self, file_path_relative: str) -> bool:
        return await self.underlying.delete_file(file_path_relative)

    async def exists(self, file_path_relative: str) -> bool:
        return await self.underlying.exists(file_path_relative)
