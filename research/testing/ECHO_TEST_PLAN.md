# ECHO — Comprehensive End-to-End Test Plan

**Document Version:** 1.0.0  
**Project:** ECHO — AI Digital Memory Twin  
**Tagline:** *Preserve the memories. Hear the voice. See the presence. Keep the story alive.*  
**Target Root:** `D:\ECHO`  
**Execution Environment:** Windows 11 | Python 3.11.9 | Node.js v24.21.0 | Next.js 14.2.35  

---

## 1. Executive Overview and Scope

The ECHO platform is an evidence-grounded, privacy-preserving multimodal artificial intelligence system designed to preserve and interact with memorial archives. This test plan defines the empirical verification strategy across all system layers:

1. **Storage and Filesystem Boundaries** (strict confinement to `D:\ECHO`).
2. **Backend API and Lifespan Services** (FastAPI, SQLite/aiosqlite async, Uvicorn).
3. **Frontend Application Compilation & Routing** (Next.js 14, React 18, Three.js).
4. **Multimodal Archival Processing** (Images, Audio, Video, Documents, SHA-256).
5. **Retrieval-Augmented Generation & Vector Retrieval** (Hybrid search, Chunking).
6. **Memory Guardian & Ethical Guardrails** (18-point verification, anti-confabulation, safe unknowns).
7. **Memorial Voice Synthesis & Consent Management** (Instant revocation, watermarking).
8. **3D Spatial Memory Room & Avatars** (Three.js WebGL, ethical presence notices).
9. **Family Collaboration & RBAC Governance** (Role matrix, single-use invites, dispute handling).
10. **Research Telemetry & Security Defenses** (Audit logging, path traversal, injection immunity).

---

## 2. Test Environment and Baselines

| Parameter | Specification | Verification Method |
|---|---|---|
| **Root Path** | `D:\ECHO` | Absolute path check |
| **Storage Root** | `D:\ECHO\storage\local` | Directory existence & permissions |
| **Python Runtime** | Python 3.11.9 (Windows Store / System) | `python --version` |
| **Node.js Runtime** | Node.js v24.21.0 | `node --version` |
| **Package Manager** | npm 11.19.0 | `npm --version` |
| **Backend Port** | `127.0.0.1:8000` | Sockets listener inspection |
| **Frontend Port** | `http://localhost:3000` | HTTP GET inspection |
| **AI Mode** | Deterministic Offline Mock Providers | `LLM_PROVIDER=mock`, `STT_PROVIDER=mock` |

---

## 3. Test Methodology & Pyramid

The testing strategy encompasses four levels:
1. **Unit & Property Tests:** Direct component isolation (crypto hashes, schema serialization, confidence math).
2. **Integration Tests:** Component interactions (Vault upload -> Processing -> Evidence -> Guardian validation).
3. **End-to-End Synthetic Workflows:** Full user journeys simulating Vault Owner, Family Member, and Researcher personas.
4. **Defensive Security & Boundary Probes:** Malicious payload injection, path traversal attempts, consent bypass tests.

---

## 4. Test Matrix & Coverage Dimensions

| Dimension | Scope | Target Test Suites | Expected Outcome |
|---|---|---|---|
| **D1: Type & Build** | Frontend TypeScript & Next.js production build | `npx tsc --noEmit`<br>`npm run build` | 0 type errors; 25 routes compiled |
| **D2: API & Health** | FastAPI endpoints & OpenAPI schema | `test_health.py`<br>`GET /health`, `GET /docs` | HTTP 200 `healthy`, 140 routes in schema |
| **D3: Vault Lifecycle** | Archival upload, SHA-256, CRUD | `test_phase2_vault.py`<br>`test_phase10_e2e_workflows.py` | Cryptographic integrity match; 0 residual leaks |
| **D4: Unknowns & Guard** | Anti-confabulation, unknown answer preservation | `test_phase5_rag_guardian.py`<br>`test_phase9_guardian_evaluation.py` | Safe unknown delivered; zero evidence never hallucinates |
| **D5: Voice & Consent** | Speech pipeline, legal consent, watermarking | `test_phase6_voice.py` | Blocked without consent; instant revoke; RIFF watermark |
| **D6: 3D Room & Timeline** | Spatial room, avatar notices, chronologies | `test_phase7_memory_room.py`<br>`test_phase8_collaboration.py` | Avatar notice present; timeline ordered; self-approval blocked |
| **D7: RBAC & Privacy** | Role escalation, boundary isolation, auth | `test_phase9_security.py`<br>`test_phase10_security_privacy_regression.py` | Visitor blocked from audit; private memories isolated |
| **D8: Research Metrics** | Benchmark evaluation, F1, boundary score | `test_phase9_research_metrics.py` | 0.0% boundary violations; exact benchmark computation |
| **D9: Storage & Backup** | Directory isolation, dry-run backup | `scripts/run_tests.ps1`<br>`scripts/backup_vault.py` | 7 storage directories confirmed; 300+ files verified |
| **D10: Ethical Notices** | Multi-surface AI memorial disclaimer | `test_ethical_boundaries.py` | Consciousness simulation rejected; disclaimers active |

---

## 5. Test Personas & Role Matrix

| Persona | Role Identifier | Authorized Actions | Restricted Actions |
|---|---|---|---|
| **Vault Owner** | `VAULT_OWNER` | Upload, edit, delete, grant/revoke consent, audit logs | None |
| **Family Member** | `FAMILY_MEMBER` | View verified memories, submit contributions, listen to voice | Cannot approve own contribution, cannot view revoked data |
| **Researcher** | `RESEARCHER` | Query benchmark metrics, inspect de-identified evidence | Cannot access unredacted private memories |
| **Visitor** | `VISITOR` | View public memorial memories | Cannot upload, cannot access audit logs or private memories |

---

## 6. Execution Command Sequence

```powershell
# 1. Typecheck and build verification
cd D:\ECHO\frontend
npx tsc --noEmit
npm run build

# 2. Automated Python regression suite
cd D:\ECHO
python -m pytest tests/ -v

# 3. 10-Dimension verification suite
python tests/final_verification_suite.py

# 4. PowerShell operational suite
powershell -ExecutionPolicy Bypass -File D:\ECHO\scripts\run_tests.ps1

# 5. Live service socket probes
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
```
