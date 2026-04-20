"""Group management for envoy: organize projects into named groups."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envoy.storage import get_store_dir, load_manifest


class GroupError(Exception):
    pass


def _group_path(store_dir: Path | None = None) -> Path:
    return (store_dir or get_store_dir()) / "groups.json"


def _load_groups(store_dir: Path | None = None) -> Dict[str, List[str]]:
    path = _group_path(store_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_groups(groups: Dict[str, List[str]], store_dir: Path | None = None) -> None:
    path = _group_path(store_dir)
    with path.open("w") as fh:
        json.dump(groups, fh, indent=2)


def add_to_group(group: str, project: str, store_dir: Path | None = None) -> None:
    """Add *project* to *group*, creating the group if needed."""
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise GroupError(f"Project '{project}' does not exist")
    groups = _load_groups(store_dir)
    members = groups.setdefault(group, [])
    if project in members:
        raise GroupError(f"Project '{project}' is already in group '{group}'")
    members.append(project)
    _save_groups(groups, store_dir)


def remove_from_group(group: str, project: str, store_dir: Path | None = None) -> None:
    """Remove *project* from *group*."""
    groups = _load_groups(store_dir)
    if group not in groups or project not in groups[group]:
        raise GroupError(f"Project '{project}' is not in group '{group}'")
    groups[group].remove(project)
    if not groups[group]:
        del groups[group]
    _save_groups(groups, store_dir)


def list_groups(store_dir: Path | None = None) -> Dict[str, List[str]]:
    """Return all groups and their members."""
    return _load_groups(store_dir)


def delete_group(group: str, store_dir: Path | None = None) -> None:
    """Delete an entire group."""
    groups = _load_groups(store_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist")
    del groups[group]
    _save_groups(groups, store_dir)


def find_by_group(group: str, store_dir: Path | None = None) -> List[str]:
    """Return the list of projects in *group*."""
    groups = _load_groups(store_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist")
    return list(groups[group])
