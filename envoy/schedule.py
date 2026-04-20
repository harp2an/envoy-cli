"""Schedule automatic push/pull syncs for projects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir, load_manifest


class ScheduleError(Exception):
    pass


VALID_INTERVALS = {"hourly", "daily", "weekly"}


def _schedule_path(store_dir: Path) -> Path:
    return store_dir / "schedules.json"


def _load_schedules(store_dir: Path) -> dict[str, Any]:
    path = _schedule_path(store_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_schedules(store_dir: Path, data: dict[str, Any]) -> None:
    path = _schedule_path(store_dir)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_schedule(project: str, interval: str, direction: str = "push", store_dir: Path | None = None) -> dict[str, Any]:
    """Set a sync schedule for a project."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ScheduleError(f"Project '{project}' not found")
    if interval not in VALID_INTERVALS:
        raise ScheduleError(f"Invalid interval '{interval}'; choose from {sorted(VALID_INTERVALS)}")
    if direction not in ("push", "pull"):
        raise ScheduleError(f"Invalid direction '{direction}'; choose 'push' or 'pull'")
    schedules = _load_schedules(store_dir)
    entry = {"interval": interval, "direction": direction}
    schedules[project] = entry
    _save_schedules(store_dir, schedules)
    return entry


def get_schedule(project: str, store_dir: Path | None = None) -> dict[str, Any] | None:
    """Return schedule for a project, or None if not set."""
    store_dir = store_dir or get_store_dir()
    return _load_schedules(store_dir).get(project)


def remove_schedule(project: str, store_dir: Path | None = None) -> None:
    """Remove the schedule for a project."""
    store_dir = store_dir or get_store_dir()
    schedules = _load_schedules(store_dir)
    if project not in schedules:
        raise ScheduleError(f"No schedule found for project '{project}'")
    del schedules[project]
    _save_schedules(store_dir, schedules)


def list_schedules(store_dir: Path | None = None) -> dict[str, Any]:
    """Return all scheduled projects."""
    store_dir = store_dir or get_store_dir()
    return _load_schedules(store_dir)
