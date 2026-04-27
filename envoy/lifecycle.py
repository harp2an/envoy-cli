"""Lifecycle management for projects: track creation, activation, deprecation, and archival states."""

import json
from datetime import datetime, timezone
from pathlib import Path
from envoy.storage import get_store_dir, load_manifest


class LifecycleError(Exception):
    pass


VALID_STATES = ("active", "inactive", "deprecated", "archived")


def _lifecycle_path(store_dir: Path) -> Path:
    return store_dir / "lifecycle.json"


def _load_lifecycle(store_dir: Path) -> dict:
    path = _lifecycle_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_lifecycle(store_dir: Path, data: dict) -> None:
    _lifecycle_path(store_dir).write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def set_state(project: str, state: str, store_dir: Path | None = None) -> dict:
    """Set the lifecycle state of a project."""
    if state not in VALID_STATES:
        raise LifecycleError(f"Invalid state '{state}'. Must be one of: {', '.join(VALID_STATES)}")
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise LifecycleError(f"Project '{project}' not found.")
    data = _load_lifecycle(store_dir)
    entry = data.get(project, {"created_at": _now_iso()})
    entry["state"] = state
    entry["updated_at"] = _now_iso()
    data[project] = entry
    _save_lifecycle(store_dir, data)
    return entry


def get_state(project: str, store_dir: Path | None = None) -> dict | None:
    """Return the lifecycle entry for a project, or None if unset."""
    store_dir = store_dir or get_store_dir()
    data = _load_lifecycle(store_dir)
    return data.get(project)


def list_states(store_dir: Path | None = None) -> dict:
    """Return all lifecycle entries."""
    store_dir = store_dir or get_store_dir()
    return _load_lifecycle(store_dir)


def remove_state(project: str, store_dir: Path | None = None) -> bool:
    """Remove lifecycle tracking for a project. Returns True if removed."""
    store_dir = store_dir or get_store_dir()
    data = _load_lifecycle(store_dir)
    if project not in data:
        return False
    del data[project]
    _save_lifecycle(store_dir, data)
    return True
