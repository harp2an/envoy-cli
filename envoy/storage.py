"""Local and remote storage management for .env files."""

import os
import json
from pathlib import Path
from typing import Optional

DEFAULT_STORE_DIR = Path.home() / ".envoy"
MANIFEST_FILE = "manifest.json"


def get_store_dir() -> Path:
    """Return the envoy store directory, creating it if needed."""
    store = Path(os.environ.get("ENVOY_STORE_DIR", DEFAULT_STORE_DIR))
    store.mkdir(parents=True, exist_ok=True)
    return store


def load_manifest() -> dict:
    """Load the manifest tracking stored env files."""
    manifest_path = get_store_dir() / MANIFEST_FILE
    if not manifest_path.exists():
        return {}
    with open(manifest_path, "r") as f:
        return json.load(f)


def save_manifest(manifest: dict) -> None:
    """Persist the manifest to disk."""
    manifest_path = get_store_dir() / MANIFEST_FILE
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def store_env(project: str, encrypted_data: str) -> Path:
    """Store encrypted env data for a project."""
    store = get_store_dir()
    env_file = store / f"{project}.env.enc"
    env_file.write_text(encrypted_data)

    manifest = load_manifest()
    manifest[project] = {
        "file": str(env_file),
        "updated_at": _now_iso(),
    }
    save_manifest(manifest)
    return env_file


def load_env(project: str) -> Optional[str]:
    """Load encrypted env data for a project, or None if not found."""
    manifest = load_manifest()
    if project not in manifest:
        return None
    env_file = Path(manifest[project]["file"])
    if not env_file.exists():
        return None
    return env_file.read_text()


def list_projects() -> list[str]:
    """Return a list of all stored project names."""
    return list(load_manifest().keys())


def delete_env(project: str) -> bool:
    """Delete stored env for a project. Returns True if deleted."""
    manifest = load_manifest()
    if project not in manifest:
        return False
    env_file = Path(manifest[project]["file"])
    if env_file.exists():
        env_file.unlink()
    del manifest[project]
    save_manifest(manifest)
    return True


def get_project_info(project: str) -> Optional[dict]:
    """Return metadata for a stored project, or None if not found.

    The returned dict contains:
      - ``file``: absolute path to the encrypted env file
      - ``updated_at``: ISO-8601 timestamp of the last update
    """
    manifest = load_manifest()
    return manifest.get(project)


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
