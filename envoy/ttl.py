"""TTL (time-to-live) support for stored env projects."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


class TTLError(Exception):
    pass


def _ttl_path(store_dir: Optional[Path] = None) -> Path:
    return (store_dir or get_store_dir()) / "ttl.json"


def _load_ttls(store_dir: Optional[Path] = None) -> dict:
    path = _ttl_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_ttls(data: dict, store_dir: Optional[Path] = None) -> None:
    _ttl_path(store_dir).write_text(json.dumps(data, indent=2))


def set_ttl(project: str, seconds: int, store_dir: Optional[Path] = None) -> str:
    """Set a TTL for a project. Returns the ISO expiry timestamp."""
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    ttls = _load_ttls(store_dir)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()
    ttls[project] = {"expires_at": expires_at, "seconds": seconds}
    _save_ttls(ttls, store_dir)
    return expires_at


def get_ttl(project: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    """Return TTL info for a project, or None if not set."""
    return _load_ttls(store_dir).get(project)


def remove_ttl(project: str, store_dir: Optional[Path] = None) -> None:
    """Remove TTL for a project."""
    ttls = _load_ttls(store_dir)
    if project not in ttls:
        raise TTLError(f"No TTL set for project '{project}'.")
    del ttls[project]
    _save_ttls(ttls, store_dir)


def is_expired(project: str, store_dir: Optional[Path] = None) -> bool:
    """Return True if the project's TTL has passed."""
    ttls = _load_ttls(store_dir)
    if project not in ttls:
        return False
    expires_at = datetime.fromisoformat(ttls[project]["expires_at"])
    return datetime.now(timezone.utc) >= expires_at


def list_ttls(store_dir: Optional[Path] = None) -> dict:
    """Return all TTL entries."""
    return _load_ttls(store_dir)
