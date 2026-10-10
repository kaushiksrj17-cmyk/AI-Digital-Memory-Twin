// ==============================================================================
// ECHO Frontend TypeScript Definitions — Phase 2 Extended
// ==============================================================================

export type ConfidenceLevel = 'VERIFIED' | 'SUPPORTED_INFERENCE' | 'UNKNOWN_UNSUPPORTED';

export type MemoryCategory =
  | 'CHILDHOOD'
  | 'EDUCATION'
  | 'CAREER'
  | 'FAMILY'
  | 'FRIENDS'
  | 'TRAVEL'
  | 'HOBBIES'
  | 'ACHIEVEMENTS'
  | 'SPECIAL_EVENTS'
  | 'PERSONAL_STORIES'
  | 'OTHER';

export type SourceType =
  | 'ORIGINAL_PHOTO'
  | 'ORIGINAL_VIDEO'
  | 'ORIGINAL_AUDIO'
  | 'DOCUMENT'
  | 'FAMILY_STORY'
  | 'USER_ENTRY'
  | 'AI_GENERATED'
  // Backward compatibility
  | 'PHOTOGRAPH'
  | 'VIDEO'
  | 'AUDIO_RECORDING'
  | 'LETTER'
  | 'BIOGRAPHY'
  | 'OFFICIAL_RECORD'
  | 'PERSONAL_NOTE'
  | 'DIARY';

export type VerificationStatus =
  | 'VERIFIED'
  | 'PENDING_REVIEW'
  | 'REJECTED'
  | 'UNKNOWN'
  // Backward compatibility
  | 'UNREVIEWED'
  | 'PENDING_VERIFICATION'
  | 'VERIFIED_BY_FAMILY'
  | 'VERIFIED_BY_DOCUMENT'
  | 'DISPUTED';

export type PrivacyLevel =
  | 'PRIVATE'
  | 'FAMILY'
  | 'AUTHORIZED_USERS'
  // Backward compatibility
  | 'FAMILY_ONLY'
  | 'MEMORIAL_PUBLIC'
  | 'RESTRICTED';

export type ConsentType =
  | 'MEDIA_PROCESSING'
  | 'AI_PROCESSING'
  | 'VOICE_PROCESSING'
  | 'AVATAR_PROCESSING'
  | 'FAMILY_ACCESS';

export type ConsentStatus = 'GRANTED' | 'REVOKED' | 'EXPIRED' | 'PENDING';

export type ProcessingStatus =
  | 'PENDING'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'FAILED'
  | 'REVIEW_REQUIRED';

export type AuditAction =
  | 'UPLOAD'
  | 'VIEW'
  | 'EDIT'
  | 'DELETE'
  | 'ARCHIVE'
  | 'EXPORT'
  | 'VERIFY'
  | 'REJECT'
  | 'CONSENT_GRANTED'
  | 'CONSENT_REVOKED'
  | 'PRIVACY_CHANGED';

export interface ProvenanceRecord {
  source_id: string;
  source_type: SourceType;
  source_title: string;
  source_reference: string;
  evidence_text: string;
  confidence: ConfidenceLevel;
  confidence_score: number;
  provenance_status: string;
  citation_label: string;
}

export interface Memory {
  id: string;
  memory_id?: string;
  memorial_profile_id: string;
  title: string;
  description: string;
  narrative?: string;
  summary?: string;
  category: MemoryCategory;
  source_type: SourceType;
  confidence: ConfidenceLevel;
  verification_status: VerificationStatus;
  confidence_score: number;
  privacy_level: PrivacyLevel;
  consent_status: ConsentStatus;
  date?: string;
  approximate_date?: string;
  location?: string;
  location_name?: string;
  people?: string[];
  people_ids?: string[];
  original_filename?: string;
  mime_type?: string;
  file_size?: number;
  storage_path?: string;
  thumbnail_path?: string;
  checksum?: string;
  processing_status?: ProcessingStatus;
  archived?: boolean;
  uploaded_by?: string;
  tags: string[];
  provenance_records: ProvenanceRecord[];
  created_at: string;
  updated_at?: string;
}

export interface ConsentRecord {
  id: string;
  consent_id?: string;
  memorial_profile_id: string;
  user_id: string;
  granter_name: string;
  granter_relationship: string;
  consent_type: ConsentType;
  scope: string;
  status: ConsentStatus;
  document_reference?: string;
  memory_id?: string;
  media_id?: string;
  notes?: string;
  created_at: string;
  granted_at?: string;
  revoked_at?: string;
}

export interface AuditLogEntry {
  id: string;
  actor: string;
  action: AuditAction;
  resource: string;
  result: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface LifeEvent {
  id: string;
  memorial_profile_id: string;
  title: string;
  event_category: string;
  event_date?: string;
  date_description?: string;
  location_name?: string;
  narrative?: string;
  confidence: ConfidenceLevel;
  people_ids?: string[];
  evidence_ids?: string[];
}

export interface Person {
  id: string;
  memorial_profile_id: string;
  full_name: string;
  nickname?: string;
  relationship_to_subject: string;
  biographical_note?: string;
  avatar_media_id?: string;
  is_deceased?: boolean;
}

export interface Relationship {
  id: string;
  memorial_profile_id: string;
  person_a_id: string;
  person_b_id: string;
  relationship_type: string;
  description?: string;
  start_year?: number;
  end_year?: number;
  closeness_rating?: number;
}

export type ProvenanceStatus =
  | 'DIRECTLY_OBSERVED'
  | 'USER_PROVIDED'
  | 'AI_INFERRED'
  | 'UNKNOWN';

export type EvidenceType =
  | 'TEXT'
  | 'OCR_TEXT'
  | 'TRANSCRIPT'
  | 'IMAGE_METADATA'
  | 'VISUAL_OBJECT'
  | 'VISUAL_SCENE'
  | 'VIDEO_KEYFRAME'
  | 'ENTITY'
  | 'EVENT'
  | 'LOCATION'
  | 'DATE'
  | 'AUDIO_METADATA'
  | 'VIDEO_METADATA'
  | 'DOCUMENT_METADATA';

export type EntityType =
  | 'PERSON'
  | 'LOCATION'
  | 'ORGANIZATION'
  | 'OBJECT'
  | 'DATE'
  | 'EVENT'
  | 'DOCUMENT'
  | 'MEDIA';

export type EventType =
  | 'BIRTH'
  | 'CHILDHOOD'
  | 'EDUCATION'
  | 'CAREER'
  | 'FAMILY'
  | 'FRIENDSHIP'
  | 'TRAVEL'
  | 'ACHIEVEMENT'
  | 'CELEBRATION'
  | 'IMPORTANT_EVENT'
  | 'PERSONAL_STORY'
  | 'OTHER';

export interface Evidence {
  id: string;
  evidence_id?: string;
  memorial_profile_id?: string;
  memory_id?: string;
  media_id?: string;
  title: string;
  evidence_type?: EvidenceType;
  source_type?: SourceType;
  content?: string;
  raw_content_excerpt?: string;
  structured_value?: Record<string, any>;
  source_reference?: string;
  source_citation?: string;
  provenance_status?: ProvenanceStatus;
  confidence: ConfidenceLevel;
  confidence_score?: number;
  extraction_method?: string;
  processor_version?: string;
  verification_status?: VerificationStatus;
  created_at?: string;
  updated_at?: string;
}

export interface ProcessingJob {
  id: string;
  media_id: string;
  memory_id?: string;
  processor: string;
  processing_status: ProcessingStatus;
  processing_version: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  retry_count: number;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface EntityRecord {
  id: string;
  entity_type: EntityType;
  value: string;
  source_media_id?: string;
  source_memory_id?: string;
  provenance_status: ProvenanceStatus;
  confidence: ConfidenceLevel;
  confidence_score: number;
  extraction_method: string;
  created_at: string;
}

export interface ExtractedEventRecord {
  id: string;
  title: string;
  description?: string;
  event_type: EventType;
  date?: string;
  approximate_date?: string;
  location?: string;
  people?: string[];
  source_media_id?: string;
  source_memory_id?: string;
  provenance_status: ProvenanceStatus;
  confidence: ConfidenceLevel;
  confidence_score: number;
  extraction_method: string;
  created_at: string;
}

export interface ProcessingAnalytics {
  total_memories: number;
  total_media: number;
  pending_jobs: number;
  processing_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  review_required_jobs: number;
  ocr_processed_count: number;
  audio_transcribed_count: number;
  video_processed_count: number;
  documents_processed_count: number;
  images_processed_count: number;
  average_latency_ms: number;
  total_evidence_items: number;
  confidence_distribution: Record<string, number>;
}

export interface MediaMetadataRecord {
  media_id: string;
  memory_id?: string;
  media_type: string;
  filename: string;
  mime_type: string;
  file_size: number;
  checksum: string;
  capture_date?: string;
  approximate_date?: string;
  location_name?: string;
  language?: string;
  duration_seconds?: number;
  width?: number;
  height?: number;
  fps?: number;
  channels?: number;
  sample_rate?: number;
  page_count?: number;
  character_count?: number;
  provenance_status: ProvenanceStatus;
  processing_version: string;
  created_at: string;
}

export interface OCRResultData {
  text: string;
  page_number?: number;
  language: string;
  confidence: number;
  source_media_id: string;
  extraction_timestamp: string;
  provenance_status: ProvenanceStatus;
  message?: string;
}

export interface TranscriptResultData {
  full_text: string;
  duration_seconds: number;
  language: string;
  provider: string;
  segments: Array<{
    segment_id: string;
    start_time: number;
    end_time: number;
    text: string;
    speaker?: string;
    confidence: number;
    language: string;
  }>;
  provenance_status: ProvenanceStatus;
  message?: string;
}

export interface KeyframeRecord {
  keyframe_id: string;
  media_id: string;
  timestamp_seconds: number;
  frame_number: number;
  storage_path: string;
  thumbnail_path?: string;
  created_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  ethical_disclaimer: string;
  confidence: ConfidenceLevel;
  confidence_score?: number;
  is_ai_generated: boolean;
  guardian_status?: GuardianDecision;
  provenance_citations?: ProvenanceRecord[];
  sources?: ResponseSource[];
  claims?: ResponseClaim[];
  contradictions?: Array<Record<string, any>>;
  warnings?: string[];
  contains_unsupported_claims?: boolean;
  retrieval_context_summary?: string;
  timestamp: string;
}

export interface ConversationSession {
  id: string;
  memorial_profile_id?: string;
  user_id?: string;
  title: string;
  topic_summary?: string;
  ethical_boundary_acknowledged?: boolean;
  created_at: string;
  updated_at?: string;
  messages: Message[];
}


export interface DashboardStats {
  total_memories: number;
  verified_memories: number;
  supported_inferences: number;
  unknown_unsupported: number;
  photos_count: number;
  videos_count: number;
  audio_count: number;
  documents_count: number;
  people_count: number;
  life_events_count: number;
  conversation_sessions_count: number;
  privacy_status: string;
  is_demonstration_mode: boolean;
}

// ==============================================================================
// Phase 4 Memory DNA, Knowledge Graph & Vector Retrieval Types
// ==============================================================================

export type MemoryDNACategory =
  | 'IDENTITY'
  | 'FAMILY'
  | 'RELATIONSHIPS'
  | 'CHILDHOOD'
  | 'EDUCATION'
  | 'CAREER'
  | 'FRIENDS'
  | 'HOBBIES'
  | 'INTERESTS'
  | 'TRAVEL'
  | 'ACHIEVEMENTS'
  | 'IMPORTANT_EVENTS'
  | 'PLACES'
  | 'IMPORTANT_OBJECTS'
  | 'DOCUMENTED_PREFERENCES'
  | 'DOCUMENTED_VALUES'
  | 'KNOWN_PHRASES'
  | 'FREQUENT_TOPICS'
  | 'PERSONAL_STORIES'
  | 'LEGACY'
  | 'UNKNOWN';

export type GraphNodeType =
  | 'PERSON'
  | 'MEMORY'
  | 'EVENT'
  | 'PLACE'
  | 'OBJECT'
  | 'DOCUMENT'
  | 'MEDIA'
  | 'ORGANIZATION'
  | 'DATE'
  | 'TOPIC';

export type GraphRelationshipType =
  | 'RELATED_TO'
  | 'APPEARED_IN'
  | 'PARTICIPATED_IN'
  | 'ASSOCIATED_WITH'
  | 'OWNED_OR_USED'
  | 'DOCUMENTS'
  | 'CONTAINS'
  | 'PROVIDES_EVIDENCE_FOR'
  | 'OCCURRED_AT'
  | 'INVOLVES'
  | 'OCCURRED_ON'
  | 'STUDIED_AT'
  | 'WORKED_AT'
  | 'INTERESTED_IN'
  | 'ABOUT'
  | 'APPEARS_IN'
  | 'MET'
  | 'OTHER';

export type RetrievalMode = 'VECTOR' | 'KEYWORD' | 'GRAPH' | 'HYBRID';

export type ContradictionStatus = 'OPEN' | 'UNDER_REVIEW' | 'RESOLVED' | 'UNRESOLVED';

export interface MemoryDNAItem {
  dna_item_id: string;
  memorial_profile_id: string;
  category: MemoryDNACategory;
  key: string;
  value: any;
  description?: string;
  source_memory_ids: string[];
  source_media_ids: string[];
  source_evidence_ids: string[];
  provenance_status: ProvenanceStatus;
  confidence: ConfidenceLevel;
  confidence_score: number;
  verification_status: VerificationStatus;
  created_at: string;
  updated_at: string;
}

export interface MemoryDNA {
  memory_dna_id: string;
  memorial_profile_id: string;
  person_id?: string;
  summary?: string;
  life_events: any[];
  people: any[];
  relationships: any[];
  places: any[];
  education: any[];
  career: any[];
  family: any[];
  friends: any[];
  hobbies: any[];
  interests: any[];
  important_objects: any[];
  important_dates: any[];
  documented_preferences: any[];
  documented_values: any[];
  known_phrases: any[];
  frequently_mentioned_topics: any[];
  stories: any[];
  achievements: any[];
  travel: any[];
  legacy: any[];
  source_references: string[];
  confidence: ConfidenceLevel;
  provenance: ProvenanceStatus;
  last_updated: string;
  version: number;
}

export interface MemoryDNAVersion {
  version_id: string;
  memory_dna_id: string;
  memorial_profile_id: string;
  version: number;
  dna_snapshot: any;
  changed_by: string;
  change_reason: string;
  source_evidence: string[];
  created_at: string;
}

export interface GraphNodeModel {
  id: string;
  memorial_profile_id: string;
  label: GraphNodeType;
  name: string;
  properties: Record<string, any>;
  source_memory_ids: string[];
  source_evidence_ids: string[];
  provenance_status: ProvenanceStatus;
  confidence: ConfidenceLevel;
  confidence_score: number;
  created_at: string;
  updated_at: string;
}

export interface GraphRelationshipModel {
  relationship_id: string;
  memorial_profile_id: string;
  source_node: string;
  target_node: string;
  relationship_type: GraphRelationshipType;
  properties: Record<string, any>;
  source_evidence_ids: string[];
  source_memory_ids: string[];
  provenance_status: ProvenanceStatus;
  confidence: ConfidenceLevel;
  confidence_score: number;
  created_at: string;
  updated_at: string;
}

export interface GraphNeighborhood {
  node: GraphNodeModel;
  neighbors: Array<{
    node: GraphNodeModel;
    direction: 'incoming' | 'outgoing';
    relationship_type: string;
  }>;
  relationships: GraphRelationshipModel[];
}

export interface GraphSearchResult {
  nodes: GraphNodeModel[];
  relationships: GraphRelationshipModel[];
  total_nodes: number;
  total_relationships: number;
}

export interface ContradictionRecord {
  contradiction_id: string;
  memorial_profile_id: string;
  subject: string;
  claim_a: string;
  claim_b: string;
  source_a: string;
  source_b: string;
  confidence_a: number;
  confidence_b: number;
  status: ContradictionStatus;
  notes?: string;
  created_at: string;
  resolved_at?: string;
}

export interface EvidenceChunk {
  chunk_id: string;
  memorial_profile_id: string;
  memory_id?: string;
  media_id?: string;
  evidence_id?: string;
  chunk_index: number;
  text: string;
  start_offset?: number;
  end_offset?: number;
  source_reference: string;
  provenance: ProvenanceStatus;
  confidence: ConfidenceLevel;
  confidence_score: number;
  created_at: string;
}

export interface RetrievalResultItem {
  result_id: string;
  memory_id?: string;
  media_id?: string;
  evidence_id?: string;
  chunk_id?: string;
  text: string;
  score: number;
  score_components: Record<string, number>;
  source_reference: string;
  provenance_status: ProvenanceStatus;
  confidence: ConfidenceLevel;
  content_type: string;
  retrieval_method: RetrievalMode;
  why_retrieved: string;
  created_at: string;
}

export interface RetrievalResponse {
  query_id: string;
  query: string;
  retrieval_mode: RetrievalMode;
  top_k: number;
  candidate_count: number;
  returned_count: number;
  latency_ms: number;
  results: RetrievalResultItem[];
  metrics: Record<string, any>;
}

export interface Phase4Metrics {
  memory_dna_items: number;
  graph_nodes: number;
  graph_relationships: number;
  indexed_evidence: number;
  vector_records: number;
  retrieval_queries: number;
  verified_evidence: number;
  supported_inferences: number;
  unknown_items: number;
}

// ==============================================================================
// Phase 5 Conversation, RAG & Memory Guardian Interfaces
// ==============================================================================

export type QuestionCategory =
  | 'MEMORY_LOOKUP'
  | 'PERSON_LOOKUP'
  | 'EVENT_LOOKUP'
  | 'RELATIONSHIP_LOOKUP'
  | 'TIMELINE_LOOKUP'
  | 'MEDIA_LOOKUP'
  | 'DOCUMENT_LOOKUP'
  | 'PREFERENCE_LOOKUP'
  | 'LIFE_STORY'
  | 'GENERAL_GREETING'
  | 'GENERAL_INFORMATION'
  | 'UNSUPPORTED_PERSONAL_QUERY'
  | 'SENSITIVE_QUERY'
  | 'UNKNOWN';

export type GuardianDecision = 'PASS' | 'REVISE' | 'BLOCK' | 'UNKNOWN';

export type ClaimStatus =
  | 'SUPPORTED'
  | 'PARTIALLY_SUPPORTED'
  | 'UNSUPPORTED'
  | 'CONTRADICTED'
  | 'UNKNOWN';

export type ConversationRole = 'USER' | 'ASSISTANT' | 'SYSTEM';

export interface QuestionClassification {
  category: QuestionCategory;
  confidence: number;
  reason: string;
  requires_archive: boolean;
  created_at: string;
}

export interface ResponseClaim {
  claim_id: string;
  message_id?: string;
  text: string;
  subject?: string;
  predicate?: string;
  object?: string;
  supporting_evidence_ids: string[];
  confidence: ConfidenceLevel;
  confidence_score: number;
  status: ClaimStatus;
  notes?: string;
}

export interface ResponseSource {
  source_id: string;
  source_title: string;
  source_type: SourceType;
  memory_id?: string;
  media_id?: string;
  evidence_id?: string;
  evidence_text: string;
  provenance_status: ProvenanceStatus;
  confidence: ConfidenceLevel;
  citation_label: string;
  created_at?: string;
}

export interface GuardianResult {
  result_id: string;
  message_id?: string;
  guardian_status: GuardianDecision;
  reason: string;
  violations: string[];
  unsupported_claims: string[];
  missing_evidence: string[];
  confidence: ConfidenceLevel;
  provenance: ProvenanceStatus;
  recommended_action: string;
  timestamp: string;
}

export interface RAGQueryRequest {
  query: string;
  memorial_profile_id: string;
  conversation_id?: string;
  top_k?: number;
  retrieval_mode?: RetrievalMode;
  confidence_threshold?: number;
}

export interface RAGQueryResponse {
  conversation_id?: string;
  message_id: string;
  query: string;
  answer: string;
  confidence_level: ConfidenceLevel;
  confidence_score: number;
  guardian_status: GuardianDecision;
  generated_by_ai: boolean;
  ethical_disclaimer: string;
  sources: ResponseSource[];
  claims: ResponseClaim[];
  contradictions: Array<Record<string, any>>;
  warnings: string[];
  retrieval_explanation?: string;
  question_classification?: QuestionClassification;
  timestamp: string;
}

export interface Phase5Metrics {
  conversations: number;
  messages: number;
  rag_queries: number;
  verified_responses: number;
  supported_inferences: number;
  unknown_responses: number;
  guardian_revisions: number;
  guardian_blocks: number;
  contradictions_detected: number;
}

// ==============================================================================
// Phase 6 Voice Interaction Types
// ==============================================================================

export type VoiceProcessingState =
  | 'IDLE'
  | 'RECORDING'
  | 'UPLOADING'
  | 'TRANSCRIBING'
  | 'RETRIEVING'
  | 'GENERATING'
  | 'VALIDATING'
  | 'SYNTHESIZING'
  | 'COMPLETED'
  | 'BLOCKED'
  | 'FAILED'
  | 'CANCELLED';

export type VoiceType = 'GENERIC_SYNTHETIC' | 'AUTHORIZED_MEMORIAL_CUSTOM';
export type VoiceProfileStatus = 'UNCONFIGURED' | 'PENDING_CONSENT' | 'READY' | 'REVOKED' | 'DISABLED';
export type AudioCategory = 'ORIGINAL_RECORDING' | 'TRANSCRIPTION' | 'AI_GENERATED_MEMORIAL_VOICE';

export interface VoiceProfile {
  id: string;
  name: string;
  description?: string;
  voice_type: VoiceType;
  language: string;
  provider: string;
  status: VoiceProfileStatus;
  consent_id?: string;
  is_consent_verified: boolean;
  watermark_tag: string;
  created_at: string;
  updated_at: string;
  revoked_at?: string;
  retention_days: number;
}

export interface VoiceSession {
  id: string;
  memorial_profile_id: string;
  user_id: string;
  language: string;
  voice_profile_id?: string;
  conversation_session_id?: string;
  state: VoiceProcessingState;
  original_transcript?: string;
  edited_transcript?: string;
  is_transcript_edited: boolean;
  voice_type: VoiceType;
  last_guardian_status?: GuardianDecision;
  error_message?: string;
  latency_metrics: Record<string, number>;
  created_at: string;
  updated_at: string;
}

export interface VoiceSynthesisResponse {
  audio_id: string;
  audio_url: string;
  voice_profile_id?: string;
  voice_type: VoiceType;
  audio_category: AudioCategory;
  text: string;
  language: string;
  duration_seconds: number;
  format: string;
  sha256_checksum: string;
  is_watermarked: boolean;
  watermark_payload: string;
  ethical_disclosure: string;
  latency_ms: number;
  created_at: string;
}

export interface VoiceInteractionResponse {
  session_id: string;
  state: VoiceProcessingState;
  transcript: string;
  is_transcript_edited: boolean;
  rag_response: RAGQueryResponse;
  synthesis?: VoiceSynthesisResponse;
  synthesis_blocked: boolean;
  synthesis_blocked_reason?: string;
  audio_category: AudioCategory;
  ethical_disclosure: string;
  total_latency_ms: number;
  latency_breakdown: Record<string, number>;
  timestamp: string;
}

// ==============================================================================
// Phase 7 3D Memory Room & Memorial Avatar Types
// ==============================================================================

export type RoomObjectType =
  | 'PHOTO_FRAME'
  | 'ARCHIVE_BOOKSHELF'
  | 'MEMORY_DESK'
  | 'TIMELINE_WALL'
  | 'AUDIO_STATION'
  | 'STORY_STATION'
  | 'CENTRAL_DISPLAY';

export type RoomTheme =
  | 'ARCHIVAL_WARM'
  | 'STUDY_CLASSIC'
  | 'GALLERY_MODERN'
  | 'MINIMAL_SERENE';

export type AvatarPose =
  | 'IDLE_NEUTRAL'
  | 'ATTENTIVE'
  | 'GESTURING_TOWARD_OBJECT'
  | 'SPEAKING';

export type AvatarModelType =
  | 'STYLIZED_GENERIC'
  | 'AUTHORIZED_KINSHIP_MODEL'
  | 'NEUTRAL_SILHOUETTE';

export interface RoomVector3 {
  x: number;
  y: number;
  z: number;
}

export interface RoomObject {
  object_id: string;
  memory_id?: string;
  media_id?: string;
  title: string;
  description: string;
  object_type: RoomObjectType;
  category: MemoryCategory;
  source_type: SourceType;
  confidence: ConfidenceLevel;
  verification_status: VerificationStatus;
  privacy_level: PrivacyLevel;
  date?: string;
  location?: string;
  people: string[];
  position: RoomVector3;
  rotation?: RoomVector3;
  scale?: RoomVector3;
  media_url?: string;
  thumbnail_url?: string;
  is_demo_placeholder: boolean;
  associated_dna_keys: string[];
  color_accent: string;
}

export interface RoomConfiguration {
  room_id: string;
  memorial_profile_id: string;
  theme: RoomTheme;
  ambient_light_intensity: number;
  floor_material: string;
  wall_color: string;
  camera_initial_position: RoomVector3;
  show_labels: boolean;
  reduced_motion: boolean;
  audio_enabled: boolean;
  updated_at?: string;
}

export interface AvatarConfig {
  enabled: boolean;
  memorial_profile_id: string;
  model_type: AvatarModelType;
  display_name: string;
  position: RoomVector3;
  rotation: RoomVector3;
  current_pose: AvatarPose;
  is_speaking: boolean;
  speaking_text?: string;
  speaking_audio_url?: string;
  is_authorized: boolean;
  consent_verified: boolean;
  watermark_disclosure: string;
  asset_url?: string;
  updated_at?: string;
}

export interface MemoryRoomResponse {
  memorial_profile_id: string;
  room_config: RoomConfiguration;
  avatar: AvatarConfig;
  objects: RoomObject[];
  total_objects: number;
  verified_count: number;
  supported_inference_count: number;
  unknown_count: number;
  categories_present: string[];
  ethical_disclosure: string;
  webgl_supported: boolean;
  timestamp: string;
}

export interface MemoryRoomMetrics {
  total_room_accesses: number;
  average_init_time_ms: number;
  average_selection_latency_ms: number;
  total_objects_rendered: number;
  webgl_success_rate: number;
  fallback_list_view_usage: number;
  avatar_speaking_events: number;
  ethical_disclosures_served: number;
}

export interface AvatarSpeechRequest {
  text: string;
  memorial_profile_id?: string;
  voice_profile_id?: string;
  language?: string;
  user_id?: string;
}

export interface AvatarSpeechResponse {
  speech_id: string;
  approved_text: string;
  guardian_decision: GuardianDecision;
  audio_url?: string;
  duration_seconds: number;
  is_watermarked: boolean;
  ethical_disclosure: string;
  avatar_pose: AvatarPose;
  timestamp: string;
}

// ==============================================================================
// Phase 8 AI Life Timeline, Relationship Graph & Family Collaboration Types
// ==============================================================================

export type DatePrecision = 'EXACT' | 'MONTH_YEAR' | 'YEAR_ONLY' | 'APPROXIMATE' | 'UNKNOWN';
export type FamilyRole = 'OWNER' | 'FAMILY_ADMIN' | 'CONTRIBUTOR' | 'VIEWER';
export type InvitationStatus = 'PENDING' | 'ACCEPTED' | 'REVOKED' | 'EXPIRED';
export type ContributionStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'APPROVED'
  | 'NEEDS_CHANGES'
  | 'REJECTED'
  | 'DISPUTED'
  | 'WITHDRAWN';

export type ContributionType =
  | 'NEW_MEMORY'
  | 'METADATA_CORRECTION'
  | 'TIMELINE_EVENT'
  | 'RELATIONSHIP_SUGGESTION'
  | 'ALTERNATIVE_DATE_OR_FACT'
  | 'SUPPORTING_DOCUMENT';

export interface TimelineEvent {
  id: string;
  memorial_profile_id: string;
  title: string;
  description?: string;
  category: string;
  event_date?: string;
  date_end?: string;
  date_description?: string;
  date_precision: DatePrecision;
  location_name?: string;
  associated_people: string[];
  associated_people_ids: string[];
  linked_memory_ids: string[];
  evidence_ids: string[];
  source_type: SourceType;
  confidence: ConfidenceLevel;
  confidence_score: number;
  verification_status: VerificationStatus;
  provenance_status: string;
  is_ai_suggested: boolean;
  is_disputed: boolean;
  dispute_notes?: string;
  competing_evidence_ids: string[];
  memory_room_object_id?: string;
  created_by_user_id: string;
  created_at: string;
  updated_at: string;
}

export interface TimelineResponse {
  total_events: number;
  events: TimelineEvent[];
  categories_present: string[];
  years_present: number[];
  disputed_count: number;
  unreviewed_count: number;
}

export interface RelationshipDetail {
  id: string;
  memorial_profile_id: string;
  source_entity_id: string;
  source_entity_name: string;
  source_entity_type: string;
  target_entity_id: string;
  target_entity_name: string;
  target_entity_type: string;
  relationship_type: string;
  description?: string;
  source_evidence_ids: string[];
  source_memory_ids: string[];
  provenance_status: string;
  confidence: ConfidenceLevel;
  confidence_score: number;
  verification_status: VerificationStatus;
  is_disputed: boolean;
  dispute_notes?: string;
  competing_evidence_ids: string[];
  created_by: string;
  is_ai_suggested: boolean;
  created_at: string;
  updated_at: string;
}

export interface DuplicateEntityCandidate {
  id: string;
  entity_a_id: string;
  entity_a_name: string;
  entity_a_label: string;
  entity_b_id: string;
  entity_b_name: string;
  entity_b_label: string;
  similarity_score: number;
  detection_reason: string;
  suggested_canonical_id: string;
  status: string;
}

export interface RelationshipGraphNode {
  id: string;
  name: string;
  label: string;
  confidence?: string;
  properties?: Record<string, any>;
}

export interface RelationshipGraphResponse {
  nodes: RelationshipGraphNode[];
  edges: RelationshipDetail[];
  total_nodes: number;
  total_edges: number;
  verified_edges_count: number;
  disputed_edges_count: number;
  pending_review_edges_count: number;
  duplicate_candidates_count: number;
}

export interface FamilyWorkspace {
  id: string;
  name: string;
  memorial_profile_id: string;
  owner_user_id: string;
  description?: string;
  members_count: number;
}

export interface FamilyMember {
  id: string;
  workspace_id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: FamilyRole;
  joined_at: string;
  status: string;
  relationship_to_subject?: string;
}

export interface FamilyInvitation {
  id: string;
  workspace_id: string;
  email: string;
  role: FamilyRole;
  relationship_to_subject?: string;
  status: InvitationStatus;
  invited_by_name: string;
  created_at: string;
  expires_at: string;
  invite_url?: string;
}

export interface FamilyContribution {
  id: string;
  workspace_id: string;
  contributor_id: string;
  contributor_name: string;
  contributor_email: string;
  contribution_type: ContributionType;
  title: string;
  target_id?: string;
  proposed_content: Record<string, any>;
  original_content?: Record<string, any>;
  supporting_evidence: Array<Record<string, any>>;
  contributor_notes?: string;
  confidence: ConfidenceLevel;
  provenance: string;
  is_ai_suggested: boolean;
  status: ContributionStatus;
  version: number;
  reviewer_id?: string;
  reviewer_name?: string;
  review_decision?: string;
  review_notes?: string;
  reviewed_at?: string;
  submitted_at: string;
  updated_at: string;
  version_history: Array<Record<string, any>>;
}

export interface Phase8Metrics {
  timeline_retrieval_latency_ms: number;
  events_with_supporting_evidence_count: number;
  events_awaiting_review_count: number;
  disputed_events_count: number;
  disputed_relationships_count: number;
  relationship_evidence_coverage_pct: number;
  contribution_approval_count: number;
  contribution_rejection_count: number;
  review_turnaround_time_hours_avg: number;
  unauthorized_access_attempts_count: number;
  duplicate_entity_suggestions_count: number;
  contradiction_detection_count: number;
  active_family_members_count: number;
  pending_invitations_count: number;
  total_contributions_count: number;
  measured_at: string;
}



