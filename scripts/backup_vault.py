"""ECHO Vault Backup and Disaster Recovery Utility.

Confined strictly to D:\\ECHO.
Provides operational backup, verification, and recovery for:
- Database files: D:\\ECHO\\storage\\local\\echo_dev.db
- Vault storage assets: D:\\ECHO\\storage\\originals, processed, thumbnails
- Research telemetry and audit manifests

Security & Safety Rules:
- Never overwrites live production databases without explicit user confirmation.
- Generates cryptographically secure SHA-256 manifest to detect bit-rot/tampering.
- Conforms strictly to storage boundaries.
"""

import os
import sys
import argparse
import hashlib
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path("D:/ECHO").resolve()
STORAGE_ROOT = PROJECT_ROOT / "storage"
LOCAL_DB_PATH = STORAGE_ROOT / "local" / "echo_dev.db"
EXPORTS_DIR = STORAGE_ROOT / "exports"


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a physical file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def create_backup(
    destination_dir: Optional[Path] = None,
    include_media: bool = True,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Create a verified snapshot archive of the database and vault storage."""
    dest = (destination_dir or EXPORTS_DIR).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_name = f"echo_vault_backup_{timestamp}.zip"
    archive_path = dest / archive_name

    items_to_backup: List[Path] = []

    # 1. Database file
    if LOCAL_DB_PATH.exists():
        items_to_backup.append(LOCAL_DB_PATH)

    # 2. Vault media directories
    if include_media:
        for sub in ["originals", "processed", "thumbnails"]:
            sub_dir = STORAGE_ROOT / sub
            if sub_dir.exists():
                for p in sub_dir.rglob("*"):
                    if p.is_file() and not p.name.startswith("."):
                        items_to_backup.append(p)

    manifest: Dict[str, Any] = {
        "backup_version": "1.0.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "storage_root": str(STORAGE_ROOT),
        "total_files": len(items_to_backup),
        "files": {}
    }

    total_bytes = 0
    for file_path in items_to_backup:
        rel_key = str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        file_size = file_path.stat().st_size
        total_bytes += file_size
        checksum = calculate_sha256(file_path)
        manifest["files"][rel_key] = {
            "size_bytes": file_size,
            "sha256": checksum
        }

    manifest["total_size_bytes"] = total_bytes

    if dry_run:
        return {
            "status": "DRY_RUN",
            "archive_path": str(archive_path),
            "manifest": manifest,
            "total_files": len(items_to_backup),
            "total_bytes": total_bytes
        }

    # Write Zip Archive
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Write manifest
        zipf.writestr("manifest.json", json.dumps(manifest, indent=2))
        
        # Write files preserving relative path
        for file_path in items_to_backup:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            zipf.write(file_path, arcname=str(rel_path).replace("\\", "/"))

    archive_checksum = calculate_sha256(archive_path)

    return {
        "status": "SUCCESS",
        "archive_path": str(archive_path),
        "archive_checksum_sha256": archive_checksum,
        "total_files": len(items_to_backup),
        "total_bytes": total_bytes,
        "manifest": manifest
    }


def verify_backup(archive_path: Path) -> Dict[str, Any]:
    """Verify archive integrity and compare file hashes against embedded manifest."""
    if not archive_path.exists():
        raise FileNotFoundError(f"Backup archive not found: {archive_path}")

    with zipfile.ZipFile(archive_path, "r") as zipf:
        if "manifest.json" not in zipf.namelist():
            raise ValueError("Invalid backup archive: missing manifest.json")

        manifest_data = json.loads(zipf.read("manifest.json").decode("utf-8"))
        files_manifest = manifest_data.get("files", {})

        verified_files = 0
        corrupted_files: List[str] = []

        for rel_path, meta in files_manifest.items():
            if rel_path not in zipf.namelist():
                corrupted_files.append(f"Missing file in archive: {rel_path}")
                continue

            content = zipf.read(rel_path)
            actual_hash = hashlib.sha256(content).hexdigest()
            if actual_hash != meta["sha256"]:
                corrupted_files.append(f"Hash mismatch for {rel_path}: expected {meta['sha256']}, got {actual_hash}")
            else:
                verified_files += 1

    return {
        "status": "VERIFIED" if not corrupted_files else "CORRUPTED",
        "archive_path": str(archive_path),
        "verified_files": verified_files,
        "corrupted_count": len(corrupted_files),
        "errors": corrupted_files,
        "manifest_timestamp": manifest_data.get("timestamp_utc")
    }


def restore_backup(
    archive_path: Path,
    target_root: Path,
    overwrite: bool = False
) -> Dict[str, Any]:
    """Safely restore backup contents into a target directory."""
    if not archive_path.exists():
        raise FileNotFoundError(f"Backup archive not found: {archive_path}")

    verification = verify_backup(archive_path)
    if verification["status"] != "VERIFIED":
        raise ValueError(f"Cannot restore corrupted archive: {verification['errors']}")

    target_root = target_root.resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    restored_files: List[str] = []

    with zipfile.ZipFile(archive_path, "r") as zipf:
        manifest_data = json.loads(zipf.read("manifest.json").decode("utf-8"))
        files_manifest = manifest_data.get("files", {})

        for rel_path in files_manifest.keys():
            dest_path = target_root / rel_path
            if dest_path.exists() and not overwrite:
                raise FileExistsError(f"File exists and overwrite is False: {dest_path}")

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            content = zipf.read(rel_path)
            with open(dest_path, "wb") as f:
                f.write(content)
            restored_files.append(str(dest_path))

    return {
        "status": "SUCCESS",
        "target_root": str(target_root),
        "restored_count": len(restored_files),
        "restored_files": restored_files
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ECHO Vault Backup & Disaster Recovery")
    parser.add_argument("--backup", action="store_true", help="Create new vault backup")
    parser.add_argument("--verify", type=str, help="Verify existing backup archive path")
    parser.add_argument("--restore", type=str, help="Restore archive path")
    parser.add_argument("--target-dir", type=str, help="Restore target directory")
    parser.add_argument("--overwrite", action="store_true", help="Allow file overwrites during restore")
    parser.add_argument("--dry-run", action="store_true", help="Simulate backup without writing archive")

    args = parser.parse_args()

    if args.backup:
        print("[ECHO] Initiating Vault Backup...")
        res = create_backup(dry_run=args.dry_run)
        print(json.dumps(res, indent=2))
    elif args.verify:
        print(f"[ECHO] Verifying Backup: {args.verify}")
        res = verify_backup(Path(args.verify))
        print(json.dumps(res, indent=2))
    elif args.restore:
        if not args.target_dir:
            print("[ERROR] --target-dir is required for restoration to prevent unintended overwrites.")
            sys.exit(1)
        print(f"[ECHO] Restoring Backup {args.restore} to {args.target_dir}")
        res = restore_backup(Path(args.restore), Path(args.target_dir), overwrite=args.overwrite)
        print(json.dumps(res, indent=2))
    else:
        parser.print_help()
