"""Project expiry management: set, check, and clear expiry dates for projects."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir, load_manifest


class ExpiryError(Exception):
    pass


def _expiry_path(store_dir: Path) -> Path:
    return store_dir / "expiry.json"


def _load_expiries(store_dir: Path) -> dict:
    path = _expiry_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_expiries(store_dir: Path, data: dict) -> None:
    _expiry_path(store_dir).write_text(json.dumps(data, indent=2))


def set_expiry(project: str, expires_at: str, store_dir: Optional[Path] = None) -> str:
    """Set an ISO-8601 expiry timestamp for a project. Returns the stored timestamp."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ExpiryError(f"Project '{project}' not found.")
    try:
        dt = datetime.fromisoformat(expires_at)
    except ValueError:
        raise ExpiryError(f"Invalid datetime format: '{expires_at}'. Use ISO-8601.")
    iso = dt.isoformat()
    data = _load_expiries(store_dir)
    data[project] = iso
    _save_expiries(store_dir, data)
    return iso


def get_expiry(project: str, store_dir: Optional[Path] = None) -> Optional[str]:
    """Return the expiry timestamp for a project, or None if not set."""
    store_dir = store_dir or get_store_dir()
    return _load_expiries(store_dir).get(project)


def remove_expiry(project: str, store_dir: Optional[Path] = None) -> None:
    """Remove the expiry for a project. Raises ExpiryError if not set."""
    store_dir = store_dir or get_store_dir()
    data = _load_expiries(store_dir)
    if project not in data:
        raise ExpiryError(f"No expiry set for project '{project}'.")
    del data[project]
    _save_expiries(store_dir, data)


def is_expired(project: str, store_dir: Optional[Path] = None) -> bool:
    """Return True if the project has an expiry set and it is in the past."""
    store_dir = store_dir or get_store_dir()
    expiry = get_expiry(project, store_dir)
    if expiry is None:
        return False
    dt = datetime.fromisoformat(expiry)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return datetime.now(tz=timezone.utc) > dt


def list_expiries(store_dir: Optional[Path] = None) -> dict:
    """Return all project expiry entries as a dict of {project: iso_timestamp}."""
    store_dir = store_dir or get_store_dir()
    return dict(_load_expiries(store_dir))
