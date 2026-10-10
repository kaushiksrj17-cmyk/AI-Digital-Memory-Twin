# ECHO — Family Collaboration & Access Control Architecture

**Research Title:** Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation.  
**Project Tagline:** "Preserve the memories. Hear the voice. See the presence. Keep the story alive."

---

## 1. Overview & Collaboration Principles

Preserving digital memory is inherently a multi-generational, collaborative family endeavor. However, unconstrained family editing risks overwriting authentic historical testimony, leaking sensitive confidences, or triggering family disputes without proper provenance.

Phase 8 implements **Family Workspaces & Role-Based Access Control (RBAC)** to enable authorized family members, descendants, and trusted archivists to participate while maintaining strict cryptographic security and evidence integrity.

---

## 2. 4-Tier RBAC Permission Matrix

The system enforces four well-defined roles across all backend API routes (`models/enums.py` & `backend/app/services/family_service.py`):

| Permission Capability | OWNER | FAMILY_ADMIN | CONTRIBUTOR | VIEWER |
|---|:---:|:---:|:---:|:---:|
| **Archive Ownership & Workspace Settings** | Yes | No | No | No |
| **Manage Family Members & Assign Roles** | Yes | Yes (Up to CONTRIBUTOR) | No | No |
| **Create & Send Invitations** | Yes | Yes | No | No |
| **Revoke Invitations & Remove Members** | Yes | Yes (Non-OWNER) | No | No |
| **Review & Approve Proposed Contributions** | Yes | Yes | No | No |
| **Resolve Contested Dates & Disputes** | Yes | Yes | No | No |
| **Execute Duplicate Entity Merging** | Yes | Yes | No | No |
| **Submit Memories, Documents & Photos** | Yes | Yes | Yes | No |
| **Suggest Timeline Events & Relationships** | Yes | Yes | Yes | No |
| **Propose Metadata Corrections & Context** | Yes | Yes | Yes | No |
| **Approve Own Submissions (Self-Approval)** | **BLOCKED** | **BLOCKED** | **BLOCKED** | **BLOCKED** |
| **View Verified Life Timeline & Graph** | Yes | Yes | Yes | Yes |
| **Access Original Media (Authenticated)** | Yes | Yes | Permitted Only | Permitted Only |
| **Inspect System Audit Logs & Research Telemetry** | Yes | Yes | No | No |

### Role Breakdown

1. **`OWNER`**:
   - The primary custodian of the digital memory twin archive.
   - Holds unrestricted authority over workspace configuration, deletion operations, and consent directives.
   - May appoint or dismiss `FAMILY_ADMIN` members.

2. **`FAMILY_ADMIN`**:
   - Authorized family administrator assisting in curation and review.
   - Reviews contribution queues, resolves historical disputes, and executes entity merges.
   - Can invite `CONTRIBUTOR` or `VIEWER` members, but cannot alter `OWNER` status or assign roles higher than their own.

3. **`CONTRIBUTOR`**:
   - Trusted family members, friends, or associates who contribute stories, photos, letters, and corrections.
   - All proposed additions and modifications enter an asynchronous review queue (`PENDING_REVIEW` / `SUBMITTED`).
   - Contributor submissions **never** directly mutate verified records until approved by an independent reviewer.

4. **`VIEWER`**:
   - Read-only family members and extended relatives.
   - Can explore the verified Life Timeline, interactive 3D Memory Room, and Relationship Graph.
   - Cannot create, edit, dispute, or approve archive records.

---

## 3. Secure Single-Use Invitation Lifecycle

Invitations must be protected against tampering, interception, link reuse, and privilege escalation:

```
[Authorized User]
       │
       ▼ (1) Create Invitation (Target Email, Role, Expiration: 7 Days)
[Backend FamilyService]
       │
       ├─► Generates 32-byte cryptographic token: secrets.token_urlsafe(32)
       ├─► Computes SHA-256 hash of token: hashlib.sha256(token).hexdigest()
       ├─► Stores token_hash, status="PENDING" in SQLite/PostgreSQL
       └─► Returns invitation link with plaintext token to inviter
       │
       ▼ (2) Invitee Receives Link: /family/accept-invite?token=...
[Invitee Authenticates & Accepts]
       │
       ├─► Hashes provided token with SHA-256
       ├─► Finds invitation record matching token_hash
       ├─► Validates: status == "PENDING"
       ├─► Validates: expires_at > now()
       ├─► Validates: role <= inviter_max_permitted_role
       │
       ▼ (3) State Transition & Audit
       ├─► status = "ACCEPTED", accepted_at = now()
       ├─► Creates FamilyMemberRecord in workspace
       └─► Logs FamilyInvitationAccepted in immutable audit log
```

### Security Safeguards

1. **No Plaintext Token Storage**:
   - Only the SHA-256 digest (`token_hash`) is persisted in the database. Compromising the database never exposes usable invitation links.
2. **Strict Single-Use Invariant**:
   - Once accepted, `status` becomes `ACCEPTED`. Subsequent attempts with the same token fail with `InvitationAlreadyUsedError`.
3. **Cryptographic Expiration**:
   - Invitations expire after a configurable window (default: 7 days). Expired tokens fail with `InvitationExpiredError`.
4. **Revocation Authority**:
   - Admins and owners can revoke pending invitations at any time. Revoked tokens immediately fail with `InvitationRevokedError`.
5. **Privilege Escalation Block**:
   - A `FAMILY_ADMIN` cannot generate an invitation with role `OWNER` or `FAMILY_ADMIN`. Attempting to do so triggers an explicit `PrivilegeEscalationError`.

---

## 4. Frontend Experience (`/family`)

The Family Collaboration page (`frontend/src/app/family/page.tsx`) provides:
- **Member Directory**: Shows family members, active roles, joined dates, and actions.
- **Invitation Modal**: Form for creating invitations with email and role selection, generating copyable single-use links.
- **Pending Invitations Tab**: Lists outstanding invitations with one-click revocation.
- **Phase 8 Research Telemetry Cards**:
  - Contribution Approval Rate (%)
  - Contested Dates Count
  - Average Review Turnaround Time (hours)
  - Unauthorized Access Attempts prevented

All actions respect the current user's role and disable or hide forbidden interactions on both client and server sides.
