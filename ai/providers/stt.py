"""Speech-to-Text (STT) Provider Interface and Implementations.

Architectural support for English (en), Tamil (ta), and Hindi (hi).
Deterministic, research-grade mock provider for tests and offline demonstrations.
Real Gemini multimodal STT provider when configured with credentials.
Never presents mock output as genuine speech recognition.
"""

from abc import abstractmethod
from typing import Optional, Dict, Any, List
import wave
import io
import os
from uuid import uuid4

from ai.providers.base import BaseAIProvider, ProviderStatus, ProviderHealth


class BaseSTTProvider(BaseAIProvider):
    """Abstract interface for audio transcription and oral history extraction."""

    def __init__(self, name: str, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(name=name, category="Speech-to-Text", api_key=api_key, model=model)

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        pass


class MockSTTProvider(BaseSTTProvider):
    """Deterministic Mock STT provider for automated tests and offline demonstrations.
    
    Clearly and transparently labeled as a simulation.
    """

    SAMPLE_TRANSCRIPTS = {
        "en": "Can you tell me about the university graduation ceremony in 1968?",
        "ta": "1968 இல் நடந்த பல்கலைக்கழக பட்டமளிப்பு விழா பற்றி சொல்ல முடியுமா?",
        "hi": "क्या आप मुझे 1968 में विश्वविद्यालय के दीक्षांत समारोह के बारे में बता सकते हैं?"
    }

    def __init__(self):
        super().__init__(name="MockSTTProvider", api_key="mock", model="echo-mock-whisper-v1")

    def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            name=self.name,
            category=self.category,
            status=ProviderStatus.MOCK_MODE,
            model=self.model,
            is_ready=True,
            message="Deterministic Mock Speech-to-Text active (Simulation only)."
        )

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = "en") -> Dict[str, Any]:
        lang = (language or "en").lower()
        if lang not in self.SAMPLE_TRANSCRIPTS:
            lang = "en"

        duration = 5.0
        # Try inspecting WAV header if available
        if audio_bytes.startswith(b"RIFF") and len(audio_bytes) > 44:
            try:
                with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    if rate > 0:
                        duration = round(frames / float(rate), 2)
            except Exception:
                pass
        else:
            # Estimate from file size ~128kbps
            duration = max(1.0, round((len(audio_bytes) * 8) / 128000.0, 2))

        transcript = self.SAMPLE_TRANSCRIPTS.get(lang, self.SAMPLE_TRANSCRIPTS["en"])
        
        # Build timestamped segments
        segments = [
            {
                "id": str(uuid4()),
                "start": 0.0,
                "end": duration,
                "text": transcript,
                "speaker": "Preserved Speaker",
                "confidence": 0.98,
                "language": lang
            }
        ]

        return {
            "transcript": transcript,
            "language": lang,
            "duration_seconds": duration,
            "confidence": 0.98,
            "segments": segments,
            "is_mock": True,
            "provider_name": self.name,
            "model": self.model,
            "note": "SIMULATED OUTPUT: Mock Speech-to-Text provider used for demonstration/testing."
        }


class GeminiSTTProvider(BaseSTTProvider):
    """Multimodal STT provider powered by Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        super().__init__(name="GeminiSTTProvider", api_key=api_key, model=model)

    def get_health(self) -> ProviderHealth:
        if self.is_configured:
            return ProviderHealth(
                name=self.name,
                category=self.category,
                status=ProviderStatus.AVAILABLE,
                model=self.model,
                is_ready=True,
                message="Gemini Multimodal Speech-to-Text ready."
            )
        return ProviderHealth(
            name=self.name,
            category=self.category,
            status=ProviderStatus.UNCONFIGURED,
            model=self.model,
            is_ready=False,
            message="Gemini API key is not configured."
        )

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = "en") -> Dict[str, Any]:
        if not self.is_configured:
            raise ValueError("Gemini STT provider is unconfigured.")
        
        # Real integration uses google.genai / httpx if credentials present
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        prompt = (
            f"Transcribe this oral audio recording accurately into {language or 'English'}. "
            "Output only the transcribed text verbatim without commentary."
        )
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": "audio/wav", "data": audio_b64}}
                ]
            }]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {
                    "transcript": text,
                    "language": language or "en",
                    "duration_seconds": 5.0,
                    "confidence": 0.95,
                    "segments": [{"start": 0.0, "end": 5.0, "text": text, "confidence": 0.95}],
                    "is_mock": False,
                    "provider_name": self.name,
                    "model": self.model
                }
            else:
                raise RuntimeError(f"Gemini STT failed with status {resp.status_code}: {resp.text}")
