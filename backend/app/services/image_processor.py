"""Image Processing Service for ECHO.

Processes images (JPG, JPEG, PNG, WEBP):
- File validation
- Technical metadata extraction (dimensions, format, EXIF, orientation, capture date)
- Thumbnail generation (preserves original)
- Visual evidence extraction (pluggable vision provider)
- Strict adherence to evidence boundaries: if vision provider is unconfigured,
  never fabricates scene/object descriptions; returns UNCONFIGURED/PROCESSING_LIMITED.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image, ExifTags
import io
import os
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import (
    ConfidenceLevel,
    ProvenanceStatus,
    EvidenceType,
    SourceType
)
from models.evidence import Evidence
from storage.vault_storage import vault_storage
from ai.providers.factory import provider_registry


class ImageProcessor:
    """Specialized multimodal processor for photographic and scanned image assets."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(self):
        self.processor_name = "ImageProcessor"
        self.processor_version = "echo-img-v1.0"

    async def process_image(
        self,
        media_id: str,
        relative_path: str,
        memory_id: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process an image asset and generate structured evidence artifacts."""
        ext = Path(relative_path).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported image format: {ext}")

        abs_path = vault_storage.get_absolute_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Media file missing from storage: {relative_path}")

        image_bytes = abs_path.read_bytes()
        file_size = len(image_bytes)

        # 1. Technical Metadata Extraction
        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size
            img_format = img.format or ext.replace(".", "").upper()
            
            # EXIF extraction
            exif_data = {}
            capture_date = None
            camera_make = None
            camera_model = None
            orientation = None

            try:
                raw_exif = img.getexif()
                if raw_exif:
                    for tag_id, val in raw_exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        # Filter out non-serializable bytes
                        if isinstance(val, (bytes, bytearray)):
                            continue
                        exif_data[tag_name] = str(val)

                    capture_date = exif_data.get("DateTimeOriginal") or exif_data.get("DateTime")
                    camera_make = exif_data.get("Make")
                    camera_model = exif_data.get("Model")
                    orientation = exif_data.get("Orientation")
            except Exception:
                pass  # Corrupted or unreadable EXIF

        technical_metadata = {
            "width": width,
            "height": height,
            "format": img_format,
            "file_size": file_size,
            "exif_available": bool(exif_data),
            "capture_date": capture_date,
            "camera_make": camera_make,
            "camera_model": camera_model,
            "orientation": orientation,
            "aspect_ratio": round(width / max(height, 1), 2),
            "raw_exif": exif_data
        }

        # 2. Thumbnail verification/generation
        thumb_name = f"{abs_path.stem[:16]}_thumb.jpg"
        thumb_rel_path = f"thumbnails/{thumb_name}"
        thumb_abs_path = vault_storage.get_absolute_path(thumb_rel_path)
        if not thumb_abs_path.exists():
            thumb_rel_path = await vault_storage._generate_image_thumbnail(image_bytes, abs_path.stem)

        evidence_items: List[Evidence] = []

        # Technical metadata evidence (DIRECTLY_OBSERVED, VERIFIED)
        meta_evidence = Evidence(
            id=str(uuid4()),
            memory_id=memory_id,
            media_id=media_id,
            title="Image Technical Characteristics",
            evidence_type=EvidenceType.IMAGE_METADATA,
            content=f"Image dimensions {width}x{height}px, format {img_format}, size {file_size} bytes.",
            structured_value=technical_metadata,
            source_reference=f"EXIF/File Header ({abs_path.name})",
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            confidence=ConfidenceLevel.VERIFIED,
            confidence_score=1.0,
            extraction_method="pillow_header_inspection",
            processor_version=self.processor_version
        )
        evidence_items.append(meta_evidence)

        # 3. Visual Understanding via Vision Provider
        vision_provider = provider_registry.vision_provider
        vision_health = vision_provider.get_health()
        
        # Check if real vision model is configured (or test flag enabled)
        is_provider_ready = vision_provider.is_configured or os.getenv("ENABLE_VISION_MOCK", "false").lower() == "true"

        if is_provider_ready:
            try:
                analysis = await vision_provider.analyze_image(image_bytes)
                desc = analysis.get("description", "")
                objects = analysis.get("detected_objects", [])
                faces = analysis.get("detected_faces_count", 0)

                scene_evidence = Evidence(
                    id=str(uuid4()),
                    memory_id=memory_id,
                    media_id=media_id,
                    title="Visual Scene Analysis",
                    evidence_type=EvidenceType.VISUAL_SCENE,
                    content=desc or "Visual scene analysis produced by vision model.",
                    structured_value={
                        "description": desc,
                        "detected_objects": objects,
                        "detected_faces_count": faces,
                        "provider": vision_provider.name
                    },
                    source_reference=f"Vision Model: {vision_provider.model}",
                    provenance_status=ProvenanceStatus.AI_INFERRED,
                    confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
                    confidence_score=0.85,
                    extraction_method=vision_provider.name,
                    processor_version=self.processor_version
                )
                evidence_items.append(scene_evidence)
                vision_status = "COMPLETED"
                vision_message = "Visual feature extraction complete."
            except Exception as e:
                vision_status = "FAILED"
                vision_message = f"Vision provider execution failed: {str(e)}"
        else:
            # Strictly do NOT fabricate scene descriptions when provider is unconfigured
            vision_status = "UNCONFIGURED"
            vision_message = "Vision model unconfigured. Preserved original image and technical metadata without fabrication."

        return {
            "media_id": media_id,
            "processor": self.processor_name,
            "processor_version": self.processor_version,
            "technical_metadata": technical_metadata,
            "thumbnail_path": thumb_rel_path,
            "evidence": evidence_items,
            "vision_status": vision_status,
            "message": vision_message
        }


image_processor = ImageProcessor()
