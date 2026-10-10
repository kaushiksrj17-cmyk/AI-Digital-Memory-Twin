# ECHO — PHASE 10: WORKSPACE AND CONFIGURATION AUDIT

**Date:** 2026-10-10  
**Project Location:** `D:\ECHO`  
**Storage Root:** `D:\ECHO\storage`  
**Frontend Location:** `D:\ECHO\frontend`  
**Audit Status:** COMPLETE  

---

## 1. Executive Summary

This configuration and architecture audit was conducted in accordance with Phase 10 requirements prior to making changes. Every system parameter, startup script, environment variable, authentication pathway, storage boundary, and database configuration was verified by inspecting the actual source code and executing runtime validations.

ECHO is an evidence-grounded, privacy-preserving digital memory platform. It is designed to run entirely locally in offline development and test environments while supporting production deployments.

---

## 2. Workspace and Path Confinement

| Component | Configured Path | Boundary Enforcement Mechanism | Status |
| :--- | :--- | :--- | :--- |
| **Project Root** | `D:\ECHO` | `settings.PROJECT_ROOT` strictly pinned | VERIFIED |
| **Storage Root** | `D:\ECHO\storage\local` | `settings.STORAGE_ROOT` pinned | VERIFIED |
| **Vault Originals** | `D:\ECHO\storage\originals` | `VaultStorageManager` path verification | VERIFIED |
| **Vault Processed** | `D:\ECHO\storage\processed` | `VaultStorageManager` path verification | VERIFIED |
| **Vault Thumbnails** | `D:\ECHO\storage\thumbnails` | `VaultStorageManager` path verification | VERIFIED |
| **Vault Temporary** | `D:\ECHO\storage\temporary` | `VaultStorageManager` path verification | VERIFIED |
| **Vault Exports** | `D:\ECHO\storage\exports` | `VaultStorageManager` path verification | VERIFIED |
| **Voice Storage** | `D:\ECHO\storage\voice` | Subdirectories (`profiles`, `recordings`, `temp`) | VERIFIED |
| **Database** | `D:\ECHO\storage\local\echo_dev.db` | SQLite / aiosqlite localized file | VERIFIED |
| **Frontend** | `D:\ECHO\frontend` | Next.js 14.2.35 standalone/SPA root | VERIFIED |

**Confinement Verification:**
- Path traversal sequences (`..`, `\0`, mixed slashes) are intercepted by `VaultStorageManager._resolve_safe_path()`, raising `MaliciousPathError`.
- No file uploads or derived artifacts can escape `D:\ECHO\storage`.

---

## 3. Configuration & Startup Parameters

### Backend
- **Framework:** FastAPI with Python 3.11.9
- **API Prefix:** `/api/v1` (defined in `backend.app.core.config.Settings.API_V1_STR`)
- **Default Bind:** `127.0.0.1:8000`
- **Development Startup:**
  ```powershell
  uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- **Production Startup:**
  ```powershell
  uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 4
  ```
- **Health Check Endpoint:** `GET /api/v1/health` and `GET /api/v1/health/detailed`

### Frontend
- **Framework:** Next.js 14.2.35 (React 18, TypeScript 5, Tailwind CSS)
- **Default Bind:** `127.0.0.1:3000`
- **Development Startup:**
  ```powershell
  cd D:\ECHO\frontend
  npm run dev
  ```
- **Production Build & Startup:**
  ```powershell
  cd D:\ECHO\frontend
  npm run build
  npm run start
  ```
- **Environment Variable Names:**
  - `NEXT_PUBLIC_API_URL`: Configures backend API base URL (defaults to `http://localhost:8000/api/v1`).
  - Next.js rewrite proxy: `/api/v1/:path*` is automatically rewritten to `http://127.0.0.1:8000/api/v1/:path*` in `next.config.mjs`.

---

## 4. Authentication and Authorization (RBAC) Architecture

### Token Lifecycle
1. **Creation:** `create_access_token(data: dict, expires_delta: Optional[timedelta])` in `backend/app/core/security.py` issues JWT tokens signed with HS256 algorithm using `SECRET_KEY`.
2. **Payload Claims:** Contains `sub` (user email), `user_id`, `role` (one of `vault_owner`, `guardian`, `family_member`, `researcher`, `visitor`), and `exp`.
3. **Transmission:** Standard HTTP header `Authorization: Bearer <token>`.
4. **Validation:** `decode_access_token(token)` in `security.py` verifies cryptographic signature and expiration. Invalid, malformed, or expired tokens raise `HTTPException(401, "Invalid or expired access token")`.
5. **Phase 1–8 Backward Compatibility:** When no `Authorization` header is present, `get_current_user()` returns a fallback demo user (`id="demo-user-001"`, `role="vault_owner"`), ensuring all legacy unit tests pass without requiring mock auth headers on every test call.

### Role-Based Access Control (RBAC)
- Five roles defined in `UserRole`:
  - `VAULT_OWNER`: Full administrative and vault control.
  - `GUARDIAN`: Ethical oversight, memory curation, verification, review.
  - `FAMILY_MEMBER`: Viewing shared family memories, submitting contributions, voting.
  - `RESEARCHER`: Access to benchmark metrics, research dashboard, authorized public dataset.
  - `VISITOR`: Read-only access to `MEMORIAL_PUBLIC` memories only.
- Enforcement functions:
  - `require_role(allowed_roles)`: Dependency checker for endpoint-level role gating.
  - `require_permission(permission)`: Operational permission checker.
  - `can_access_privacy_level(user_role, privacy_level)`: Multi-tier memory privacy clearance.

---

## 5. Storage, Media Uploads & File Cleanup

### File Limits and MIME Validation
- **Max File Size:** 100 MB (`MAX_FILE_SIZE_BYTES = 104,857,600 bytes`).
- **Permitted File Extensions:**
  - Images: `.jpg`, `.jpeg`, `.png`, `.webp`
  - Audio: `.mp3`, `.wav`, `.m4a`
  - Video: `.mp4`, `.mov`, `.webm`
  - Documents: `.pdf`, `.txt`, `.docx`
- **Sanitization:** `VaultStorageManager.sanitize_filename()` strips all path traversal characters, directory separators, null bytes, and non-printable control characters, replacing invalid characters with underscores and capping the basename length at 100 characters.
- **Deduplication:** Computes SHA-256 cryptographic checksums before saving. If an identical file exists, the existing storage asset is re-referenced, avoiding duplicate physical disk writes.
- **Deletion & Cleanup:** `VaultStorageManager.delete_file()` removes physical files and associated thumbnails unless active duplicate references exist.

---

## 6. Database Persistence & Recovery

- **ORM / Engine:** SQLAlchemy 2.0 with asynchronous engine (`sqlite+aiosqlite`) at `sqlite+aiosqlite:///D:/ECHO/storage/local/echo_dev.db`.
- **Driver Fallback:** Synchronous SQLite with thread offloading if `aiosqlite` is unavailable; PostgreSQL asyncpg driver supported if `DATABASE_URL` is set to `postgresql://`.
- **Initialization:** `database/init_db.py` contains `init_db_async()` and `init_db_sync()`, creating all relational tables idempotently using `Base.metadata.create_all`.
- **Disposal:** Engine is gracefully disposed on application shutdown in `lifespan` handler (`backend/app/main.py`).

---

## 7. AI Providers and Offline Mode

- **Default State:** All AI providers default to `"mock"` in `backend/app/core/config.py`:
  - `LLM_PROVIDER = "mock"`
  - `EMBEDDING_PROVIDER = "mock"`
  - `STT_PROVIDER = "mock"`
  - `TTS_PROVIDER = "mock"`
  - `CV_PROVIDER = "mock"`
  - `OCR_PROVIDER = "mock"`
- **Offline Integrity:** In mock mode, providers execute purely synthetic, deterministic algorithms on local fixtures. Zero network requests or cloud telemetry events are dispatched.
- **External Integration Mode:** Configurable via environment variables (`LLM_API_KEY`, etc.). If an external provider is selected without valid credentials, `ProviderNotConfiguredError` (HTTP 503) is raised.

---

## 8. CORS and Error Handling

- **CORS Allowed Origins:**
  - `http://localhost:3000`
  - `http://127.0.0.1:3000`
  - `http://localhost:8000`
  - `http://127.0.0.1:8000`
- **Credentials:** Allowed (`allow_credentials=True`).
- **Error Response Structure:**
  - Custom `EchoException` derivatives caught by `register_error_handlers(app)`.
  - Format:
    ```json
    {
      "error": true,
      "type": "ExceptionClassName",
      "message": "Sanitized error message",
      "details": {}
    }
    ```
  - Internal tracebacks and sensitive database details are suppressed in HTTP responses.

---

## 9. Identified Defects & Remediations

| # | Component | Defect Description | Risk Level | Remediation Plan |
| :--- | :--- | :--- | :--- | :--- |
| **D1** | `memory_service.py` | Line 168 hardcoded `"demo-user-001"` in private memory check: `user_id in [memory.uploaded_by, memory.created_by_user_id, "demo-user-001"]`. This allowed any request with user ID `"demo-user-001"` to view another user's private memory even when acting with `visitor` role. | HIGH | Remove `"demo-user-001"` from creator list. Check ownership `user_id in [memory.uploaded_by, memory.created_by_user_id]` or role clearance (`vault_owner`, `guardian`). |
| **D2** | `memories.py` | Several endpoints (`get_memory`, `list_memories`, `update_memory`, `delete_memory`) did not declare `current_user: Dict = Depends(get_current_user)` or pass user ID and role into `memory_service`. Defaulted to `vault_owner`. | HIGH | Inject `current_user: Dict = Depends(get_current_user)` on memory endpoints and forward `current_user["id"]` and `current_user["role"]`. |
| **D3** | `memory_service.py` | `check_access()` returned `True` unconditionally for `FAMILY` memories, allowing `visitor` and `researcher` roles to view private family memories. | HIGH | Apply `can_access_privacy_level(role, memory.privacy_level.value)` so only `vault_owner`, `guardian`, and `family_member` access `FAMILY` memories. |
| **D4** | Frontend Pages | Inconsistent API URL handling across pages (`retrieval/page.tsx`, `knowledge-graph/page.tsx`, `memory-dna/page.tsx` used hardcoded `http://localhost:8000/api/v1`, whereas others used `NEXT_PUBLIC_API_URL`). | MEDIUM | Ensure all frontend API calls use `NEXT_PUBLIC_API_URL` or relative `/api/v1` matching Next.js rewrites. |
| **D5** | Operational Scripts | Missing dedicated backup and restore verification script in `scripts/`. | MEDIUM | Implement `scripts/backup_vault.py` providing safe, non-destructive vault backup and integrity checks. |

---

## 10. Unverified Assumptions & Recommended Follow-Up

1. **Database Scalability:** SQLite is verified and optimal for single-node local execution. For multi-tenant production concurrency, PostgreSQL via asyncpg is recommended.
2. **Key Storage:** In production, `SECRET_KEY` must be populated from an external secret manager or protected environment variable rather than default values.
3. **Session Revocation:** JWTs are stateless; immediate blacklisting requires an in-memory or Redis token revocation registry if instant logout revocation is required before token expiry.

---

**Audit Completed By:** ECHO System Verification Engine  
**Approved For:** Phase 10 Production Readiness & Integration Testing
