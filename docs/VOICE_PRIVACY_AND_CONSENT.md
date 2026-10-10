# ECHO — Voice Privacy, Kinship Authorization & Consent Framework

**Research Title:** Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation.  
**Ethical Doctrine:** Respect for Personhood, Kinship Governance, and Non-Deceptive Representation.

---

## 1. Ethical Governance Principles

In interactive memorial AI systems, acoustic likeness carries profound psychological and moral significance. Unauthorized voice synthesis poses severe risks of grief exploitation, deceptive impersonation, and violation of testamentary autonomy.

ECHO implements a strict, multi-tiered consent framework governed by the following immutable principles:

1. **Non-Deceptive Attribution**: The system never simulates living consciousness or pretends to be the deceased person speaking in real time.
2. **Severability of Possession from Cloning Rights**: Possession of oral history recordings, cassette tapes, or home videos does **not** grant rights to synthesize or clone the voice of an identifiable individual.
3. **Point-of-Use Authorization Verification**: Consent is not merely checked upon session creation; it is re-verified synchronously immediately before every custom synthesis request.
4. **Immediate Revocability**: If consent is revoked by a designated kinship guardian, all future synthesis using that profile is immediately blocked across all sessions.
5. **Transparent Fallback**: When custom voice synthesis is unconfigured, pending, or revoked, the system falls back to an explicitly labeled **Generic Synthetic Voice**.

---

## 2. Five Scoped Consent Dimensions

ECHO defines five explicit consent scopes required for voice operations:

| Consent Scope | Description | Enforcing Service | Required For |
|---|---|---|---|
| `VOICE_PROCESSING` | Permission to extract acoustic features, phonemes, and text transcripts from audio. | `TranscriptionService` | Uploading and transcribing oral history tapes. |
| `AI_PROCESSING` | Permission to submit queries to retrieval models, knowledge graphs, and LLM engines. | `ConsentService` / `RAGService` | Any RAG response generation. |
| `CUSTOM_VOICE_SYNTHESIS` | Explicit legal and kinship authorization to synthesize speech imitating an identifiable individual's voice. | `VoiceConsentService` / `TTSService` | Generating audio with an authorized memorial voice profile. |
| `AUDIO_STORAGE` | Permission to retain recorded and synthesized audio assets in project storage. | `VaultStorage` / `TTSService` | Saving audio to `storage/voice/recordings/` or `temp/`. |
| `FAMILY_ACCESS` | Permission to share voice interaction sessions with authorized kinship circle members. | `VoiceProfileService` | Multi-user family viewing and playback. |

---

## 3. Voice Profile Lifecycle & State Machine

Every voice profile follows an audited lifecycle:

```
[ UNCONFIGURED ]
       │ (Metadata registered)
       ▼
[ PENDING_CONSENT ] ──(Kinship documentation verified)──► [ READY ]
       │                                                      │
       │                                                      ├─► [ DISABLED ] (Temporary pause)
       │                                                      │
       └────────────────────(Guardian Revocation)─────────────┴─► [ REVOKED ]
                                                                      │
                                                          (Permanent blackout)
```

### Profile States
- **`UNCONFIGURED`**: Initial state where metadata exists but acoustic assets or provider endpoints have not been established.
- **`PENDING_CONSENT`**: Acoustic models prepared, but mandatory `CUSTOM_VOICE_SYNTHESIS` consent has not yet been verified.
- **`READY`**: Active, verified kinship consent on record; authorized for synthesis.
- **`DISABLED`**: Temporarily suspended by guardian; can be re-enabled without re-submitting legal documentation.
- **`REVOKED`**: Permanently revoked by designated family guardian; all future synthesis requests are blocked.

---

## 4. Synthesis Authorization Algorithm

The following logic executes synchronously inside `voice_consent_service.py` on every text-to-speech request:

```python
async def verify_synthesis_authorization(
    voice_type: VoiceType,
    memorial_profile_id: str,
    voice_profile_id: Optional[str] = None,
    user_id: str = "demo-user-001"
) -> Dict[str, Any]:
    # 1. Base check: Is general AI processing permitted?
    if not await consent_service.is_ai_processing_permitted(memorial_profile_id):
        return {
            "allowed": False,
            "reason": "AI processing consent is revoked or missing for this memorial archive.",
            "fallback_allowed": False
        }

    # 2. Generic synthetic voice requests are allowed under standard AI consent
    if voice_type == VoiceType.GENERIC_SYNTHETIC:
        return {"allowed": True, "reason": "Generic synthetic voice permitted."}

    # 3. Custom memorial voice requires valid profile & unrevoked CUSTOM_VOICE_SYNTHESIS consent
    profile = await voice_profile_service.get_profile(voice_profile_id)
    if not profile or profile.status != VoiceProfileStatus.READY:
        return {
            "allowed": False,
            "reason": f"Voice profile is {profile.status.value if profile else 'NOT_FOUND'}.",
            "fallback_allowed": True
        }

    # 4. Check active kinship consent record
    has_consent = await consent_service.check_consent(
        consent_type=ConsentType.CUSTOM_VOICE_SYNTHESIS,
        memorial_profile_id=memorial_profile_id
    )
    if not has_consent:
        return {
            "allowed": False,
            "reason": "Explicit kinship consent for CUSTOM_VOICE_SYNTHESIS is missing or revoked.",
            "fallback_allowed": True
        }

    return {"allowed": True, "reason": "Authorized memorial voice likeness confirmed."}
```

---

## 5. Mandatory Ethical Disclosures

Every synthesized audio asset contains indelible metadata disclosures:

### Visual Labeling
Synthesized speech displayed in the user interface or audio player must present the prompt:
> **"AI-GENERATED MEMORIAL VOICE — SYNTHETIC AUDIO, NOT AN ORIGINAL RECORDING."**

If generic fallback voice is active:
> **"GENERIC AI-GENERATED SYNTHETIC VOICE — NOT THE MEMORIAL PERSON'S VOICE."**

### Digital Watermarking
Generated audio waveforms embed an unalterable ASCII watermark container in the PCM WAV metadata chunk:
```
[ECHO-AI-MEMORIAL-VOICE-VERIFIED:sha256=<checksum>:timestamp=<iso8601>]
```

### HTTP Delivery Headers
All audio streaming responses include:
- `X-Audio-Category: AI_GENERATED_MEMORIAL_VOICE`
- `X-Ethical-Disclosure: AI-GENERATED MEMORIAL VOICE -- SYNTHETIC AUDIO, NOT AN ORIGINAL RECORDING.`
- `X-SHA256-Checksum: <hex_sha256>`
- `Cache-Control: private, no-cache, no-store, must-revalidate`

---

## 6. Audit Logging & Provenance

All voice operations emit tamper-evident audit records via `audit_service`:

- `VOICE_SESSION_STARTED`
- `VOICE_RECORDING_UPLOADED`
- `SPEECH_TRANSCRIBED`
- `TRANSCRIPT_EDITED`
- `VOICE_SYNTHESIS_REQUESTED`
- `VOICE_SYNTHESIS_COMPLETED`
- `VOICE_SYNTHESIS_BLOCKED`
- `VOICE_PROFILE_CREATED`
- `VOICE_PROFILE_REVOKED`
- `VOICE_PROFILE_DISABLED`
- `VOICE_CONSENT_GRANTED`
- `VOICE_CONSENT_REVOKED`

Audit records track the acting user, memorial profile, timestamp, IP address, and operational metadata, while strictly redacting raw passwords, tokens, and biometric embeddings.
