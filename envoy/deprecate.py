"""Deprecation notices for env keys across projects."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir, load_manifest


class DeprecationError(Exception):
    pass


def _deprecation_path(store_dir: Optional[Path] = None) -> Path:
    return (store_dir or get_store_dir()) / "deprecations.json"


def _load_deprecations(store_dir: Optional[Path] = None) -> Dict[str, Dict[str, str]]:
    path = _deprecation_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_deprecations(data: Dict[str, Dict[str, str]], store_dir: Optional[Path] = None) -> None:
    path = _deprecation_path(store_dir)
    path.write_text(json.dumps(data, indent=2))


def mark_deprecated(
    project: str,
    key: str,
    reason: str = "",
    store_dir: Optional[Path] = None,
) -> None:
    """Mark a key in a project as deprecated with an optional reason."""
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise DeprecationError(f"Project '{project}' not found")
    data = _load_deprecations(store_dir)
    data.setdefault(project, {})[key] = reason
    _save_deprecations(data, store_dir)


def unmark_deprecated(
    project: str,
    key: str,
    store_dir: Optional[Path] = None,
) -> None:
    """Remove the deprecation notice for a key in a project."""
    data = _load_deprecations(store_dir)
    if project not in data or key not in data[project]:
        raise DeprecationError(f"Key '{key}' in project '{project}' is not marked deprecated")
    del data[project][key]
    if not data[project]:
        del data[project]
    _save_deprecations(data, store_dir)


def list_deprecated(
    project: str,
    store_dir: Optional[Path] = None,
) -> Dict[str, str]:
    """Return mapping of deprecated key -> reason for a project."""
    data = _load_deprecations(store_dir)
    return dict(data.get(project, {}))


def find_deprecated_across_projects(
    store_dir: Optional[Path] = None,
) -> Dict[str, Dict[str, str]]:
    """Return all deprecations across every project."""
    return dict(_load_deprecations(store_dir))
