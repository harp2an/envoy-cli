"""Checkpoint support: save and restore named recovery points for a project."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from envoy.storage import get_store_dir, load_env, store_env


class CheckpointError(Exception):
    pass


def _checkpoint_dir(store_dir: Optional[Path] = None) -> Path:
    base = store_dir or get_store_dir()
    d = base / "checkpoints"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _checkpoint_index(project: str, store_dir: Optional[Path] = None) -> Path:
    return _checkpoint_dir(store_dir) / f"{project}.json"


def _load_index(project: str, store_dir: Optional[Path] = None) -> dict:
    path = _checkpoint_index(project, store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_index(project: str, data: dict, store_dir: Optional[Path] = None) -> None:
    _checkpoint_index(project, store_dir).write_text(json.dumps(data, indent=2))


def create_checkpoint(
    project: str,
    name: str,
    password: str,
    store_dir: Optional[Path] = None,
) -> str:
    """Save the current encrypted env as a named checkpoint. Returns ISO timestamp."""
    index = _load_index(project, store_dir)
    if name in index:
        raise CheckpointError(f"Checkpoint '{name}' already exists for project '{project}'")
    ciphertext = load_env(project, store_dir=store_dir)
    ts = datetime.now(timezone.utc).isoformat()
    index[name] = {"ts": ts, "data": ciphertext}
    _save_index(project, index, store_dir)
    return ts


def restore_checkpoint(
    project: str,
    name: str,
    password: str,
    store_dir: Optional[Path] = None,
) -> None:
    """Restore a named checkpoint, overwriting the current env."""
    index = _load_index(project, store_dir)
    if name not in index:
        raise CheckpointError(f"Checkpoint '{name}' not found for project '{project}'")
    ciphertext = index[name]["data"]
    store_env(project, ciphertext, store_dir=store_dir)


def list_checkpoints(project: str, store_dir: Optional[Path] = None) -> list[dict]:
    """Return list of checkpoint metadata dicts sorted by timestamp."""
    index = _load_index(project, store_dir)
    return sorted(
        [{"name": n, "ts": v["ts"]} for n, v in index.items()],
        key=lambda x: x["ts"],
    )


def delete_checkpoint(
    project: str,
    name: str,
    store_dir: Optional[Path] = None,
) -> None:
    """Delete a named checkpoint."""
    index = _load_index(project, store_dir)
    if name not in index:
        raise CheckpointError(f"Checkpoint '{name}' not found for project '{project}'")
    del index[name]
    _save_index(project, index, store_dir)
