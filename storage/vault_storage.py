"""Secure Multimodal Vault Storage System for ECHO.

Confined strictly to D:\\ECHO\\storage.
Manages:
- D:\\ECHO\\storage\\originals
- D:\\ECHO\\storage\\processed
- D:\\ECHO\\storage\\thumbnails
- D:\\ECHO\\storage\\temporary
- D:\\ECHO\\storage\\exports

Enforces:
- Path traversal protection (escape attempts strictly rejected)
- Malicious filename sanitization
- Extension and MIME validation
- Cryptographic SHA-256 checksum generation
- Duplicate file detection
- Image thumbnail generation via Pillow
- Temporary processing cleanup
- Safe relative storage paths (No physical absolute paths exposed to frontend)
"""

from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
import asyncio
import hashlib
import os
import re
from datetime import datetime
from PIL import Image
import io

from storage.base import BaseStorageProvider


class UnsupportedFileTypeError(ValueError):
    """Raised when an uploaded file extension or MIME type is not permitted."""
    pass


class FileSizeLimitExceededError(ValueError):
    """Raised when file size exceeds vault storage limits."""
    pass


class MaliciousPathError(PermissionError):
    """Raised when path traversal or forbidden characters are detected."""
    pass


class VaultStorageManager(BaseStorageProvider):
    """Central storage manager for ECHO Multimodal Memory Vault."""

    # Supported File Extensions and MIME Mappings
    ALLOWED_EXTENSIONS = {
        # Images
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        # Videos
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".webm": "video/webm",
        # Audio
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        # Documents
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    # Additional accepted MIME variants
    ALLOWED_MIMES = {
        "image/jpeg", "image/png", "image/webp",
        "video/mp4", "video/quicktime", "video/webm",
        "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/m4a", "audio/mp4", "audio/x-m4a",
        "application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword", "application/octet-stream"
    }

    MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 Megabytes

    def __init__(self, storage_root: Optional[str] = None):
        if storage_root:
            self.root = Path(storage_root).resolve()
        else:
            # Default strictly to D:\ECHO\storage
            self.root = (Path(__file__).parent).resolve()

        self.originals_dir = self.root / "originals"
        self.processed_dir = self.root / "processed"
        self.thumbnails_dir = self.root / "thumbnails"
        self.temporary_dir = self.root / "temporary"
        self.exports_dir = self.root / "exports"

        # Ensure all required directories exist inside D:\ECHO\storage
        for d in [self.originals_dir, self.processed_dir, self.thumbnails_dir, self.temporary_dir, self.exports_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # In-memory checksum index for fast duplicate detection (checksum -> relative_path)
        self._checksum_index: Dict[str, str] = {}
        self._scan_existing_checksums()

    def _scan_existing_checksums(self):
        """Build initial index of existing files to detect duplicates across restarts."""
        try:
            if self.originals_dir.exists():
                for p in self.originals_dir.glob("*"):
                    if p.is_file() and not p.name.startswith("."):
                        try:
                            # If filename starts with 64-char hex hash, use it
                            parts = p.name.split("_", 1)
                            if len(parts) == 2 and len(parts[0]) == 64 and all(c in "0123456789abcdef" for c in parts[0].lower()):
                                rel_path = f"originals/{p.name}"
                                self._checksum_index[parts[0].lower()] = rel_path
                        except Exception:
                            pass
        except Exception:
            pass

    def _resolve_safe_path(self, file_path_relative: str) -> Path:
        """Resolve relative path and verify it cannot escape storage root."""
        # Detect explicit path traversal sequences before normalization
        if ".." in file_path_relative or "\0" in file_path_relative:
            raise MaliciousPathError(f"Path traversal sequence detected: {file_path_relative}")

        cleaned = file_path_relative.lstrip("/\\")
        target = (self.root / cleaned).resolve()

        try:
            target.relative_to(self.root)
        except ValueError:
            raise MaliciousPathError(
                f"Path traversal detected: {file_path_relative} escapes storage root {self.root}"
            )
        return target

    def get_absolute_path(self, file_path_relative: str) -> Path:
        """Internal backend only. NEVER expose this path to the frontend."""
        return self._resolve_safe_path(file_path_relative)

    @classmethod
    def get_mime_type(cls, filename: str) -> str:
        """Get canonical MIME type from filename extension."""
        ext = Path(filename).suffix.lower()
        return cls.ALLOWED_EXTENSIONS.get(ext, "application/octet-stream")

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to eliminate path traversal, control chars, and illegal symbols."""
        if not filename:
            return "unnamed_memory_file.bin"
        
        # Check for path traversal or null bytes
        if ".." in filename or "/" in filename or "\\" in filename or "\0" in filename:
            # Strip path elements to obtain base name
            filename = os.path.basename(filename.replace("\\", "/"))

        # Remove null bytes or control characters
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        
        # Preserve base and extension
        base, ext = os.path.splitext(filename)
        sanitized_base = re.sub(r'[^a-zA-Z0-9_\-]', '_', base)
        sanitized_ext = ext.lower()
        
        # Limit length
        if len(sanitized_base) > 100:
            sanitized_base = sanitized_base[:100]
            
        clean_name = f"{sanitized_base}{sanitized_ext}".strip("._")
        return clean_name or "memory_file.bin"

    @classmethod
    def validate_file(cls, filename: str, content: bytes, mime_type: Optional[str] = None) -> Tuple[str, str]:
        """Validate filename, file size, extension, and MIME type."""
        # 1. Size Check
        file_size = len(content)
        if file_size > cls.MAX_FILE_SIZE_BYTES:
            raise FileSizeLimitExceededError(
                f"File size ({file_size} bytes) exceeds maximum limit of {cls.MAX_FILE_SIZE_BYTES} bytes (100MB)."
            )
        if file_size == 0:
            raise ValueError("Empty file upload is not allowed.")

        # 2. Filename & Extension Check
        clean_name = cls.sanitize_filename(filename)
        ext = os.path.splitext(clean_name)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(cls.ALLOWED_EXTENSIONS.keys()))}"
            )

        # 3. MIME Validation
        expected_mime = cls.ALLOWED_EXTENSIONS[ext]
        resolved_mime = (mime_type or expected_mime).lower().split(";")[0].strip()
        
        # If MIME given doesn't match and isn't a known allowed MIME variant
        if resolved_mime not in cls.ALLOWED_MIMES and resolved_mime != expected_mime:
            # If application/octet-stream, fallback to extension-derived MIME
            if resolved_mime == "application/octet-stream":
                resolved_mime = expected_mime
            else:
                raise UnsupportedFileTypeError(
                    f"Unsupported or mismatched MIME type '{resolved_mime}' for extension '{ext}'."
                )

        return clean_name, resolved_mime

    @staticmethod
    def calculate_checksum(content: bytes) -> str:
        """Calculate cryptographically secure SHA-256 digest."""
        hasher = hashlib.sha256()
        hasher.update(content)
        return hasher.hexdigest()

    async def save_file(
        self,
        file_path_relative: str,
        content: bytes,
        mime_type: Optional[str] = None
    ) -> str:
        """Save file to storage and return relative path."""
        target = self._resolve_safe_path(file_path_relative)
        target.parent.mkdir(parents=True, exist_ok=True)

        def _write():
            with open(target, "wb") as f:
                f.write(content)

        await asyncio.to_thread(_write)
        return str(target.relative_to(self.root)).replace("\\", "/")

    async def get_file(self, file_path_relative: str) -> bytes:
        """Retrieve file content from storage."""
        target = self._resolve_safe_path(file_path_relative)
        if not target.exists():
            raise FileNotFoundError(f"File not found in vault storage: {file_path_relative}")

        def _read() -> bytes:
            with open(target, "rb") as f:
                return f.read()

        return await asyncio.to_thread(_read)

    async def delete_file(self, file_path_relative: str) -> bool:
        """Safely remove a file from vault storage."""
        target = self._resolve_safe_path(file_path_relative)
        if target.exists():
            await asyncio.to_thread(target.unlink)
            return True
        return False

    async def exists(self, file_path_relative: str) -> bool:
        target = self._resolve_safe_path(file_path_relative)
        return await asyncio.to_thread(target.exists)

    async def save_original(
        self,
        original_filename: str,
        content: bytes,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate, check duplicates, store in originals/, generate thumbnail, and return metadata."""
        # 1. Validation
        clean_filename, resolved_mime = self.validate_file(original_filename, content, mime_type)
        checksum = self.calculate_checksum(content)

        # 2. Duplicate Detection
        if checksum in self._checksum_index:
            existing_rel_path = self._checksum_index[checksum]
            existing_target = self.root / existing_rel_path
            if existing_target.exists():
                # Derive existing thumbnail path if any
                thumb_name = f"{checksum[:16]}_thumb.jpg"
                thumb_rel_path = f"thumbnails/{thumb_name}"
                has_thumb = (self.root / thumb_rel_path).exists()
                return {
                    "is_duplicate": True,
                    "checksum": checksum,
                    "storage_path": existing_rel_path,
                    "thumbnail_path": thumb_rel_path if has_thumb else None,
                    "file_size": len(content),
                    "mime_type": resolved_mime,
                    "original_filename": clean_filename,
                    "message": "Duplicate file detected. Existing vault asset referenced."
                }

        # 3. Store in originals/
        storage_filename = f"{checksum}_{clean_filename}"
        rel_storage_path = f"originals/{storage_filename}"
        await self.save_file(rel_storage_path, content, resolved_mime)
        self._checksum_index[checksum] = rel_storage_path

        # 4. Generate Thumbnail if Image
        thumbnail_rel_path = None
        ext = os.path.splitext(clean_filename)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            thumbnail_rel_path = await self._generate_image_thumbnail(content, checksum)

        return {
            "is_duplicate": False,
            "checksum": checksum,
            "storage_path": rel_storage_path,
            "thumbnail_path": thumbnail_rel_path,
            "file_size": len(content),
            "mime_type": resolved_mime,
            "original_filename": clean_filename,
            "message": "File successfully stored in vault originals."
        }

    async def _generate_image_thumbnail(self, content: bytes, checksum: str) -> Optional[str]:
        """Generate and save 300x300 thumbnail for images."""
        thumb_filename = f"{checksum[:16]}_thumb.jpg"
        rel_thumb_path = f"thumbnails/{thumb_filename}"
        target = self.root / rel_thumb_path

        def _make_thumb():
            try:
                with Image.open(io.BytesIO(content)) as img:
                    img = img.convert("RGB")
                    img.thumbnail((300, 300))
                    img.save(target, format="JPEG", quality=85)
                return True
            except Exception:
                return False

        success = await asyncio.to_thread(_make_thumb)
        return rel_thumb_path if success else None

    async def clean_temporary(self, file_path_relative: str) -> bool:
        """Safely delete temporary processing file."""
        if not file_path_relative.startswith("temporary/"):
            return False
        return await self.delete_file(file_path_relative)


# Singleton vault storage instance
vault_storage = VaultStorageManager()
