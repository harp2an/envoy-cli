"""Rollback support: revert a project's env to a previous history version."""

from __future__ import annotations

from envoy.history import HistoryError, get_version, list_versions, record_version
from envoy.storage import load_env, store_env
from envoy.audit import record_event


class RollbackError(Exception):
    """Raised when a rollback operation fails."""


def rollback_to_version(
    project: str,
    version_index: int,
    password: str,
    store_dir: str | None = None,
) -> str:
    """Revert *project* to the env content stored at *version_index*.

    Returns the ISO timestamp of the version that was restored.

    Raises:
        RollbackError: if the version does not exist or decryption fails.
    """
    versions = list_versions(project, store_dir=store_dir)
    if not versions:
        raise RollbackError(f"No history found for project '{project}'.")
    if version_index < 0 or version_index >= len(versions):
        raise RollbackError(
            f"Version index {version_index} out of range "
            f"(0-{len(versions) - 1})."
        )
    try:
        content = get_version(project, version_index, password, store_dir=store_dir)
    except HistoryError as exc:
        raise RollbackError(str(exc)) from exc

    # Persist current state as a new history entry before overwriting.
    try:
        current = load_env(project, password, store_dir=store_dir)
        record_version(project, current, password, store_dir=store_dir)
    except Exception:
        pass  # best-effort backup of current state

    store_env(project, content, password, store_dir=store_dir)
    ts = versions[version_index]["timestamp"]
    record_event("rollback", project, {"version_index": version_index, "timestamp": ts},
                 store_dir=store_dir)
    return ts


def list_rollback_points(
    project: str,
    store_dir: str | None = None,
) -> list[dict]:
    """Return all available rollback points (same as history list)."""
    return list_versions(project, store_dir=store_dir)
