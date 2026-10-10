# ECHO — Storage Architecture & Security Model

**Project Root:** `D:\ECHO`  
**Storage Subsystem:** `D:\ECHO\storage\`  
**Enclosure:** Local USB Isolated Storage

---

## 1. Storage Directory Topology

All project assets, uploads, and databases are strictly confined under `D:\ECHO\storage\`:

```
D:\ECHO\storage\
├── originals\       # Primary uploaded evidence media (photographs, audio, documents, video)
├── processed\       # Normalized derivatives and future multimodal feature outputs
├── thumbnails\      # Optimized 300x300 image thumbnails for responsive UI rendering
├── temporary\       # Scratch files during ingest/conversion, cleaned immediately upon completion
├── exports\         # Export packages and serialized archival bundles
└── local\           # Development databases (echo_dev.db) and legacy local cache
```

---

## 2. Path Traversal & Escape Prevention

The vault implements path confinement via `VaultStorageManager`:

1. **Resolution and Base Boundary**: Every relative file request is canonicalized using `Path.resolve()`. The resolved target path must satisfy:
   ```python
   target.relative_to(self.root)
   ```
   If the target attempts to navigate outside `self.root` (`D:\ECHO\storage`), a `MaliciousPathError` is raised.
2. **Explicit Sequence Screening**: Any path containing `..`, `\0` (null bytes), or absolute path prefixes (`C:\`, `D:\`, `/etc/`) is rejected prior to filesystem invocation.
3. **HTTP 400 & Security Audit Alert**: Path traversal attempts automatically trigger an `AuditAction.SECURITY_ALERT` entry recording the attacker IP and rejected payload.

---

## 3. Filename Sanitization Rules

Raw filenames from client browsers often contain illegal characters or directory traversal vectors. The vault enforces:
- Removal of directory paths: `os.path.basename()` extracts pure filenames.
- Control character elimination: `re.sub(r'[\x00-\x1f\x7f]', '', filename)`.
- Base alphanumeric preservation: Non-alphanumeric characters (except dots, underscores, and dashes) are converted to underscores.
- Length bounding: Basenames are truncated to 100 characters to prevent buffer issues.
- Safe Storage Naming: Files in `originals/` are stored with their SHA-256 digest prefix:
  `{sha256_hash}_{clean_filename}`.

---

## 4. Zero-Exposure Principle (No Absolute Physical Paths)

In compliance with privacy and security requirements:
- **No Absolute Filesystem Paths**: API responses, JSON exports, and frontend components **never receive physical paths** such as `D:\ECHO\storage\originals\...`.
- **Relative Vault Identifiers**: All assets are referenced exclusively by safe relative identifiers, e.g.:
  - `originals/e3b0c44..._portrait.jpg`
  - `thumbnails/e3b0c44..._thumb.jpg`
- Serving files to authorized users is handled exclusively through authenticated streaming endpoints (`GET /api/v1/media/{id}?download=true`).

---

## 5. Safe Archiving vs. Secure Deletion

1. **Archiving (`POST /api/v1/memories/{id}/archive`)**:
   - Sets `archived = True`.
   - Preserves original media on disk.
   - Hides the memory from default active lists (`include_archived=False`).
   - Retains complete tamper-evident audit history.
   - Can be unarchived/restored at any time.

2. **Deletion (`DELETE /api/v1/memories/{id}`)**:
   - Soft-delete: Sets `deleted_at = datetime.utcnow()`.
   - Records an `AuditAction.DELETE` event.
   - Associated media is only physically deleted if no other memory in the vault shares the same SHA-256 checksum.
