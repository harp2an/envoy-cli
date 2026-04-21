"""Profile management: named sets of configuration overrides per project."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir, load_manifest


class ProfileError(Exception):
    pass


def _profile_path(store_dir: Path) -> Path:
    return store_dir / "profiles.json"


def _load_profiles(store_dir: Path) -> Dict[str, Dict[str, str]]:
    path = _profile_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_profiles(store_dir: Path, data: Dict[str, Dict[str, str]]) -> None:
    _profile_path(store_dir).write_text(json.dumps(data, indent=2))


def set_profile(project: str, profile: str, overrides: Dict[str, str],
               store_dir: Optional[Path] = None) -> None:
    """Create or replace a named profile for *project*."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ProfileError(f"Project '{project}' not found")
    if not profile:
        raise ProfileError("Profile name must not be empty")
    data = _load_profiles(store_dir)
    key = f"{project}:{profile}"
    data[key] = overrides
    _save_profiles(store_dir, data)


def get_profile(project: str, profile: str,
               store_dir: Optional[Path] = None) -> Optional[Dict[str, str]]:
    """Return overrides for *profile* of *project*, or None if absent."""
    store_dir = store_dir or get_store_dir()
    data = _load_profiles(store_dir)
    return data.get(f"{project}:{profile}")


def remove_profile(project: str, profile: str,
                  store_dir: Optional[Path] = None) -> None:
    """Delete a named profile; raises ProfileError if it does not exist."""
    store_dir = store_dir or get_store_dir()
    data = _load_profiles(store_dir)
    key = f"{project}:{profile}"
    if key not in data:
        raise ProfileError(f"Profile '{profile}' not found for project '{project}'")
    del data[key]
    _save_profiles(store_dir, data)


def list_profiles(project: str,
                 store_dir: Optional[Path] = None) -> List[str]:
    """Return all profile names registered for *project*."""
    store_dir = store_dir or get_store_dir()
    data = _load_profiles(store_dir)
    prefix = f"{project}:"
    return [k[len(prefix):] for k in data if k.startswith(prefix)]
