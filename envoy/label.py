"""Label management for envoy projects.

Labels are free-form key-value metadata attached to projects,
distinct from tags (which are plain strings) and metadata (which
is per-project arbitrary data).  Labels allow querying projects
by structured attributes such as env=production or team=backend.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir, load_manifest


class LabelError(Exception):
    """Raised when a label operation fails."""


def _label_path(store_dir: Path) -> Path:
    return store_dir / "labels.json"


def _load_labels(store_dir: Path) -> Dict[str, Dict[str, str]]:
    path = _label_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_labels(store_dir: Path, data: Dict[str, Dict[str, str]]) -> None:
    _label_path(store_dir).write_text(json.dumps(data, indent=2))


def set_label(store_dir: Path, project: str, key: str, value: str) -> None:
    """Set *key* = *value* on *project*.  Creates the label map if absent."""
    if not key:
        raise LabelError("Label key must not be empty")
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise LabelError(f"Project '{project}' not found")
    data = _load_labels(store_dir)
    data.setdefault(project, {})[key] = value
    _save_labels(store_dir, data)


def remove_label(store_dir: Path, project: str, key: str) -> None:
    """Remove *key* from *project*'s labels.  Raises if not present."""
    data = _load_labels(store_dir)
    if project not in data or key not in data[project]:
        raise LabelError(f"Label '{key}' not found on project '{project}'")
    del data[project][key]
    if not data[project]:
        del data[project]
    _save_labels(store_dir, data)


def get_labels(store_dir: Path, project: str) -> Dict[str, str]:
    """Return all labels for *project* (may be empty dict)."""
    return _load_labels(store_dir).get(project, {})


def find_by_label(store_dir: Path, key: str, value: Optional[str] = None) -> List[str]:
    """Return projects that have *key* set (optionally matching *value*)."""
    data = _load_labels(store_dir)
    results: List[str] = []
    for project, labels in data.items():
        if key in labels:
            if value is None or labels[key] == value:
                results.append(project)
    return sorted(results)
