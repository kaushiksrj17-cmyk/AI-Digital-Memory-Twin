# ECHO — Granular Consent & Family Authorization Model

**Component:** Legal & Ethical Safeguard Framework  
**Enforcement:** `backend/app/services/consent_service.py`  
**API Endpoints:** `/api/v1/consent`

---

## 1. Ethical Imperative

Digital memory twins interact with sensitive personal likenesses, recorded voices, private correspondence, and sacred family memories. 

### The Golden Rule
> **Consent is NEVER assumed.**  
> Neither voice synthesis, 3D avatar presence, nor AI processing may take place without explicit, recorded consent from the subject or authorized next-of-kin.

---

## 2. Granular Consent Scopes

| Scope | Description | Phase Dependency | Default State |
| :--- | :--- | :--- | :--- |
| **`MEDIA_PROCESSING`** | Permission to ingest, index, and organize uploaded family media. | Phase 2 | Optional (Must be checked by uploader) |
| **`AI_PROCESSING`** | Permission to ground LLM dialogue responses in preserved texts/transcripts. | Phase 3 / 5 | Explicit Grant Required |
| **`VOICE_PROCESSING`** | Permission to extract vocal acoustic features and generate voice clones. | Phase 6 | Strictly Locked until Authorized |
| **`AVATAR_PROCESSING`** | Permission to generate visual 3D avatars or animate facial likenesses. | Phase 7 | Strictly Locked until Authorized |
| **`FAMILY_ACCESS`** | Permission to share memories across accredited family kinship circle. | Phase 8 | Explicit Grant Required |

---

## 3. Consent Record Structure

Each consent event records:
- `consent_id`: Unique cryptographic identifier.
- `granter_name`: Legal name of authorizing party.
- `granter_relationship`: Relationship to deceased or subject (e.g. "Daughter", "Executor").
- `consent_type`: Specific scope from table above.
- `status`: `GRANTED`, `REVOKED`, `EXPIRED`, `PENDING`.
- `document_reference`: Optional hash or reference to legal signed authorization.
- `granted_at`: Timestamp when authorization was granted.
- `revoked_at`: Timestamp when authorization was rescinded.
- `memory_id` / `media_id`: Specific asset bound to consent (or profile-wide if null).

---

## 4. Immediate Revocation Workflow

A family trustee or guardian can revoke consent at any time via:
```http
POST /api/v1/consent/{consent_id}/revoke
```
When revoked:
1. `status` transitions to `REVOKED`.
2. `revoked_at` is stamped.
3. An `AuditAction.CONSENT_REVOKED` record is committed to the audit log.
4. Downstream AI pipelines (voice, avatar, dialogue) immediately cease querying or generating from the affected media.
