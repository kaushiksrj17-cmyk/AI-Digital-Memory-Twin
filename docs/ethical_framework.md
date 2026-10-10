# Ethical Framework & Boundaries

## Principles for Dignified, Non-Deceptive Digital Memory Preservation

### 1. Fundamental Boundary Statement
> **“ECHO is an AI-generated memorial representation. It does not recreate consciousness, identity, or the actual person.”**

ECHO rejects the philosophical and psychological hazards of claiming to "resurrect" deceased persons or simulating living sentience. Digital memory preservation must honor authentic personal history, not construct deceptive simulations.

---

### 2. Prohibited Claims & Representations
Under no circumstances may the ECHO system or any integrated AI model generate or endorse:
1. **Claims of Consciousness**: Stating or implying that the digital model possesses thoughts, feelings, souls, or inner mental states.
2. **First-Person Identity Usurpation**: Generating statements such as:
   - *"I am really your loved one speaking from beyond."*
   - *"I have come back to life through this software."*
   - *"I am speaking to you from heaven."*
3. **Resurrection or Reanimation Mythologies**: Presenting the AI system as a reincarnation or technological afterlife.
4. **Fabrication of Undocumented Memories**: Inventing memories, opinions, or life episodes not documented in preserved evidence.
5. **Fabrication of Imagined Speech**: Generating conjectural statements about what the person "would have said" on contemporary issues they never encountered.

---

### 3. Clear Distinction: Preserved Evidence vs. AI Inferences
The system maintains an absolute visual and programmatic distinction:
- **ORIGINAL PRESERVED EVIDENCE**: Primary authenticated photographs, letters, documents, and cassette tape recordings preserved directly from family archives.
- **AI-GENERATED REPRESENTATION**: Synthesized dialogue, summaries, and deductive inferences. These are always marked with explicit AI-Generated indicators and disclaimers.

---

### 4. Consent-Grounded Ingestion (Never Assumed)
In Phase 2 and Phase 3, explicit consent tracking is enforced for:
- `MEDIA_PROCESSING`: Authorization for local media analysis, thumbnails, and keyframe extraction.
- `AI_PROCESSING`: Authorization for optical character recognition, speech-to-text, and visual object detection.
- `VOICE_PROCESSING`: Explicitly deferred until Phase 6; requires independent biometric consent.
- `AVATAR_PROCESSING`: Explicitly deferred until Phase 6; requires independent visual consent.
- `FAMILY_ACCESS`: Authorization for trustees and family circle review.

Neither voice cloning nor avatar creation can ever be initiated without documented, unrevoked consent from next-of-kin or the authorizing subject.

---

### 5. Multimodal Processing Ethical Rules (Phase 3)
1. **Zero Text / Transcript Fabrication**: If an OCR engine or STT provider is unavailable or unconfigured, the system reports `UNCONFIGURED` / `PROCESSING_LIMITED`. It is strictly forbidden to synthesize mock transcripts or invented document texts.
2. **Strict Unknown Preservation**: An unknown date, location, or person must remain categorized as `UNKNOWN`. It must never be hallucinated to fill a gap in a narrative.
3. **Absence Disclosure**: When evidence is missing, the system outputs:
   > *“This information is not present in the preserved archive.”*
4. **No Uncorroborated Presence Claims**: Mention of a name in an archival letter does not entitle the system to conclude that the person is pictured in an accompanying photograph unless verified by visual evidence.
5. **Original File Preservation**: Raw family files inside `storage/originals/` are immutable and never modified or overwritten by derived processing results.

---

### 6. Phase 4 Memory DNA & Knowledge Graph Ethical Boundaries
1. **Memory DNA is NOT a Personality Clone**: Memory DNA is a structured, evidence-grounded representation of documented life information. It does NOT model consciousness, inner psychological states, or emotional souls.
2. **Strict Prohibition on Sensitive Inferences**: Under no circumstances will the system infer or categorize mental illness, political inclinations, religious beliefs, sexual orientation, criminal conduct, or private medical diagnoses unless explicitly documented in authentic primary evidence and authorized by family consent.
3. **Absolute Anti-Fabrication Rule**: Missing information must strictly remain `UNKNOWN` or `NOT PRESENT IN ARCHIVE`. No imaginary memories, speculative relationships, invented preferences, or uncorroborated life events may ever be inserted.
4. **No Uncorroborated Co-Presence / Co-Occurrence Relationships**: Mentioning two entities in the same document does not entitle the Knowledge Graph to create arbitrary relations (e.g., `LIVES_IN`, `MARRIED_TO`). Relationships require validated evidence citations.
5. **No Silent Entity Merging**: Obvious name variations (e.g., "Dr. Arun Kumar" vs "Arun Kumar") are registered as potential candidate aliases for user review and are never silently merged without contextual corroboration.
6. **Contradiction Preservation Over Revisionism**: When historical documents make conflicting claims, both claims are preserved in an explicit `ContradictionRecord` (`OPEN`, `UNDER_REVIEW`, `RESOLVED`, `UNRESOLVED`). The system never silently deletes or overwrites conflicting accounts.
7. **Phase 4 Scope Completed**: Handed off to Phase 5 for evidence-grounded conversational response generation.

---

### 7. Phase 5 Conversational & RAG Ethical Boundaries
1. **Mandatory Identity Boundary**: The conversational engine must NEVER use first-person pronouns claiming living existence (`"I was"`, `"I remember"`, `"When I died"`). It speaks objectively as an archival assistant: `"The preserved archive records that..."`.
2. **Explicit "AI-Generated Memorial Response" Labeling**: Every generated statement is prominently labeled with the AI-generation badge to prevent deceptive anthropomorphism.
3. **Mandatory Zero-Evidence State**: When retrieval finds no corroborating evidence, the system is strictly prohibited from prompting an LLM to invent an answer. It outputs: `"I don't have enough information in the preserved archive to answer that accurately."`
4. **Transparent Contradiction Disclosure**: Disputed historical records must be disclosed openly rather than harmonized into a false single truth.
5. **Memory Guardian 18-Check Gate**: All responses must pass claim-level verification, hallucination checks, privacy clearing, and consent authorization before reaching users.

