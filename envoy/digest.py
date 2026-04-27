"""Digest module: generate and verify periodic summaries of project state."""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir, load_manifest


class DigestError(Exception):
    pass


def _digest_path(store_dir: Path) -> Path:
    return store_dir / "digests.json"


def _load_digests(store_dir: Path) -> dict:
    p = _digest_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_digests(store_dir: Path, data: dict) -> None:
    _digest_path(store_dir).write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_fingerprint(store_dir: Path, project: str) -> str:
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise DigestError(f"Project '{project}' not found")
    entry = manifest[project]
    raw = json.dumps(entry, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_digest(store_dir: Path, project: str, note: str = "") -> dict[str, Any]:
    """Generate a digest snapshot for a project and persist it."""
    fingerprint = _project_fingerprint(store_dir, project)
    record: dict[str, Any] = {
        "fingerprint": fingerprint,
        "generated_at": _now_iso(),
        "note": note,
    }
    digests = _load_digests(store_dir)
    digests.setdefault(project, []).append(record)
    _save_digests(store_dir, digests)
    return record


def list_digests(store_dir: Path, project: str) -> list[dict]:
    """Return all digest records for a project."""
    digests = _load_digests(store_dir)
    return digests.get(project, [])


def verify_digest(store_dir: Path, project: str, index: int = -1) -> bool:
    """Verify the current fingerprint matches the stored digest at *index*."""
    records = list_digests(store_dir, project)
    if not records:
        raise DigestError(f"No digests found for project '{project}'")
    stored = records[index]["fingerprint"]
    current = _project_fingerprint(store_dir, project)
    return stored == current


def clear_digests(store_dir: Path, project: str) -> None:
    """Remove all digest records for a project."""
    digests = _load_digests(store_dir)
    digests.pop(project, None)
    _save_digests(store_dir, digests)
