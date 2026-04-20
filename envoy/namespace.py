"""Namespace support: group projects under logical namespaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir, load_manifest


class NamespaceError(Exception):
    pass


def _namespace_path(store_dir: Optional[Path] = None) -> Path:
    return (store_dir or get_store_dir()) / "namespaces.json"


def _load_namespaces(store_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    path = _namespace_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_namespaces(data: Dict[str, List[str]], store_dir: Optional[Path] = None) -> None:
    path = _namespace_path(store_dir)
    path.write_text(json.dumps(data, indent=2))


def add_to_namespace(namespace: str, project: str, store_dir: Optional[Path] = None) -> None:
    """Add a project to a namespace, creating the namespace if needed."""
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise NamespaceError(f"Project '{project}' does not exist")
    data = _load_namespaces(store_dir)
    members = data.setdefault(namespace, [])
    if project in members:
        raise NamespaceError(f"Project '{project}' is already in namespace '{namespace}'")
    members.append(project)
    _save_namespaces(data, store_dir)


def remove_from_namespace(namespace: str, project: str, store_dir: Optional[Path] = None) -> None:
    """Remove a project from a namespace."""
    data = _load_namespaces(store_dir)
    if namespace not in data or project not in data[namespace]:
        raise NamespaceError(f"Project '{project}' is not in namespace '{namespace}'")
    data[namespace].remove(project)
    if not data[namespace]:
        del data[namespace]
    _save_namespaces(data, store_dir)


def list_namespaces(store_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    """Return all namespaces and their member projects."""
    return _load_namespaces(store_dir)


def get_namespace_projects(namespace: str, store_dir: Optional[Path] = None) -> List[str]:
    """Return projects belonging to a namespace."""
    data = _load_namespaces(store_dir)
    if namespace not in data:
        raise NamespaceError(f"Namespace '{namespace}' does not exist")
    return list(data[namespace])


def delete_namespace(namespace: str, store_dir: Optional[Path] = None) -> None:
    """Delete an entire namespace (does not delete projects)."""
    data = _load_namespaces(store_dir)
    if namespace not in data:
        raise NamespaceError(f"Namespace '{namespace}' does not exist")
    del data[namespace]
    _save_namespaces(data, store_dir)
