"""ECHO Services Package."""

from backend.app.services.memory_service import memory_service, MemoryService
from backend.app.services.confidence_service import confidence_service, ConfidenceService
from backend.app.services.provenance_service import provenance_service, ProvenanceService
from backend.app.services.conversation_service import conversation_service, ConversationService
from backend.app.services.guardian_service import guardian_service, MemoryGuardianService
from backend.app.services.audit_service import audit_service, AuditService
from backend.app.services.consent_service import consent_service, ConsentService
from backend.app.services.image_processor import image_processor, ImageProcessor
from backend.app.services.audio_processor import audio_processor, AudioProcessor
from backend.app.services.video_processor import video_processor, VideoProcessor
from backend.app.services.document_processor import document_processor, DocumentProcessor
from backend.app.services.ocr_service import ocr_service, OCRService
from backend.app.services.transcription_service import transcription_service, TranscriptionService
from backend.app.services.metadata_service import metadata_service, MetadataService
from backend.app.services.entity_extractor import entity_extractor, EntityExtractor
from backend.app.services.event_extractor import event_extractor, EventExtractor
from backend.app.services.processing_orchestrator import processing_orchestrator, ProcessingOrchestrator
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import LocalVectorStore, get_vector_store
from backend.app.services.knowledge_graph_service import KnowledgeGraphService, LocalGraphStore, get_graph_store
from backend.app.services.relationship_service import RelationshipService
from backend.app.services.entity_resolution_service import EntityResolutionService
from backend.app.services.contradiction_service import ContradictionService, get_contradiction_service
from backend.app.services.retrieval_service import RetrievalService, get_retrieval_service
from backend.app.services.memory_dna_service import MemoryDNAService, get_memory_dna_service
# Phase 5 Services
from backend.app.services.question_classifier import QuestionClassifier, get_question_classifier
from backend.app.services.prompt_engine import PromptEngine, get_prompt_engine
from backend.app.services.context_manager import ContextManager, get_context_manager
from backend.app.services.hallucination_detector import HallucinationDetector, get_hallucination_detector
from backend.app.services.claim_extractor import ClaimExtractor, get_claim_extractor
from backend.app.services.memory_guardian import MemoryGuardian, get_memory_guardian
from backend.app.services.confidence_engine import ConfidenceEngine, get_confidence_engine
from backend.app.services.provenance_engine import ProvenanceEngine, get_provenance_engine
from backend.app.services.rag_service import RAGService, get_rag_service
# Phase 6 Voice Services
from backend.app.services.voice_provider import voice_provider_service, VoiceProviderService
from backend.app.services.voice_consent_service import voice_consent_service, VoiceConsentService
from backend.app.services.voice_profile_service import voice_profile_service, VoiceProfileService
from backend.app.services.tts_service import tts_service, TTSService
from backend.app.services.voice_session_service import voice_session_service, VoiceSessionService
from backend.app.services.speech_service import speech_service, SpeechService

__all__ = [
    "memory_service",
    "MemoryService",
    "confidence_service",
    "ConfidenceService",
    "provenance_service",
    "ProvenanceService",
    "conversation_service",
    "ConversationService",
    "guardian_service",
    "MemoryGuardianService",
    "audit_service",
    "AuditService",
    "consent_service",
    "ConsentService",
    "image_processor",
    "ImageProcessor",
    "audio_processor",
    "AudioProcessor",
    "video_processor",
    "VideoProcessor",
    "document_processor",
    "DocumentProcessor",
    "ocr_service",
    "OCRService",
    "transcription_service",
    "TranscriptionService",
    "metadata_service",
    "MetadataService",
    "entity_extractor",
    "EntityExtractor",
    "event_extractor",
    "EventExtractor",
    "processing_orchestrator",
    "ProcessingOrchestrator",
    # Phase 4 Services
    "ChunkingService",
    "EmbeddingService",
    "LocalVectorStore",
    "get_vector_store",
    "KnowledgeGraphService",
    "LocalGraphStore",
    "get_graph_store",
    "RelationshipService",
    "EntityResolutionService",
    "ContradictionService",
    "get_contradiction_service",
    "RetrievalService",
    "get_retrieval_service",
    "MemoryDNAService",
    "get_memory_dna_service",
    # Phase 5 Services
    "QuestionClassifier",
    "get_question_classifier",
    "PromptEngine",
    "get_prompt_engine",
    "ContextManager",
    "get_context_manager",
    "HallucinationDetector",
    "get_hallucination_detector",
    "ClaimExtractor",
    "get_claim_extractor",
    "MemoryGuardian",
    "get_memory_guardian",
    "ConfidenceEngine",
    "get_confidence_engine",
    "ProvenanceEngine",
    "get_provenance_engine",
    "RAGService",
    "get_rag_service",
    # Phase 6 Services
    "voice_provider_service",
    "VoiceProviderService",
    "voice_consent_service",
    "VoiceConsentService",
    "voice_profile_service",
    "VoiceProfileService",
    "tts_service",
    "TTSService",
    "voice_session_service",
    "VoiceSessionService",
    "speech_service",
    "SpeechService",
]


