"""Domain Enums for ECHO Memorial Architecture.

Encapsulates Confidence System, Privacy, Consent, Media Provenance,
and Phase 2 Secure Memory Vault Category and Processing Lifecycle.
"""

from enum import Enum


class ConfidenceLevel(str, Enum):
    """Memory Confidence Level System.
    
    GREEN = VERIFIED: Grounded in primary authenticated documents, audio, or video evidence.
    YELLOW = SUPPORTED_INFERENCE: Plausible deduction drawn from correlated preserved memories.
    RED = UNKNOWN_UNSUPPORTED: Unsubstantiated or unrecorded claim; explicitly acknowledged as unknown.
    """
    VERIFIED = "VERIFIED"                      # GREEN
    SUPPORTED_INFERENCE = "SUPPORTED_INFERENCE" # YELLOW
    UNKNOWN_UNSUPPORTED = "UNKNOWN_UNSUPPORTED" # RED


class MemoryCategory(str, Enum):
    """Controlled categories for personal archive organization with future extensibility."""
    CHILDHOOD = "CHILDHOOD"
    EDUCATION = "EDUCATION"
    CAREER = "CAREER"
    FAMILY = "FAMILY"
    FRIENDS = "FRIENDS"
    TRAVEL = "TRAVEL"
    HOBBIES = "HOBBIES"
    ACHIEVEMENTS = "ACHIEVEMENTS"
    SPECIAL_EVENTS = "SPECIAL_EVENTS"
    PERSONAL_STORIES = "PERSONAL_STORIES"
    OTHER = "OTHER"


class VerificationStatus(str, Enum):
    """Memory verification lifecycle status."""
    VERIFIED = "VERIFIED"
    PENDING_REVIEW = "PENDING_REVIEW"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"
    # Phase 1 backward compatibility aliases
    UNREVIEWED = "UNREVIEWED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED_BY_FAMILY = "VERIFIED_BY_FAMILY"
    VERIFIED_BY_DOCUMENT = "VERIFIED_BY_DOCUMENT"
    DISPUTED = "DISPUTED"


class PrivacyLevel(str, Enum):
    """Privacy and access boundary tier. Default is strictly PRIVATE."""
    PRIVATE = "PRIVATE"                      # Vault owner and primary guardian only
    FAMILY = "FAMILY"                        # Authorized kinship circle
    AUTHORIZED_USERS = "AUTHORIZED_USERS"    # Specific accredited researchers/relatives
    # Phase 1 backward compatibility aliases
    FAMILY_ONLY = "FAMILY_ONLY"
    MEMORIAL_PUBLIC = "MEMORIAL_PUBLIC"
    RESTRICTED = "RESTRICTED"


class SourceType(str, Enum):
    """Origin of memory evidence.
    
    Important: AI_GENERATED content must always be visually and programmatically
    distinguishable from original preserved material.
    """
    ORIGINAL_PHOTO = "ORIGINAL_PHOTO"
    ORIGINAL_VIDEO = "ORIGINAL_VIDEO"
    ORIGINAL_AUDIO = "ORIGINAL_AUDIO"
    DOCUMENT = "DOCUMENT"
    FAMILY_STORY = "FAMILY_STORY"
    USER_ENTRY = "USER_ENTRY"
    AI_GENERATED = "AI_GENERATED"
    # Phase 1 backward compatibility aliases
    PHOTOGRAPH = "PHOTOGRAPH"
    VIDEO = "VIDEO"
    AUDIO_RECORDING = "AUDIO_RECORDING"
    LETTER = "LETTER"
    BIOGRAPHY = "BIOGRAPHY"
    OFFICIAL_RECORD = "OFFICIAL_RECORD"
    PERSONAL_NOTE = "PERSONAL_NOTE"
    DIARY = "DIARY"


class RelationshipType(str, Enum):
    PARENT = "PARENT"
    CHILD = "CHILD"
    SPOUSE = "SPOUSE"
    SIBLING = "SIBLING"
    GRANDPARENT = "GRANDPARENT"
    GRANDCHILD = "GRANDCHILD"
    FRIEND = "FRIEND"
    MENTOR = "MENTOR"
    COLLEAGUE = "COLLEAGUE"
    OTHER = "OTHER"


class ConsentType(str, Enum):
    """Granular consent scopes. Never assumed; requires explicit guardian authorization."""
    MEDIA_PROCESSING = "MEDIA_PROCESSING"
    AI_PROCESSING = "AI_PROCESSING"
    VOICE_PROCESSING = "VOICE_PROCESSING"
    AVATAR_PROCESSING = "AVATAR_PROCESSING"
    FAMILY_ACCESS = "FAMILY_ACCESS"
    CUSTOM_VOICE_SYNTHESIS = "CUSTOM_VOICE_SYNTHESIS"
    AUDIO_STORAGE = "AUDIO_STORAGE"


class ConsentStatus(str, Enum):
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    PENDING = "PENDING"


class ProcessingStatus(str, Enum):
    """Asynchronous ingestion and processing lifecycle status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class AuditAction(str, Enum):
    """Audit action types for tamper-evident provenance logging."""
    UPLOAD = "UPLOAD"
    VIEW = "VIEW"
    EDIT = "EDIT"
    DELETE = "DELETE"
    ARCHIVE = "ARCHIVE"
    EXPORT = "EXPORT"
    VERIFY = "VERIFY"
    REJECT = "REJECT"
    CONSENT_GRANTED = "CONSENT_GRANTED"
    CONSENT_REVOKED = "CONSENT_REVOKED"
    PRIVACY_CHANGED = "PRIVACY_CHANGED"
    # Phase 3 Multimodal AI Processing Actions
    PROCESSING_STARTED = "PROCESSING_STARTED"
    PROCESSING_COMPLETED = "PROCESSING_COMPLETED"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    PROCESSING_RETRIED = "PROCESSING_RETRIED"
    PROCESSING_CANCELLED = "PROCESSING_CANCELLED"
    EVIDENCE_CREATED = "EVIDENCE_CREATED"
    # Phase 4 Memory DNA, Knowledge Graph, Embeddings & Retrieval Actions
    MEMORY_DNA_BUILT = "MEMORY_DNA_BUILT"
    MEMORY_DNA_UPDATED = "MEMORY_DNA_UPDATED"
    MEMORY_DNA_VERIFIED = "MEMORY_DNA_VERIFIED"
    MEMORY_DNA_REJECTED = "MEMORY_DNA_REJECTED"
    GRAPH_NODE_CREATED = "GRAPH_NODE_CREATED"
    GRAPH_RELATIONSHIP_CREATED = "GRAPH_RELATIONSHIP_CREATED"
    GRAPH_REBUILT = "GRAPH_REBUILT"
    EMBEDDING_CREATED = "EMBEDDING_CREATED"
    EMBEDDING_DELETED = "EMBEDDING_DELETED"
    RETRIEVAL_EXECUTED = "RETRIEVAL_EXECUTED"
    # Phase 5 Conversation Engine, RAG & Memory Guardian Actions
    CONVERSATION_CREATED = "CONVERSATION_CREATED"
    MESSAGE_CREATED = "MESSAGE_CREATED"
    RAG_QUERY = "RAG_QUERY"
    EVIDENCE_RETRIEVED = "EVIDENCE_RETRIEVED"
    RESPONSE_GENERATED = "RESPONSE_GENERATED"
    GUARDIAN_VALIDATED = "GUARDIAN_VALIDATED"
    RESPONSE_BLOCKED = "RESPONSE_BLOCKED"
    RESPONSE_REVISED = "RESPONSE_REVISED"
    CONTRADICTION_DETECTED = "CONTRADICTION_DETECTED"
    # Phase 6 Voice Interaction & Memorial Voice Actions
    VOICE_SESSION_STARTED = "VOICE_SESSION_STARTED"
    VOICE_AUDIO_TRANSCRIBED = "VOICE_AUDIO_TRANSCRIBED"
    VOICE_SYNTHESIS_REQUESTED = "VOICE_SYNTHESIS_REQUESTED"
    VOICE_SYNTHESIS_COMPLETED = "VOICE_SYNTHESIS_COMPLETED"
    VOICE_SYNTHESIS_BLOCKED = "VOICE_SYNTHESIS_BLOCKED"
    VOICE_PROFILE_CREATED = "VOICE_PROFILE_CREATED"
    VOICE_PROFILE_UPDATED = "VOICE_PROFILE_UPDATED"
    VOICE_PROFILE_DISABLED = "VOICE_PROFILE_DISABLED"
    VOICE_PROFILE_REVOKED = "VOICE_PROFILE_REVOKED"
    VOICE_AUDIO_ACCESSED = "VOICE_AUDIO_ACCESSED"
    VOICE_AUDIO_DELETED = "VOICE_AUDIO_DELETED"
    # Phase 7 3D Memory Room & Memorial Avatar Actions
    ROOM_ACCESSED = "ROOM_ACCESSED"
    ROOM_OBJECT_SELECTED = "ROOM_OBJECT_SELECTED"
    ROOM_CONFIG_UPDATED = "ROOM_CONFIG_UPDATED"
    AVATAR_CONFIG_UPDATED = "AVATAR_CONFIG_UPDATED"
    AVATAR_SPEECH_TRIGGERED = "AVATAR_SPEECH_TRIGGERED"
    # Phase 8 AI Life Timeline, Relationship Graph & Family Collaboration Actions
    TIMELINE_EVENT_CREATED = "TIMELINE_EVENT_CREATED"
    TIMELINE_EVENT_UPDATED = "TIMELINE_EVENT_UPDATED"
    TIMELINE_EVENT_VERIFIED = "TIMELINE_EVENT_VERIFIED"
    TIMELINE_EVENT_DISPUTED = "TIMELINE_EVENT_DISPUTED"
    RELATIONSHIP_CREATED = "RELATIONSHIP_CREATED"
    RELATIONSHIP_VERIFIED = "RELATIONSHIP_VERIFIED"
    RELATIONSHIP_DISPUTED = "RELATIONSHIP_DISPUTED"
    RELATIONSHIP_MERGED = "RELATIONSHIP_MERGED"
    FAMILY_INVITATION_CREATED = "FAMILY_INVITATION_CREATED"
    FAMILY_INVITATION_ACCEPTED = "FAMILY_INVITATION_ACCEPTED"
    FAMILY_INVITATION_REVOKED = "FAMILY_INVITATION_REVOKED"
    FAMILY_MEMBER_ROLE_CHANGED = "FAMILY_MEMBER_ROLE_CHANGED"
    FAMILY_MEMBER_REMOVED = "FAMILY_MEMBER_REMOVED"
    CONTRIBUTION_SUBMITTED = "CONTRIBUTION_SUBMITTED"
    CONTRIBUTION_REVIEWED = "CONTRIBUTION_REVIEWED"
    CONTRIBUTION_WITHDRAWN = "CONTRIBUTION_WITHDRAWN"
    # Phase 1 backward compatibility aliases
    MEMORY_ACCESSED = "MEMORY_ACCESSED"
    MEMORY_CREATED = "MEMORY_CREATED"
    MEMORY_MODIFIED = "MEMORY_MODIFIED"
    MEDIA_UPLOADED = "MEDIA_UPLOADED"
    EVIDENCE_VERIFIED = "EVIDENCE_VERIFIED"
    CONVERSATION_INITIATED = "CONVERSATION_INITIATED"
    SECURITY_ALERT = "SECURITY_ALERT"


class ProvenanceStatus(str, Enum):
    """Origin grounding status for evidence artifacts."""
    DIRECTLY_OBSERVED = "DIRECTLY_OBSERVED"  # Read directly from primary file (e.g. text file, metadata)
    USER_PROVIDED = "USER_PROVIDED"          # Explicitly entered by authenticated user/guardian
    AI_INFERRED = "AI_INFERRED"              # Derived via configured AI processor (never presented as fact)
    UNKNOWN = "UNKNOWN"                      # Missing or inconclusive data (never fabricated)


class EvidenceType(str, Enum):
    """Categorization of extracted evidence records."""
    TEXT = "TEXT"
    OCR_TEXT = "OCR_TEXT"
    TRANSCRIPT = "TRANSCRIPT"
    IMAGE_METADATA = "IMAGE_METADATA"
    VISUAL_OBJECT = "VISUAL_OBJECT"
    VISUAL_SCENE = "VISUAL_SCENE"
    VIDEO_KEYFRAME = "VIDEO_KEYFRAME"
    ENTITY = "ENTITY"
    EVENT = "EVENT"
    LOCATION = "LOCATION"
    DATE = "DATE"
    AUDIO_METADATA = "AUDIO_METADATA"
    VIDEO_METADATA = "VIDEO_METADATA"
    DOCUMENT_METADATA = "DOCUMENT_METADATA"


class EntityType(str, Enum):
    """Types of entities extracted from multimodal evidence."""
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    ORGANIZATION = "ORGANIZATION"
    OBJECT = "OBJECT"
    DATE = "DATE"
    EVENT = "EVENT"
    DOCUMENT = "DOCUMENT"
    MEDIA = "MEDIA"


class EventType(str, Enum):
    """Documented milestone and event categories."""
    BIRTH = "BIRTH"
    CHILDHOOD = "CHILDHOOD"
    EDUCATION = "EDUCATION"
    CAREER = "CAREER"
    FAMILY = "FAMILY"
    FRIENDSHIP = "FRIENDSHIP"
    TRAVEL = "TRAVEL"
    ACHIEVEMENT = "ACHIEVEMENT"
    CELEBRATION = "CELEBRATION"
    IMPORTANT_EVENT = "IMPORTANT_EVENT"
    PERSONAL_STORY = "PERSONAL_STORY"
    OTHER = "OTHER"


class ProviderReadiness(str, Enum):
    """Readiness state of external AI providers."""
    CONFIGURED = "CONFIGURED"
    UNCONFIGURED = "UNCONFIGURED"
    FAILED = "FAILED"
    AVAILABLE = "AVAILABLE"
    MOCK_MODE = "MOCK_MODE"


class MemoryDNACategory(str, Enum):
    """Structured categories for evidence-grounded Memory DNA representation."""
    IDENTITY = "IDENTITY"
    FAMILY = "FAMILY"
    RELATIONSHIPS = "RELATIONSHIPS"
    CHILDHOOD = "CHILDHOOD"
    EDUCATION = "EDUCATION"
    CAREER = "CAREER"
    FRIENDS = "FRIENDS"
    HOBBIES = "HOBBIES"
    INTERESTS = "INTERESTS"
    TRAVEL = "TRAVEL"
    ACHIEVEMENTS = "ACHIEVEMENTS"
    IMPORTANT_EVENTS = "IMPORTANT_EVENTS"
    PLACES = "PLACES"
    IMPORTANT_OBJECTS = "IMPORTANT_OBJECTS"
    DOCUMENTED_PREFERENCES = "DOCUMENTED_PREFERENCES"
    DOCUMENTED_VALUES = "DOCUMENTED_VALUES"
    KNOWN_PHRASES = "KNOWN_PHRASES"
    FREQUENT_TOPICS = "FREQUENT_TOPICS"
    PERSONAL_STORIES = "PERSONAL_STORIES"
    LEGACY = "LEGACY"
    UNKNOWN = "UNKNOWN"


class GraphNodeType(str, Enum):
    """Knowledge Graph entity and document node types."""
    PERSON = "PERSON"
    MEMORY = "MEMORY"
    EVENT = "EVENT"
    PLACE = "PLACE"
    OBJECT = "OBJECT"
    DOCUMENT = "DOCUMENT"
    MEDIA = "MEDIA"
    ORGANIZATION = "ORGANIZATION"
    DATE = "DATE"
    TOPIC = "TOPIC"


class GraphRelationshipType(str, Enum):
    """Normalized edge relationship types in ECHO Knowledge Graph."""
    RELATED_TO = "RELATED_TO"
    APPEARED_IN = "APPEARED_IN"
    PARTICIPATED_IN = "PARTICIPATED_IN"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    OWNED_OR_USED = "OWNED_OR_USED"
    DOCUMENTS = "DOCUMENTS"
    CONTAINS = "CONTAINS"
    PROVIDES_EVIDENCE_FOR = "PROVIDES_EVIDENCE_FOR"
    OCCURRED_AT = "OCCURRED_AT"
    INVOLVES = "INVOLVES"
    OCCURRED_ON = "OCCURRED_ON"
    STUDIED_AT = "STUDIED_AT"
    WORKED_AT = "WORKED_AT"
    INTERESTED_IN = "INTERESTED_IN"
    ABOUT = "ABOUT"
    APPEARS_IN = "APPEARS_IN"
    MET = "MET"
    # Phase 8 Evidence-Grounded Kinship & Social Graph Edge Types
    PARENT_OF = "PARENT_OF"
    CHILD_OF = "CHILD_OF"
    SIBLING_OF = "SIBLING_OF"
    SPOUSE_OF = "SPOUSE_OF"
    FRIEND_OF = "FRIEND_OF"
    VISITED = "VISITED"
    MENTIONED_IN = "MENTIONED_IN"
    DOCUMENTED_BY = "DOCUMENTED_BY"
    CONNECTED_TO_MEMORY = "CONNECTED_TO_MEMORY"
    OTHER = "OTHER"


class RetrievalMode(str, Enum):
    """Retrieval strategies for evidence retrieval engine."""
    VECTOR = "VECTOR"
    KEYWORD = "KEYWORD"
    GRAPH = "GRAPH"
    HYBRID = "HYBRID"


class ContradictionStatus(str, Enum):
    """Lifecycle status for documented claim contradictions."""
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class QuestionCategory(str, Enum):
    """Classification categories for user inquiries."""
    MEMORY_LOOKUP = "MEMORY_LOOKUP"
    PERSON_LOOKUP = "PERSON_LOOKUP"
    EVENT_LOOKUP = "EVENT_LOOKUP"
    RELATIONSHIP_LOOKUP = "RELATIONSHIP_LOOKUP"
    TIMELINE_LOOKUP = "TIMELINE_LOOKUP"
    MEDIA_LOOKUP = "MEDIA_LOOKUP"
    DOCUMENT_LOOKUP = "DOCUMENT_LOOKUP"
    PREFERENCE_LOOKUP = "PREFERENCE_LOOKUP"
    LIFE_STORY = "LIFE_STORY"
    GENERAL_GREETING = "GENERAL_GREETING"
    GENERAL_INFORMATION = "GENERAL_INFORMATION"
    UNSUPPORTED_PERSONAL_QUERY = "UNSUPPORTED_PERSONAL_QUERY"
    SENSITIVE_QUERY = "SENSITIVE_QUERY"
    UNKNOWN = "UNKNOWN"


class GuardianDecision(str, Enum):
    """Memory Guardian validation verdict."""
    PASS = "PASS"
    REVISE = "REVISE"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class ClaimStatus(str, Enum):
    """Grounding verification status of extracted factual claims."""
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"


class ConversationRole(str, Enum):
    """Participants in dialogue sessions."""
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"


class VoiceProfileStatus(str, Enum):
    """Voice profile lifecycle states."""
    UNCONFIGURED = "UNCONFIGURED"
    PENDING_CONSENT = "PENDING_CONSENT"
    READY = "READY"
    REVOKED = "REVOKED"
    DISABLED = "DISABLED"


class VoiceType(str, Enum):
    """Categorization of voice synthesis model."""
    GENERIC_SYNTHETIC = "GENERIC_SYNTHETIC"
    AUTHORIZED_MEMORIAL_CUSTOM = "AUTHORIZED_MEMORIAL_CUSTOM"


class VoiceProcessingState(str, Enum):
    """Finite state machine for voice interaction lifecycle."""
    IDLE = "IDLE"
    RECORDING = "RECORDING"
    UPLOADING = "UPLOADING"
    TRANSCRIBING = "TRANSCRIBING"
    RETRIEVING = "RETRIEVING"
    GENERATING = "GENERATING"
    VALIDATING = "VALIDATING"
    SYNTHESIZING = "SYNTHESIZING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AudioCategory(str, Enum):
    """Three mandatory domain categories for all audio in ECHO."""
    ORIGINAL_RECORDING = "ORIGINAL_RECORDING"
    TRANSCRIPTION = "TRANSCRIPTION"
    AI_GENERATED_MEMORIAL_VOICE = "AI_GENERATED_MEMORIAL_VOICE"


# ==============================================================================
# Phase 7 3D Memory Room & Memorial Avatar Enums
# ==============================================================================

class RoomObjectType(str, Enum):
    """Types of interactive 3D objects representing preserved memory assets."""
    PHOTO_FRAME = "PHOTO_FRAME"           # Preserved photographs on walls
    ARCHIVE_BOOKSHELF = "ARCHIVE_BOOKSHELF" # Preserved documents & books on shelves
    MEMORY_DESK = "MEMORY_DESK"           # Significant physical objects on desk
    TIMELINE_WALL = "TIMELINE_WALL"       # Chronological life milestones on wall
    AUDIO_STATION = "AUDIO_STATION"       # Oral history reel & sound player
    STORY_STATION = "STORY_STATION"       # Written memoirs and family stories
    CENTRAL_DISPLAY = "CENTRAL_DISPLAY"   # Featured focal memory in center


class RoomTheme(str, Enum):
    """Calm, respectful visual styling presets for the 3D memory room."""
    ARCHIVAL_WARM = "ARCHIVAL_WARM"       # Warm wood, amber ambient glow, library atmosphere
    STUDY_CLASSIC = "STUDY_CLASSIC"       # Mahogany shelves, brass details, academic study
    GALLERY_MODERN = "GALLERY_MODERN"     # Clean slate, recessed spotlights, quiet museum
    MINIMAL_SERENE = "MINIMAL_SERENE"     # Muted taupe, soft daylight, uncluttered space


class AvatarPose(str, Enum):
    """Subtle, respectful poses and animation states for the memorial avatar."""
    IDLE_NEUTRAL = "IDLE_NEUTRAL"                     # Calm standing/sitting neutral pose
    ATTENTIVE = "ATTENTIVE"                           # Turned toward user/active camera
    GESTURING_TOWARD_OBJECT = "GESTURING_TOWARD_OBJECT" # Directing visual focus to memory
    SPEAKING = "SPEAKING"                             # Subtle mouth & facial sync during TTS


class AvatarModelType(str, Enum):
    """Stylization level for the visual memorial avatar."""
    STYLIZED_GENERIC = "STYLIZED_GENERIC"             # Neutral stylized geometric character
    AUTHORIZED_KINSHIP_MODEL = "AUTHORIZED_KINSHIP_MODEL" # Approved likeness with verified consent
    NEUTRAL_SILHOUETTE = "NEUTRAL_SILHOUETTE"         # Abstract translucent silhouette


# ==============================================================================
# Phase 8 AI Life Timeline, Relationship Graph & Family Collaboration Enums
# ==============================================================================

class DatePrecision(str, Enum):
    """Evidentiary precision of chronological life event dates."""
    EXACT = "EXACT"                       # Full day, month, and year documented (e.g. 1968-06-22)
    MONTH_YEAR = "MONTH_YEAR"             # Documented month and year (e.g. June 1968)
    YEAR_ONLY = "YEAR_ONLY"               # Documented year only (e.g. 1968)
    APPROXIMATE = "APPROXIMATE"           # Estimated range or approximate epoch (e.g. circa 1968)
    UNKNOWN = "UNKNOWN"                   # Undetermined date; never fabricated


class FamilyRole(str, Enum):
    """Four-tier role-based access control for family archive collaboration."""
    OWNER = "OWNER"                       # Full archive sovereignty, membership, settings & export
    FAMILY_ADMIN = "FAMILY_ADMIN"         # Member management, review queue resolution & dispute oversight
    CONTRIBUTOR = "CONTRIBUTOR"           # Submits memories, suggestions, corrections, and documents
    VIEWER = "VIEWER"                     # Read-only access to authorized records; no modification rights


class InvitationStatus(str, Enum):
    """Lifecycle status for secure single-use family workspace invitations."""
    PENDING = "PENDING"                   # Awaiting redemption by recipient
    ACCEPTED = "ACCEPTED"                 # Successfully claimed and activated
    REVOKED = "REVOKED"                   # Revoked by owner/admin prior to use
    EXPIRED = "EXPIRED"                   # Passed validity period without redemption


class ContributionStatus(str, Enum):
    """Lifecycle state machine for family memory contributions and corrections."""
    DRAFT = "DRAFT"                       # Private to contributor; not yet submitted
    SUBMITTED = "SUBMITTED"               # Pending review by family guardian/admin
    UNDER_REVIEW = "UNDER_REVIEW"         # Actively being scrutinized against archival evidence
    APPROVED = "APPROVED"                 # Verified and committed to memorial archive
    NEEDS_CHANGES = "NEEDS_CHANGES"       # Feedback provided; requires contributor revision
    REJECTED = "REJECTED"                 # Incompatible with evidence or outside ethical boundaries
    DISPUTED = "DISPUTED"                 # Competing family recollections or evidence retained
    WITHDRAWN = "WITHDRAWN"               # Retracted by original contributor


class ContributionType(str, Enum):
    """Categorization of proposed family archive contributions."""
    NEW_MEMORY = "NEW_MEMORY"                         # Proposed new memory narrative with media
    METADATA_CORRECTION = "METADATA_CORRECTION"       # Proposed modification of memory metadata
    TIMELINE_EVENT = "TIMELINE_EVENT"                 # Proposed addition or edit to life journey
    RELATIONSHIP_SUGGESTION = "RELATIONSHIP_SUGGESTION" # Suggested social or kinship edge
    ALTERNATIVE_DATE_OR_FACT = "ALTERNATIVE_DATE_OR_FACT" # Alternative account or conflicting date
    SUPPORTING_DOCUMENT = "SUPPORTING_DOCUMENT"       # New primary archival source or photo evidence





