"""Optical Character Recognition (OCR) Service for ECHO.

Processes scanned letters, handwritten diaries, historical documents, and certificates.
Architectural support for English, Tamil, and Hindi.
Strict evidence boundary: If OCR provider is unconfigured, returns an explicit
UNCONFIGURED result and never fabricates extracted text.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import os

from models.enums import (
    ConfidenceLevel,
    ProvenanceStatus,
    EvidenceType
)
from models.evidence import Evidence
from models.processing import OCRResult
from storage.vault_storage import vault_storage
from ai.providers.factory import provider_registry


class OCRService:
    """Specialized OCR extraction service for evidentiary digitization."""

    SUPPORTED_LANGUAGES = ["en", "ta", "hi"]

    def __init__(self):
        self.service_name = "OCRService"
        self.processor_version = "echo-ocr-v1.0"

    async def extract_ocr(
        self,
        media_id: str,
        relative_path: str,
        memory_id: Optional[str] = None,
        target_language: str = "en"
    ) -> OCRResult:
        """Extract text from an image or scanned document using configured OCR provider."""
        abs_path = vault_storage.get_absolute_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Source file not found: {relative_path}")

        ocr_provider = provider_registry.ocr_provider
        is_provider_ready = ocr_provider.is_configured or os.getenv("ENABLE_OCR_MOCK", "false").lower() == "true"

        if not is_provider_ready:
            # Explicitly return unconfigured result. Never fabricate text!
            return OCRResult(
                media_id=media_id,
                memory_id=memory_id,
                status="UNCONFIGURED",
                extracted_text="",
                pages=[],
                language=target_language,
                supported_languages=self.SUPPORTED_LANGUAGES,
                confidence=0.0,
                provenance=ProvenanceStatus.UNKNOWN,
                message="OCR provider is not configured. Preserved original document without fabricating text."
            )

        document_bytes = abs_path.read_bytes()
        try:
            result = await ocr_provider.extract_text(document_bytes)
            extracted_text = result.get("extracted_text", "")
            confidence = float(result.get("confidence", 0.9))

            return OCRResult(
                media_id=media_id,
                memory_id=memory_id,
                status="COMPLETED",
                extracted_text=extracted_text,
                pages=[{
                    "page_number": 1,
                    "text": extracted_text,
                    "confidence": confidence,
                    "language": target_language
                }],
                language=target_language,
                supported_languages=self.SUPPORTED_LANGUAGES,
                confidence=confidence,
                provenance=ProvenanceStatus.DIRECTLY_OBSERVED,
                extraction_timestamp=datetime.now(timezone.utc),
                message="OCR digitization completed successfully."
            )
        except Exception as e:
            return OCRResult(
                media_id=media_id,
                memory_id=memory_id,
                status="FAILED",
                extracted_text="",
                pages=[],
                language=target_language,
                supported_languages=self.SUPPORTED_LANGUAGES,
                confidence=0.0,
                provenance=ProvenanceStatus.UNKNOWN,
                message=f"OCR processing failed: {str(e)}"
            )

    def create_ocr_evidence(
        self,
        ocr_result: OCRResult,
        source_filename: str
    ) -> Optional[Evidence]:
        """Convert a successful OCR result into an atomic Evidence record."""
        if ocr_result.status != "COMPLETED" or not ocr_result.extracted_text.strip():
            return None

        return Evidence(
            id=str(uuid4()),
            memory_id=ocr_result.memory_id,
            media_id=ocr_result.media_id,
            title=f"OCR Extracted Document Text ({ocr_result.language.upper()})",
            evidence_type=EvidenceType.OCR_TEXT,
            content=ocr_result.extracted_text,
            structured_value={
                "language": ocr_result.language,
                "confidence_score": ocr_result.confidence,
                "page_count": len(ocr_result.pages),
                "is_ocr": True
            },
            source_reference=f"Scanned Document ({source_filename})",
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            confidence=ConfidenceLevel.VERIFIED if ocr_result.confidence >= 0.8 else ConfidenceLevel.SUPPORTED_INFERENCE,
            confidence_score=ocr_result.confidence,
            extraction_method="ocr_digitizer",
            processor_version=self.processor_version
        )


ocr_service = OCRService()
