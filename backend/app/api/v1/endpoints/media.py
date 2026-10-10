"""Media API Endpoints.

Handles secure multimodal uploads into D:\\ECHO\\storage\\originals:
- File validation (extension, MIME, size, filename sanitization)
- SHA-256 cryptographic checksum calculation
- Duplicate detection (re-references existing files without duplicate disk writes)
- Image thumbnail generation
- Safe relative storage paths (Zero internal physical filesystem paths exposed)
- Privacy level clearance enforcement (RBAC)
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone

from storage.vault_storage import (
    vault_storage,
    UnsupportedFileTypeError,
    FileSizeLimitExceededError,
    MaliciousPathError
)
from models.enums import SourceType, PrivacyLevel, ProcessingStatus, AuditAction
from models.media import Media
from backend.app.services.audit_service import audit_service
from backend.app.core.security import get_current_user, can_access_privacy_level

router = APIRouter()

# In-memory registry for uploaded media metadata
media_registry: Dict[str, Media] = {
    "demo-media-001": Media(
        id="demo-media-001",
        file_name="graduation_portrait_1968.jpg",
        original_file_name="graduation_portrait_1968.jpg",
        media_type=SourceType.ORIGINAL_PHOTO,
        mime_type="image/jpeg",
        file_size_bytes=1420580,
        relative_storage_path="originals/demo_graduation_portrait_1968.jpg",
        thumbnail_path="thumbnails/demo_graduation_portrait_1968_thumb.jpg",
        description="Black and white formal portrait taken outside Wren Library courtyard.",
        captured_date="1968-06-22",
        privacy_level=PrivacyLevel.PRIVATE,
        sha256_checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        processing_status=ProcessingStatus.COMPLETED
    ),
    "demo-media-002": Media(
        id="demo-media-002",
        file_name="oral_history_interview_side_a.mp3",
        original_file_name="oral_history_interview_side_a.mp3",
        media_type=SourceType.ORIGINAL_AUDIO,
        mime_type="audio/mpeg",
        file_size_bytes=18450120,
        relative_storage_path="originals/demo_oral_history_interview_side_a.mp3",
        thumbnail_path=None,
        description="Preserved reel-to-reel cassette recording of childhood stories.",
        captured_date="1984-11-12",
        privacy_level=PrivacyLevel.PRIVATE,
        sha256_checksum="4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        processing_status=ProcessingStatus.COMPLETED
    )
}


@router.get("/", response_model=List[Media])
async def list_media(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """List preserved media assets in the vault filtered by privacy clearance."""
    role = current_user.get("role", "visitor")
    return [
        m for m in media_registry.values()
        if can_access_privacy_level(role, m.privacy_level.value)
    ]


@router.get("/{media_id}")
async def get_media_metadata_or_file(
    media_id: str,
    download: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve media record metadata or stream the safe relative file."""
    media = media_registry.get(media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found in vault")

    role = current_user.get("role", "visitor")
    if not can_access_privacy_level(role, media.privacy_level.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{role}' lacks clearance for {media.privacy_level.value} media"
        )

    if download:
        abs_path = vault_storage.get_absolute_path(media.relative_storage_path)
        if not abs_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical media file missing from storage")
        return FileResponse(
            path=str(abs_path),
            media_type=media.mime_type,
            filename=media.file_name
        )

    return media


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_media_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    captured_date: Optional[str] = Form(None),
    privacy_level: PrivacyLevel = Form(PrivacyLevel.PRIVATE),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Securely upload raw evidence media into D:\\ECHO\\storage\\originals.
    
    Performs:
    - Role authorization check
    - Path traversal rejection
    - Unsupported file rejection (Images, Videos, Audio, Documents only)
    - Cryptographic SHA-256 checksum calculation
    - Duplicate detection
    - Automated thumbnail generation for images
    """
    role = current_user.get("role", "visitor")
    if role not in ["vault_owner", "admin", "guardian", "family_member"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{role}' is not authorized to upload vault assets"
        )

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

        # Save through VaultStorageManager
        save_result = await vault_storage.save_original(
            original_filename=file.filename or "uploaded_media.bin",
            content=content,
            mime_type=file.content_type
        )

        # Infer source type from extension
        ext = (file.filename or "").lower()
        if ext.endswith((".jpg", ".jpeg", ".png", ".webp")):
            source_type = SourceType.ORIGINAL_PHOTO
        elif ext.endswith((".mp4", ".mov", ".webm")):
            source_type = SourceType.ORIGINAL_VIDEO
        elif ext.endswith((".mp3", ".wav", ".m4a")):
            source_type = SourceType.ORIGINAL_AUDIO
        else:
            source_type = SourceType.DOCUMENT

        media_id = str(uuid4())
        media = Media(
            id=media_id,
            file_name=save_result["original_filename"],
            original_file_name=save_result["original_filename"],
            media_type=source_type,
            mime_type=save_result["mime_type"],
            file_size_bytes=save_result["file_size"],
            relative_storage_path=save_result["storage_path"],
            thumbnail_path=save_result.get("thumbnail_path"),
            description=description,
            captured_date=captured_date,
            privacy_level=privacy_level,
            sha256_checksum=save_result["checksum"],
            processing_status=ProcessingStatus.COMPLETED,
            is_duplicate=save_result.get("is_duplicate", False)
        )
        media_registry[media.id] = media

        # Audit upload
        actor_id = current_user.get("id", "demo-user-001")
        await audit_service.record_event(
            action=AuditAction.UPLOAD,
            actor=actor_id,
            resource=f"Media:{media.id}",
            result="SUCCESS",
            metadata={
                "filename": media.file_name,
                "size_bytes": media.file_size_bytes,
                "is_duplicate": media.is_duplicate,
                "checksum": media.sha256_checksum
            }
        )

        return {
            "status": "success",
            "media_id": media.id,
            "file_name": media.file_name,
            "media_type": media.media_type,
            "mime_type": media.mime_type,
            "file_size_bytes": media.file_size_bytes,
            "storage_path": media.relative_storage_path,  # Safe relative path only
            "thumbnail_path": media.thumbnail_path,
            "checksum": media.sha256_checksum,
            "is_duplicate": media.is_duplicate,
            "message": save_result["message"]
        }

    except (UnsupportedFileTypeError, FileSizeLimitExceededError, MaliciousPathError) as e:
        await audit_service.record_event(
            action=AuditAction.UPLOAD,
            actor=current_user.get("id", "anonymous"),
            resource=f"Media:upload:{file.filename}",
            result="REJECTED",
            metadata={"error": str(e)},
            is_security_alert=isinstance(e, MaliciousPathError)
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload processing failed: {str(e)}")


@router.delete("/{media_id}", status_code=status.HTTP_200_OK)
async def delete_media(
    media_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Safely delete media asset and record audit trail."""
    role = current_user.get("role", "visitor")
    if role not in ["vault_owner", "admin", "guardian"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{role}' cannot delete media assets from vault"
        )

    media = media_registry.get(media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found in vault")

    # If not a duplicate pointing to shared file, safely remove from storage
    if not media.is_duplicate:
        await vault_storage.delete_file(media.relative_storage_path)
        if media.thumbnail_path:
            await vault_storage.delete_file(media.thumbnail_path)

    del media_registry[media_id]

    await audit_service.record_event(
        action=AuditAction.DELETE,
        actor=current_user.get("id", "demo-user-001"),
        resource=f"Media:{media_id}",
        result="SUCCESS",
        metadata={"filename": media.file_name}
    )

    return {"status": "success", "message": f"Media asset {media_id} removed safely from vault"}


# ==============================================================================
# Phase 3 Derived Extraction Sub-Endpoints
# ==============================================================================

@router.get("/{media_id}/metadata")
async def get_media_technical_metadata(
    media_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve normalized technical metadata for a media asset."""
    from backend.app.services.metadata_service import metadata_service
    media = media_registry.get(media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found in vault")

    role = current_user.get("role", "visitor")
    if not can_access_privacy_level(role, media.privacy_level.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{role}' lacks clearance for {media.privacy_level.value} media metadata"
        )

    meta = metadata_service.get_metadata(media_id)
    if meta:
        return meta
    
    # Generate on the fly
    return metadata_service.normalize_metadata(
        media_id=media.id,
        media_type=media.media_type.value,
        filename=media.file_name,
        mime_type=media.mime_type,
        file_size=media.file_size_bytes,
        checksum=media.sha256_checksum or "unknown",
        technical_data=media.metadata_extracted or {}
    )


@router.get("/{media_id}/ocr")
async def get_media_ocr_results(
    media_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve OCR results for a media asset."""
    from backend.app.services.ocr_service import ocr_service
    media = media_registry.get(media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found in vault")

    role = current_user.get("role", "visitor")
    if not can_access_privacy_level(role, media.privacy_level.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{role}' lacks clearance for {media.privacy_level.value} media"
        )
    
    return await ocr_service.extract_ocr(
        media_id=media.id,
        relative_path=media.relative_storage_path
    )


@router.get("/{media_id}/transcript")
async def get_media_transcript_results(
    media_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve audio transcript for a media asset."""
    from backend.app.services.transcription_service import transcription_service
    media = media_registry.get(media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found in vault")

    role = current_user.get("role", "visitor")
    if not can_access_privacy_level(role, media.privacy_level.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{role}' lacks clearance for {media.privacy_level.value} media"
        )
    
    return await transcription_service.transcribe_audio(
        media_id=media.id,
        relative_path=media.relative_storage_path
    )


@router.get("/{media_id}/keyframes")
async def get_media_keyframes_results(
    media_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve extracted keyframe snapshots for a video asset."""
    from backend.app.services.video_processor import video_processor
    media = media_registry.get(media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found in vault")

    role = current_user.get("role", "visitor")
    if not can_access_privacy_level(role, media.privacy_level.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{role}' lacks clearance for {media.privacy_level.value} media"
        )
    
    res = await video_processor.process_video(
        media_id=media.id,
        relative_path=media.relative_storage_path
    )
    return res.get("keyframes", [])
