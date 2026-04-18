"""Snapshot support: save and restore point-in-time copies of a project's env."""

import json
import os
from datetime import datetime, timezone

from envoy.storage import get_store_dir, load_env, store_env


class SnapshotError(Exception):
    pass


def _snapshot_dir(project: str) -> str:
    d = os.path.join(get_store_dir(), "snapshots", project)
    os.makedirs(d, exist_ok=True)
    return d


def _now_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_snapshot(project: str, password: str, label: str | None = None) -> str:
    """Encrypt and save current env as a snapshot. Returns snapshot id."""
    ciphertext = load_env(project, password)
    tag = label or _now_tag()
    snap_path = os.path.join(_snapshot_dir(project), f"{tag}.enc")
    if os.path.exists(snap_path):
        raise SnapshotError(f"Snapshot '{tag}' already exists for project '{project}'")
    with open(snap_path, "w") as f:
        f.write(ciphertext)
    return tag


def list_snapshots(project: str) -> list[str]:
    """Return sorted list of snapshot ids for a project."""
    d = _snapshot_dir(project)
    names = [fn[:-4] for fn in os.listdir(d) if fn.endswith(".enc")]
    return sorted(names)


def restore_snapshot(project: str, tag: str, password: str) -> None:
    """Restore a snapshot by re-storing its ciphertext (password must match)."""
    snap_path = os.path.join(_snapshot_dir(project), f"{tag}.enc")
    if not os.path.exists(snap_path):
        raise SnapshotError(f"Snapshot '{tag}' not found for project '{project}'")
    with open(snap_path, "r") as f:
        ciphertext = f.read()
    # Validate password by decrypting
    from envoy.crypto import decrypt
    decrypt(ciphertext, password)  # raises on bad password
    store_env(project, ciphertext)


def delete_snapshot(project: str, tag: str) -> None:
    snap_path = os.path.join(_snapshot_dir(project), f"{tag}.enc")
    if not os.path.exists(snap_path):
        raise SnapshotError(f"Snapshot '{tag}' not found for project '{project}'")
    os.remove(snap_path)
