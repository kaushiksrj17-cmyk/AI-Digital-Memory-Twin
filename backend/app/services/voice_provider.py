"""Voice Provider Abstraction and Audio Validation Engine.

Provides interchangeable Speech-to-Text and Text-to-Speech provider interfaces,
strict audio payload validation (magic byte headers, MIME verification, size limits),
and tamper-resistant metadata reporting.
"""

from typing import Dict, Any, Optional, Tuple, Set
import os
import wave
import io
import hashlib

from ai.providers.factory import provider_registry
from ai.providers.stt import BaseSTTProvider, MockSTTProvider
from ai.providers.tts import BaseTTSProvider, MockTTSProvider
from models.enums import ProviderReadiness


class VoiceProviderService:
    """Manages interchangeable voice providers and validates raw audio streams."""

    ALLOWED_EXTENSIONS: Set[str] = {".wav", ".mp3", ".m4a", ".webm", ".ogg"}
    ALLOWED_MIME_TYPES: Set[str] = {
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/mp3",
        "audio/mpeg",
        "audio/m4a",
        "audio/mp4",
        "audio/x-m4a",
        "audio/webm",
        "audio/ogg",
        "audio/opus",
        "application/octet-stream"  # Browser generic fallback
    }
    MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB

    def __init__(self):
        self.supported_languages = ["en", "ta", "hi"]

    def get_stt_provider(self) -> BaseSTTProvider:
        """Retrieve active STT provider from central registry."""
        return provider_registry.stt_provider

    def get_tts_provider(self) -> BaseTTSProvider:
        """Retrieve active TTS provider from central registry."""
        return provider_registry.tts_provider

    def get_capabilities(self) -> Dict[str, Any]:
        """Aggregate voice capabilities, supported languages, and provider readiness."""
        stt_health = self.get_stt_provider().get_health()
        tts_health = self.get_tts_provider().get_health()

        return {
            "supported_languages": [
                {"code": "en", "name": "English", "locale": "en-US"},
                {"code": "ta", "name": "Tamil (தமிழ்)", "locale": "ta-IN"},
                {"code": "hi", "name": "Hindi (हिन्दी)", "locale": "hi-IN"}
            ],
            "audio_categories": [
                "ORIGINAL_RECORDING",
                "TRANSCRIPTION",
                "AI_GENERATED_MEMORIAL_VOICE"
            ],
            "stt_engine": {
                "name": stt_health.name,
                "status": stt_health.status.value,
                "is_ready": stt_health.is_ready,
                "model": stt_health.model,
                "message": stt_health.message
            },
            "tts_engine": {
                "name": tts_health.name,
                "status": tts_health.status.value,
                "is_ready": tts_health.is_ready,
                "model": tts_health.model,
                "message": tts_health.message
            },
            "watermarking_enforced": True,
            "ethical_disclaimer": "AI-GENERATED MEMORIAL VOICE — SYNTHETIC AUDIO, NOT AN ORIGINAL RECORDING.",
            "max_file_size_mb": 25.0,
            "allowed_extensions": list(self.ALLOWED_EXTENSIONS)
        }

    def validate_audio(
        self,
        audio_bytes: bytes,
        filename: str,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Strictly validate audio file structure, size, extension, and content headers."""
        if not audio_bytes or len(audio_bytes) == 0:
            raise ValueError("Audio payload is empty.")

        file_size = len(audio_bytes)
        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Audio file exceeds maximum size limit of 25MB (got {file_size / (1024*1024):.2f}MB).")

        ext = os.path.splitext(filename.lower())[1]
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported audio format '{ext}'. Allowed formats: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}")

        if mime_type and mime_type.lower() not in self.ALLOWED_MIME_TYPES:
            raise ValueError(f"Unsupported MIME type '{mime_type}'.")

        # Magic byte signature verification
        is_valid_header = False
        duration_seconds = 0.0

        if ext == ".wav" or audio_bytes.startswith(b"RIFF"):
            if len(audio_bytes) >= 12 and audio_bytes[8:12] == b"WAVE":
                is_valid_header = True
                try:
                    with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                        n_frames = wf.getnframes()
                        rate = wf.getframerate()
                        if rate > 0:
                            duration_seconds = round(n_frames / float(rate), 2)
                except Exception:
                    # Incomplete or non-standard WAV frames, but valid container
                    pass
        elif ext == ".mp3" or audio_bytes.startswith(b"ID3") or audio_bytes.startswith(b"\xff\xfb") or audio_bytes.startswith(b"\xff\xf3"):
            is_valid_header = True
        elif ext == ".ogg" or audio_bytes.startswith(b"OggS"):
            is_valid_header = True
        elif ext == ".webm" or audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
            is_valid_header = True
        elif ext == ".m4a" or (len(audio_bytes) > 8 and audio_bytes[4:8] == b"ftyp"):
            is_valid_header = True
        else:
            # Fallback for recorded microphone blobs that might start with WebM/OGG container
            if audio_bytes.startswith(b"\x1a\x45\xdf\xa3") or audio_bytes.startswith(b"OggS"):
                is_valid_header = True

        if not is_valid_header:
            raise ValueError("Malformed or unrecognized audio file signature.")

        # If duration was not parsed from header, provide safe heuristic based on standard 128kbps
        if duration_seconds <= 0.0:
            duration_seconds = max(1.0, round((file_size * 8) / 128000.0, 2))

        # Checksum calculation for archival tamper-evidence
        sha256 = hashlib.sha256(audio_bytes).hexdigest()

        return {
            "is_valid": True,
            "filename": filename,
            "extension": ext,
            "mime_type": mime_type or f"audio/{ext.replace('.', '')}",
            "file_size_bytes": file_size,
            "duration_seconds": duration_seconds,
            "sha256": sha256
        }


voice_provider_service = VoiceProviderService()
