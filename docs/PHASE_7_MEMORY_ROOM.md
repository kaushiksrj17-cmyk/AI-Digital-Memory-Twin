# ECHO — Phase 7: 3D Avatar + Interactive Memory Room

**Research Title:** Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation.  
**Project Tagline:** "Preserve the memories. Hear the voice. See the presence. Keep the story alive."

---

## 1. Executive Summary & Research Objective

Phase 7 introduces the **Interactive 3D Memory Room & Memorial Presence Guide** into the ECHO Digital Memory Twin architecture. Building upon the foundational vaults (Phase 1–2), multimodal processing (Phase 3), Memory DNA knowledge graphs (Phase 4), RAG & Memory Guardian safety boundaries (Phase 5), and authorized voice interaction (Phase 6), Phase 7 translates preserved digital memories into an intuitive, evidence-grounded spatial sanctuary.

Rather than presenting memories solely through two-dimensional lists or tables, family members and designated researchers can walk through a dignified, serene spatial room where each photograph, audio tape, personal letter, and milestone is anchored to physical three-dimensional coordinates in space.

### Core Non-Negotiable Invariants

1. **Zero-Fabrication Spatial Grounding**:
   - Every 3D room object maps directly and verifiably to an authenticated primary memory record in the vault.
   - If a memorial archive is empty, the room renders cleanly and honestly as an empty room — the system explicitly refuses to synthesize or fabricate fictitious memories or decorative spiritual artifacts.
   - Generic demonstration fixtures are explicitly flagged as `is_demo_placeholder: true`.

2. **Mandatory Ethical Disclosure & Anti-Deception Invariant**:
   - The visual Memorial Avatar is an evidence-grounded, stylized guide and never claims to possess living consciousness, independent will, subjective emotion, or resurrection of the deceased.
   - Prominently labeled in the 3D scene, floating HUD, and voice playback:
     > `"AI-GENERATED MEMORIAL REPRESENTATION — NOT THE ACTUAL PERSON."`
   - Likeness consent is strictly validated via the Phase 2/Phase 6 consent model.

3. **Memory Guardian Gated Speech**:
   - Spoken responses triggered through the avatar guide must pass through the Phase 5 Memory Guardian boundary validation.
   - Any query or response lacking preserved evidence or violating privacy boundaries is blocked from synthesis.
   - Approved speech utilizes the Phase 6 text-to-speech (TTS) engine with indelible ethical watermarking.

4. **Universal Dual-Mode Accessibility**:
   - Users with hardware limitations, missing WebGL drivers, or visual impairments can toggle seamlessly between the **3D Spatial Sanctuary** and the **2D Accessible Archival List View**.
   - Full keyboard navigation (Arrow keys for orbit, `+`/`-` for zoom, `Home` for camera reset).
   - Reduced-motion toggle (`prefers-reduced-motion`) halts floating animations and transitions.

5. **Local-First Privacy & Confidential Media Protection**:
   - Local filesystem paths (e.g., `D:\ECHO\storage\local\...`) are never leaked to public frontend assets.
   - Media files are proxied through secure, authenticated endpoints (`/api/v1/media/{id}`).
   - Privacy tiers (`PRIVATE_VAULT`, `FAMILY_ARCHIVE`, `RESTRICTED`) are strictly enforced.

---

## 2. 3D Architectural Spatial Zones

The memory room employs an architectural coordinate frame ($10\text{m} \times 3.5\text{m} \times 10\text{m}$, centered at $(0, 0, 0)$):

```
                   [ North Gallery Wall: Photographs (z = -4.8) ]
                                      ▲
                                      │
  [ West Audio Zone: Reels ]  ◄──────(0, 0, 0)──────►  [ East Archive Shelves: Documents ]
  (x = -4.8)                          │                (x = 4.8)
                                      ▼
                   [ South Timeline Wall: Milestones (z = 4.8) ]
```

| Zone | Coordinates | Object Type | Typical Content |
|---|---|---|---|
| **North Gallery Wall** | $z = -4.8$, $y \in [0.9, 1.8]$ | `PHOTO_FRAME` | Framed primary photographs and portraits |
| **East Archive Shelves** | $x = 4.8$, $z \in [-3.2, 3.2]$ | `ARCHIVE_BOOKSHELF`, `STORY_STATION` | Bound letters, legal certificates, published manuscripts |
| **West Audio Console** | $x = -4.8$, $z \in [-3.0, 3.0]$ | `AUDIO_STATION` | Reel-to-reel tapes and preserved oral cassettes |
| **South Timeline Wall** | $z = 4.8$, $x \in [-3.5, 3.5]$ | `TIMELINE_WALL` | Chronological era milestones across decades |
| **Center Memory Desk** | $y = 0.85$, $z \in [-0.3, 0.2]$ | `MEMORY_DESK` | Brass keepsakes, heirlooms, and personal artifacts |
| **Memorial Avatar Guide**| $x = 0$, $y = 0$, $z = -2.2$ | `MemorialAvatar3D` | Stylized presence guide facing the room center |

---

## 3. End-to-End Pipeline Architecture

```
USER / CLIENT BROWSER (/memory-room)
   │
   ├── 1. WebGL Detection & Fallback Check
   │      ├─ Supported ──► Initialize Three.js WebGLRenderer & MemoryRoomScene
   │      └─ Unavailable ─► Fallback to AccessibleMemoryList (2D Accessible View)
   │
   ├── 2. GET /api/v1/memory-room?profile_id=...&category=...&search=...
   │      │
   │      ├── MemoryRoomService.get_room_composition()
   │      │   ├── Retrieve authentic records from MemoryService (Vault)
   │      │   ├── Compute non-overlapping 3D placement coordinates
   │      │   ├── Check kinship consent for Avatar likeness
   │      │   ├── Assign confidence badge colors (Green / Amber / Red)
   │      │   └── Audit log event: ROOM_ACCESSED
   │      │
   │      └── Return MemoryRoomResponse JSON
   │
   ├── 3. Interactive Spatial HUD
   │      ├── MemoryRoomControls: Theme switch, Ambient light, Reset camera, Reduced motion
   │      ├── Three.js Orbit & Raycast Selection (hover highlights, click details)
   │      ├── MemoryObjectDetails Drawer: Primary media preview, provenance metadata, Memory DNA
   │      ├── MemoryEvidencePanel Modal: Guardian verification checkpoints & provenance chain
   │      ├── MemoryTimelinePanel: Chronological horizontal milestones
   │      └── AvatarSettingsPanel: Model selection, pose toggle, speech synthesis
   │
   └── 4. Avatar Speech Trigger (POST /api/v1/avatar/speak)
          │
          ├── MemoryGuardian.validate_response() (Boundary Check)
          ├── TTSService.synthesize_speech() (Phase 6 Audio Synthesis)
          └── Return AvatarSpeechResponse (Watermarked audio URL + SPEAKING pose)
```

---

## 4. API Specification

### `GET /api/v1/memory-room`
Retrieves complete 3D room composition, spatial object transforms, and active avatar state.
- **Parameters**: `profile_id` (str), `user_id` (str), `category` (optional enum), `search` (optional str).
- **Response**: `MemoryRoomResponse` (contains `room_config`, `avatar`, `objects`, `total_objects`, `verified_count`, `supported_inference_count`, `unknown_count`, `ethical_disclosure`, `webgl_supported`).

### `GET /api/v1/memory-room/objects/{object_id}`
Retrieves detailed archival evidence, media download links, and associated Memory DNA keys for a single room object.

### `PUT /api/v1/memory-room/config`
Updates atmospheric preferences: `theme`, `ambient_light_intensity`, `reduced_motion`, `audio_enabled`.

### `GET /api/v1/avatar/config` & `PUT /api/v1/avatar/config`
Inspects and updates avatar presence configuration: `enabled`, `model_type`, `display_name`, `current_pose`.

### `POST /api/v1/avatar/speak`
Triggers avatar speech with Memory Guardian safety boundary validation and TTS generation.
- **Payload**: `{ text, memorial_profile_id, language, user_id }`
- **Response**: `AvatarSpeechResponse` (with `approved_text`, `audio_url`, `is_watermarked: true`, `ethical_disclosure`).

### `GET /api/v1/memory-room/metrics` & `POST /api/v1/memory-room/metrics`
Records and aggregates client-side research instrumentation (initialization latency, WebGL availability rate, visible object count, fallback view usage).

---

## 5. Verification & Safety Guarantees

1. **Anti-Hallucination Invariant**: Room objects only exist if grounded in authentic vault memories.
2. **Audio/Media Protection**: Private items gate access through kinship authorization scopes.
3. **No Unauthenticated Likeness Cloning**: Without explicit consent, avatar switches to neutral silhouette or generic stylized guide.
4. **Accessible Equivalence**: Every memory accessible in 3D is equally navigable and readable in the accessible 2D view.
