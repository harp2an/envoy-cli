"""Access control: per-project read/write permissions for named users/roles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir

ACCESS_FILE = "access.json"
VALID_PERMS = {"read", "write", "admin"}


class AccessError(Exception):
    pass


def _access_path(store_dir: Optional[Path] = None) -> Path:
    return (store_dir or get_store_dir()) / ACCESS_FILE


def _load_access(store_dir: Optional[Path] = None) -> Dict[str, Dict[str, List[str]]]:
    path = _access_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_access(data: Dict[str, Dict[str, List[str]]], store_dir: Optional[Path] = None) -> None:
    path = _access_path(store_dir)
    path.write_text(json.dumps(data, indent=2))


def grant_access(project: str, identity: str, permission: str, store_dir: Optional[Path] = None) -> None:
    """Grant *identity* the given *permission* on *project*."""
    if permission not in VALID_PERMS:
        raise AccessError(f"Invalid permission '{permission}'. Choose from: {sorted(VALID_PERMS)}")
    data = _load_access(store_dir)
    project_acl = data.setdefault(project, {})
    perms = project_acl.setdefault(identity, [])
    if permission not in perms:
        perms.append(permission)
    _save_access(data, store_dir)


def revoke_access(project: str, identity: str, permission: str, store_dir: Optional[Path] = None) -> None:
    """Revoke *permission* from *identity* on *project*."""
    data = _load_access(store_dir)
    try:
        perms = data[project][identity]
    except KeyError:
        raise AccessError(f"No access entry for '{identity}' on project '{project}'")
    if permission not in perms:
        raise AccessError(f"'{identity}' does not have '{permission}' on '{project}'")
    perms.remove(permission)
    if not perms:
        del data[project][identity]
    if not data[project]:
        del data[project]
    _save_access(data, store_dir)


def list_access(project: str, store_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    """Return the ACL for *project* (identity -> list of permissions)."""
    data = _load_access(store_dir)
    return dict(data.get(project, {}))


def check_access(project: str, identity: str, permission: str, store_dir: Optional[Path] = None) -> bool:
    """Return True if *identity* holds *permission* on *project*."""
    acl = list_access(project, store_dir)
    return permission in acl.get(identity, [])
