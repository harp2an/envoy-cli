"""Badge generation for project status summaries."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir, load_manifest


class BadgeError(Exception):
    pass


def _badge_path(store_dir: Path) -> Path:
    return store_dir / "badges.json"


def _load_badges(store_dir: Path) -> dict[str, Any]:
    p = _badge_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_badges(store_dir: Path, data: dict[str, Any]) -> None:
    _badge_path(store_dir).write_text(json.dumps(data, indent=2))


def generate_badge(project: str, store_dir: Path | None = None) -> dict[str, Any]:
    """Generate a status badge dict for *project*."""
    if store_dir is None:
        store_dir = get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise BadgeError(f"Project '{project}' not found in manifest.")
    meta = manifest[project]
    badge = {
        "project": project,
        "status": "ok",
        "keys": meta.get("keys", 0),
        "updated": meta.get("updated", "unknown"),
    }
    badges = _load_badges(store_dir)
    badges[project] = badge
    _save_badges(store_dir, badges)
    return badge


def get_badge(project: str, store_dir: Path | None = None) -> dict[str, Any] | None:
    """Return the last generated badge for *project*, or None."""
    if store_dir is None:
        store_dir = get_store_dir()
    return _load_badges(store_dir).get(project)


def remove_badge(project: str, store_dir: Path | None = None) -> None:
    """Remove the stored badge for *project*."""
    if store_dir is None:
        store_dir = get_store_dir()
    badges = _load_badges(store_dir)
    if project not in badges:
        raise BadgeError(f"No badge found for project '{project}'.")
    del badges[project]
    _save_badges(store_dir, badges)


def list_badges(store_dir: Path | None = None) -> list[dict[str, Any]]:
    """Return all stored badges."""
    if store_dir is None:
        store_dir = get_store_dir()
    return list(_load_badges(store_dir).values())
