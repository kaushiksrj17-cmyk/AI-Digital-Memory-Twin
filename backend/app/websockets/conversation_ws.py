"""WebSocket Endpoint for Real-Time Memorial Dialogue.

Emits streaming-ready lifecycle events:
- RETRIEVING
- CONTEXT_READY
- GENERATING
- VALIDATING
- COMPLETED / BLOCKED / ERROR
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from backend.app.services.conversation_service import conversation_service
from backend.app.services.rag_service import get_rag_service
from models.conversation import ETHICAL_DISCLAIMER_TEXT, RAGQueryRequest
from models.enums import GuardianDecision

logger = logging.getLogger("echo.ws")
ws_router = APIRouter()


@ws_router.websocket("/ws/conversation/{session_id}")
async def websocket_conversation_endpoint(websocket: WebSocket, session_id: str):
    """Real-time bidirectional WebSocket stream for evidence-grounded dialogue with lifecycle events."""
    await websocket.accept()
    logger.info(f"WebSocket client connected to session: {session_id}")

    # Send initial handshake with mandatory ethical boundary banner
    await websocket.send_json({
        "type": "connection_established",
        "session_id": session_id,
        "ethical_disclaimer": ETHICAL_DISCLAIMER_TEXT,
        "status": "ready"
    })

    rag_service = get_rag_service()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_text = payload.get("content", "")
            profile_id = payload.get("memorial_profile_id", "default-profile-001")

            if not user_text:
                continue

            # Event 1: RETRIEVING
            await websocket.send_json({
                "type": "event",
                "event": "RETRIEVING",
                "session_id": session_id,
                "message": "Searching preserved archive across vector, keyword, and knowledge graph indexes..."
            })

            # Event 2: CONTEXT_READY
            await websocket.send_json({
                "type": "event",
                "event": "CONTEXT_READY",
                "session_id": session_id,
                "message": "Archival evidence retrieved and ranked."
            })

            # Event 3: GENERATING
            await websocket.send_json({
                "type": "event",
                "event": "GENERATING",
                "session_id": session_id,
                "message": "Synthesizing evidence-grounded memorial response..."
            })

            # Process through conversation service
            ai_message = await conversation_service.post_message(
                session_id=session_id,
                content=user_text,
                memorial_profile_id=profile_id,
            )

            # Event 4: VALIDATING
            await websocket.send_json({
                "type": "event",
                "event": "VALIDATING",
                "session_id": session_id,
                "message": "Executing 18 Memory Guardian evidentiary and boundary audits..."
            })

            # Event 5: COMPLETED or BLOCKED
            is_blocked = ai_message.guardian_status == GuardianDecision.BLOCK
            event_type = "BLOCKED" if is_blocked else "COMPLETED"

            await websocket.send_json({
                "type": "event",
                "event": event_type,
                "session_id": session_id,
                "message": "Response passed evidentiary audits." if not is_blocked else "Response blocked by policy."
            })

            # Final response delivery
            await websocket.send_json({
                "type": "message",
                "message": ai_message.model_dump(mode="json")
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error in session {session_id}: {str(e)}")
        try:
            await websocket.send_json({
                "type": "event",
                "event": "ERROR",
                "error": str(e)
            })
            await websocket.close()
        except Exception:
            pass


@ws_router.websocket("/ws/voice/{session_id}")
async def websocket_voice_endpoint(websocket: WebSocket, session_id: str):
    """Real-time bidirectional WebSocket stream for voice processing with state machine events."""
    await websocket.accept()
    logger.info(f"Voice WebSocket connected for session: {session_id}")

    # Initial handshake
    await websocket.send_json({
        "type": "connection_established",
        "session_id": session_id,
        "state": "IDLE",
        "ethical_disclaimer": ETHICAL_DISCLAIMER_TEXT,
        "disclosure": "AI-GENERATED MEMORIAL VOICE — SYNTHETIC AUDIO, NOT AN ORIGINAL RECORDING."
    })

    from backend.app.services.speech_service import speech_service
    from backend.app.services.voice_session_service import voice_session_service
    from models.voice import VoiceTranscriptQueryRequest

    try:
        while True:
            raw_text = await websocket.receive_text()
            payload = json.loads(raw_text)
            action = payload.get("action", "").upper()
            profile_id = payload.get("memorial_profile_id", "default-profile-001")
            user_id = payload.get("user_id", "demo-user-001")
            voice_profile_id = payload.get("voice_profile_id")
            language = payload.get("language", "en")

            if action == "RECORDING_STARTED":
                await websocket.send_json({
                    "type": "event",
                    "event": "RECORDING",
                    "session_id": session_id,
                    "message": "Microphone recording active."
                })
            elif action == "SUBMIT_AUDIO_BASE64":
                audio_b64 = payload.get("audio_base64", "")
                if not audio_b64:
                    continue

                import base64
                audio_bytes = base64.b64decode(audio_b64)

                await websocket.send_json({
                    "type": "event",
                    "event": "UPLOADING",
                    "session_id": session_id,
                    "message": "Uploading and validating audio stream..."
                })

                await websocket.send_json({
                    "type": "event",
                    "event": "TRANSCRIBING",
                    "session_id": session_id,
                    "message": "Extracting speech-to-text transcript..."
                })

                await websocket.send_json({
                    "type": "event",
                    "event": "RETRIEVING",
                    "session_id": session_id,
                    "message": "Querying Memory Vault across Vector, Keyword, and Knowledge Graph..."
                })

                resp = await speech_service.execute_voice_pipeline(
                    audio_bytes=audio_bytes,
                    filename=payload.get("filename", "recording.wav"),
                    language=language,
                    session_id=session_id,
                    memorial_profile_id=profile_id,
                    voice_profile_id=voice_profile_id,
                    user_id=user_id
                )

                final_event = "BLOCKED" if resp.synthesis_blocked else "COMPLETED"
                await websocket.send_json({
                    "type": "event",
                    "event": final_event,
                    "session_id": session_id,
                    "message": "Voice interaction pipeline finished."
                })

                await websocket.send_json({
                    "type": "voice_response",
                    "data": resp.model_dump(mode="json")
                })

            elif action == "SUBMIT_TRANSCRIPT":
                transcript = payload.get("transcript", "")
                is_edited = bool(payload.get("is_edited", False))

                await websocket.send_json({
                    "type": "event",
                    "event": "RETRIEVING",
                    "session_id": session_id,
                    "message": "Retrieving archival evidence..."
                })

                await websocket.send_json({
                    "type": "event",
                    "event": "VALIDATING",
                    "session_id": session_id,
                    "message": "Running Memory Guardian evidentiary and boundary audits..."
                })

                resp = await speech_service.execute_transcript_query(
                    request=VoiceTranscriptQueryRequest(
                        session_id=session_id,
                        transcript_text=transcript,
                        is_edited=is_edited,
                        voice_profile_id=voice_profile_id,
                        language=language,
                        synthesize_audio=True
                    ),
                    user_id=user_id,
                    memorial_profile_id=profile_id
                )

                final_event = "BLOCKED" if resp.synthesis_blocked else "COMPLETED"
                await websocket.send_json({
                    "type": "event",
                    "event": final_event,
                    "session_id": session_id,
                    "message": "Voice query completed."
                })

                await websocket.send_json({
                    "type": "voice_response",
                    "data": resp.model_dump(mode="json")
                })

            elif action == "CANCEL":
                await voice_session_service.cancel_session(session_id)
                await websocket.send_json({
                    "type": "event",
                    "event": "CANCELLED",
                    "session_id": session_id,
                    "message": "Voice session cancelled by user."
                })

    except WebSocketDisconnect:
        logger.info(f"Voice WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Voice WebSocket error in {session_id}: {str(e)}")
        try:
            await websocket.send_json({
                "type": "event",
                "event": "ERROR",
                "error": str(e)
            })
            await websocket.close()
        except Exception:
            pass
