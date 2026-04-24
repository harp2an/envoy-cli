"""Retention policy management for envoy projects."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir, load_manifest


class RetentionError(Exception):
    pass


def _retention_path(store_dir: Path) -> Path:
    return store_dir / "retention.json"


def _load_retention(store_dir: Path) -> dict:
    path = _retention_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_retention(store_dir: Path, data: dict) -> None:
    _retention_path(store_dir).write_text(json.dumps(data, indent=2))


def set_retention(store_dir: Path, project: str, max_versions: int, max_snapshots: int) -> dict:
    """Set retention limits for a project."""
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise RetentionError(f"Project '{project}' not found")
    if max_versions < 1:
        raise RetentionError("max_versions must be at least 1")
    if max_snapshots < 1:
        raise RetentionError("max_snapshots must be at least 1")

    data = _load_retention(store_dir)
    data[project] = {"max_versions": max_versions, "max_snapshots": max_snapshots}
    _save_retention(store_dir, data)
    return data[project]


def get_retention(store_dir: Path, project: str) -> Optional[dict]:
    """Return retention settings for a project, or None if not set."""
    data = _load_retention(store_dir)
    return data.get(project)


def remove_retention(store_dir: Path, project: str) -> None:
    """Remove retention settings for a project."""
    data = _load_retention(store_dir)
    if project not in data:
        raise RetentionError(f"No retention policy for project '{project}'")
    del data[project]
    _save_retention(store_dir, data)


def list_retention(store_dir: Path) -> dict:
    """Return all retention policies."""
    return _load_retention(store_dir)
