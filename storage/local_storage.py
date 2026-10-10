"""Local private storage implementation.

Strictly confines file operations within D:\\ECHO\\storage\\local.
Prevents directory traversal and accidental leakage outside project root.
Uses standard library with asyncio.to_thread for robust, dependency-free async I/O.
"""

from pathlib import Path
from typing import Optional
import asyncio
import os

from storage.base import BaseStorageProvider


class LocalStorageProvider(BaseStorageProvider):
    """Local storage provider confined to D:\\ECHO\\storage\\local."""

    def __init__(self, root_dir: Optional[str] = None):
        if root_dir:
            self.root = Path(root_dir).resolve()
        else:
            # Default to D:\ECHO\storage\local
            self.root = (Path(__file__).parent / "local").resolve()

        self.uploads_dir = self.root / "uploads"
        self.cache_dir = self.root / "cache"

        # Ensure directories exist within D:\ECHO
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, file_path_relative: str) -> Path:
        """Resolve and verify path is safely inside storage root."""
        cleaned = file_path_relative.lstrip("/\\")
        target = (self.root / cleaned).resolve()

        try:
            target.relative_to(self.root)
        except ValueError:
            raise PermissionError(
                f"Path traversal detected: {file_path_relative} escapes storage root {self.root}"
            )
        return target

    def get_absolute_path(self, file_path_relative: str) -> Path:
        return self._resolve_safe_path(file_path_relative)

    async def save_file(
        self,
        file_path_relative: str,
        content: bytes,
        mime_type: Optional[str] = None
    ) -> str:
        target = self._resolve_safe_path(file_path_relative)
        target.parent.mkdir(parents=True, exist_ok=True)

        def _write():
            with open(target, "wb") as f:
                f.write(content)

        await asyncio.to_thread(_write)
        return str(target.relative_to(self.root)).replace("\\", "/")

    async def get_file(self, file_path_relative: str) -> bytes:
        target = self._resolve_safe_path(file_path_relative)
        if not target.exists():
            raise FileNotFoundError(f"File not found in storage: {file_path_relative}")

        def _read() -> bytes:
            with open(target, "rb") as f:
                return f.read()

        return await asyncio.to_thread(_read)

    async def delete_file(self, file_path_relative: str) -> bool:
        target = self._resolve_safe_path(file_path_relative)
        if target.exists():
            await asyncio.to_thread(target.unlink)
            return True
        return False

    async def exists(self, file_path_relative: str) -> bool:
        target = self._resolve_safe_path(file_path_relative)
        return await asyncio.to_thread(target.exists)
