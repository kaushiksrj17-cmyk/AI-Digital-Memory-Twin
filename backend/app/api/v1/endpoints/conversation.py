"""Conversation API Endpoints for ECHO Memorial AI.

Supports session lifecycle management, grounded dialogue turns, export packages,
and backward-compatible legacy session endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from models.conversation import (
    ConversationSession,
    ConversationSessionCreate,
    Message,
)
from backend.app.services.conversation_service import conversation_service

router = APIRouter()


class PostMessageRequest(BaseModel):
    content: str
    user_id: Optional[str] = "default-user-001"
    memorial_profile_id: Optional[str] = None


# --- Canonical /conversations REST routes ---

@router.get("", response_model=List[ConversationSession])
@router.get("/sessions", response_model=List[ConversationSession])
async def list_conversations(profile_id: Optional[str] = None):
    """List interactive memorial dialogue sessions."""
    return await conversation_service.list_sessions(profile_id=profile_id)


@router.post("", response_model=ConversationSession, status_code=status.HTTP_201_CREATED)
async def create_conversation(data: ConversationSessionCreate):
    """Create a new conversational memorial dialogue session."""
    return await conversation_service.create_session(data)


@router.get("/{conversation_id}", response_model=ConversationSession)
@router.get("/sessions/{conversation_id}", response_model=ConversationSession)
async def get_conversation(conversation_id: str):
    """Retrieve full transcript and citations for a conversation session."""
    session = await conversation_service.get_session(conversation_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation session '{conversation_id}' not found."
        )
    return session


@router.post("/{conversation_id}/messages", response_model=Message)
@router.post("/sessions/{conversation_id}/messages", response_model=Message)
async def post_message(conversation_id: str, request: PostMessageRequest):
    """Post user inquiry, run evidence-grounded RAG, and receive validated assistant message."""
    try:
        return await conversation_service.post_message(
            session_id=conversation_id,
            content=request.content,
            user_id=request.user_id or "default-user-001",
            memorial_profile_id=request.memorial_profile_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post conversation message: {str(e)}"
        )


@router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(conversation_id: str):
    """Delete a conversation session."""
    success = await conversation_service.delete_session(conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation session '{conversation_id}' not found."
        )
    return {"status": "success", "message": f"Conversation session '{conversation_id}' deleted."}


@router.post("/{conversation_id}/export")
async def export_conversation(conversation_id: str) -> Dict[str, Any]:
    """Export conversation session transcript preserving questions, sources, confidence, and audits."""
    exported = await conversation_service.export_session(conversation_id)
    if not exported:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation session '{conversation_id}' not found for export."
        )
    return exported
