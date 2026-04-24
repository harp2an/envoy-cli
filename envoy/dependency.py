"""Manage inter-project dependencies for envoy."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir, load_manifest


class DependencyError(Exception):
    pass


def _dep_path(store_dir: Path) -> Path:
    return store_dir / "dependencies.json"


def _load_deps(store_dir: Path) -> Dict[str, List[str]]:
    path = _dep_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_deps(store_dir: Path, data: Dict[str, List[str]]) -> None:
    _dep_path(store_dir).write_text(json.dumps(data, indent=2))


def add_dependency(project: str, depends_on: str, store_dir: Optional[Path] = None) -> None:
    """Record that *project* depends on *depends_on*."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    for name in (project, depends_on):
        if name not in manifest:
            raise DependencyError(f"Project '{name}' not found in manifest.")
    if project == depends_on:
        raise DependencyError("A project cannot depend on itself.")
    data = _load_deps(store_dir)
    deps = data.setdefault(project, [])
    if depends_on in deps:
        raise DependencyError(f"'{project}' already depends on '{depends_on}'.")
    deps.append(depends_on)
    _save_deps(store_dir, data)


def remove_dependency(project: str, depends_on: str, store_dir: Optional[Path] = None) -> None:
    store_dir = store_dir or get_store_dir()
    data = _load_deps(store_dir)
    deps = data.get(project, [])
    if depends_on not in deps:
        raise DependencyError(f"'{project}' does not depend on '{depends_on}'.")
    deps.remove(depends_on)
    if not deps:
        data.pop(project, None)
    _save_deps(store_dir, data)


def list_dependencies(project: str, store_dir: Optional[Path] = None) -> List[str]:
    store_dir = store_dir or get_store_dir()
    data = _load_deps(store_dir)
    return list(data.get(project, []))


def list_dependents(project: str, store_dir: Optional[Path] = None) -> List[str]:
    """Return projects that depend on *project*."""
    store_dir = store_dir or get_store_dir()
    data = _load_deps(store_dir)
    return [proj for proj, deps in data.items() if project in deps]
