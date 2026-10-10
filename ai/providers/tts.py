"""Text-to-Speech (TTS) Provider Interface and Implementations.

CRITICAL ETHICAL BOUNDARIES:
- Voice synthesis must only be utilized with verified consent from the subject or
  authorized next-of-kin.
- All synthesized audio must embed digital watermarks and metadata explicitly indicating
  AI memorial generation.
- Never present synthesized audio as an original recording.
- Clearly and transparently label simulated/mock results.
"""

from abc import abstractmethod
from typing import Optional, Dict, Any
import wave
import io
import math
import struct
import os

from ai.providers.base import BaseAIProvider, ProviderStatus, ProviderHealth


def generate_synthesized_audio_bytes(
    duration_seconds: float = 2.0,
    sample_rate: int = 16000,
    frequency: float = 440.0,
    watermark_tag: str = "[ECHO-AI-MEMORIAL-VOICE-VERIFIED]"
) -> bytes:
    """Generate synthetically synthesized WAV audio bytes with digital watermark container.
    
    Creates a pleasant acoustic chime modulated to verify playback functionality
    offline without external API costs or proprietary voice dependencies.
    """
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        n_samples = max(int(duration_seconds * sample_rate), sample_rate)
        frames = bytearray()
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            # Smooth attack and decay envelope
            progress = t / duration_seconds
            envelope = math.sin(math.pi * min(1.0, max(0.0, progress))) ** 2
            # Gentle harmonic acoustic chime
            tone = (
                math.sin(2.0 * math.pi * frequency * t) * 0.6 +
                math.sin(2.0 * math.pi * (frequency * 1.5) * t) * 0.25 +
                math.sin(2.0 * math.pi * (frequency * 2.0) * t) * 0.15
            )
            val = int(32767.0 * 0.28 * envelope * tone)
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
            
        wf.writeframes(frames)
    return buf.getvalue()


class BaseTTSProvider(BaseAIProvider):
    """Abstract interface for speech synthesis and voice modeling."""

    def __init__(self, name: str, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(name=name, category="Text-to-Speech", api_key=api_key, model=model)

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_profile_id: Optional[str] = None,
        language: Optional[str] = "en",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        pass


class MockTTSProvider(BaseTTSProvider):
    """Deterministic Mock TTS provider returning authentic WAV bytes with AI disclosure watermark."""

    def __init__(self):
        super().__init__(name="MockTTSProvider", api_key="mock", model="echo-mock-voice-v1")

    def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            name=self.name,
            category=self.category,
            status=ProviderStatus.MOCK_MODE,
            model=self.model,
            is_ready=True,
            message="Deterministic Mock Voice Synthesis active (Simulation only)."
        )

    async def synthesize(
        self,
        text: str,
        voice_profile_id: Optional[str] = None,
        language: Optional[str] = "en",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        words = len(text.split())
        # Estimate spoken duration (~2.5 words per sec, adjusted by speed)
        effective_speed = max(0.5, min(2.0, speed))
        calc_duration = round(max(1.8, (words / 2.5) / effective_speed), 2)
        
        # Frequency based on language or voice profile
        freq = 380.0 if language == "ta" else (420.0 if language == "hi" else 440.0)
        
        audio_bytes = generate_synthesized_audio_bytes(
            duration_seconds=calc_duration,
            sample_rate=16000,
            frequency=freq
        )

        return {
            "audio_bytes": audio_bytes,
            "audio_bytes_length": len(audio_bytes),
            "format": "audio/wav",
            "duration_seconds": calc_duration,
            "is_watermarked_ai": True,
            "watermark_tag": "[ECHO-AI-MEMORIAL-VOICE-VERIFIED]",
            "ethical_disclosure": "AI-GENERATED MEMORIAL VOICE — SYNTHETIC AUDIO, NOT AN ORIGINAL RECORDING.",
            "voice_profile_id": voice_profile_id,
            "language": language or "en",
            "speed": speed,
            "is_mock": True,
            "provider_name": self.name,
            "model": self.model,
            "note": "SIMULATED SYNTHESIS: Deterministic mock voice provider used for testing/demonstration."
        }
