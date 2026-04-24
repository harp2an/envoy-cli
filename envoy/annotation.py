"""Annotation support: attach freeform notes to projects."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from envoy.storage import get_store_dir, load_manifest


class AnnotationError(Exception):
    pass


def _annotation_path(store_dir: Path) -> Path:
    return store_dir / "annotations.json"


def _load_annotations(store_dir: Path) -> dict:
    path = _annotation_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_annotations(store_dir: Path, data: dict) -> None:
    _annotation_path(store_dir).write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def set_annotation(store_dir: Path, project: str, note: str) -> None:
    """Set or replace the annotation note for a project."""
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise AnnotationError(f"Project '{project}' not found.")
    if not note or not note.strip():
        raise AnnotationError("Annotation note must not be empty.")
    data = _load_annotations(store_dir)
    data[project] = {"note": note.strip(), "updated_at": _now_iso()}
    _save_annotations(store_dir, data)


def get_annotation(store_dir: Path, project: str) -> Optional[dict]:
    """Return the annotation dict for a project, or None if absent."""
    data = _load_annotations(store_dir)
    return data.get(project)


def remove_annotation(store_dir: Path, project: str) -> None:
    """Remove the annotation for a project."""
    data = _load_annotations(store_dir)
    if project not in data:
        raise AnnotationError(f"No annotation found for project '{project}'.")
    del data[project]
    _save_annotations(store_dir, data)


def list_annotations(store_dir: Path) -> dict:
    """Return all annotations keyed by project name."""
    return dict(_load_annotations(store_dir))
