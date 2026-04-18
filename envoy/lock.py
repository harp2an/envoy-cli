"""Project locking to prevent concurrent modifications."""

import json
import os
import time
from pathlib import Path

from envoy.storage import get_store_dir

LOCK_TIMEOUT = 30  # seconds


class LockError(Exception):
    pass


def _lock_path(project: str) -> Path:
    return get_store_dir() / f"{project}.lock"


def acquire_lock(project: str, owner: str = "envoy") -> Path:
    path = _lock_path(project)
    if path.exists():
        data = json.loads(path.read_text())
        age = time.time() - data["acquired_at"]
        if age < LOCK_TIMEOUT:
            raise LockError(
                f"Project '{project}' is locked by '{data['owner']}' "
                f"({int(age)}s ago). Try again later."
            )
        # stale lock — remove it
        path.unlink()
    payload = {"owner": owner, "acquired_at": time.time()}
    path.write_text(json.dumps(payload))
    return path


def release_lock(project: str) -> None:
    path = _lock_path(project)
    if path.exists():
        path.unlink()


def is_locked(project: str) -> bool:
    path = _lock_path(project)
    if not path.exists():
        return False
    data = json.loads(path.read_text())
    age = time.time() - data["acquired_at"]
    return age < LOCK_TIMEOUT


class ProjectLock:
    """Context manager for project locking."""

    def __init__(self, project: str, owner: str = "envoy"):
        self.project = project
        self.owner = owner

    def __enter__(self):
        acquire_lock(self.project, self.owner)
        return self

    def __exit__(self, *_):
        release_lock(self.project)
