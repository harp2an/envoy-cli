"""Track consecutive-day usage streaks for projects."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir, load_manifest


class StreakError(Exception):
    pass


def _streak_path(store_dir: Path) -> Path:
    return store_dir / "streaks.json"


def _load_streaks(store_dir: Path) -> dict:
    p = _streak_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_streaks(store_dir: Path, data: dict) -> None:
    _streak_path(store_dir).write_text(json.dumps(data, indent=2))


def _today() -> str:
    return date.today().isoformat()


def record_activity(project: str, store_dir: Optional[Path] = None) -> dict:
    """Record activity for *project* today and update its streak."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise StreakError(f"Unknown project: {project}")

    streaks = _load_streaks(store_dir)
    today = _today()
    entry = streaks.get(project, {"current": 0, "longest": 0, "last_date": None})

    last = entry.get("last_date")
    if last == today:
        # Already recorded today — no change
        return dict(entry)

    if last is not None and (date.fromisoformat(today) - date.fromisoformat(last)) == timedelta(days=1):
        entry["current"] += 1
    else:
        entry["current"] = 1

    if entry["current"] > entry["longest"]:
        entry["longest"] = entry["current"]
    entry["last_date"] = today

    streaks[project] = entry
    _save_streaks(store_dir, streaks)
    return dict(entry)


def get_streak(project: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    """Return streak data for *project*, or None if no activity recorded."""
    store_dir = store_dir or get_store_dir()
    return _load_streaks(store_dir).get(project)


def reset_streak(project: str, store_dir: Optional[Path] = None) -> None:
    """Remove streak data for *project*."""
    store_dir = store_dir or get_store_dir()
    streaks = _load_streaks(store_dir)
    if project not in streaks:
        raise StreakError(f"No streak data for project: {project}")
    del streaks[project]
    _save_streaks(store_dir, streaks)


def list_streaks(store_dir: Optional[Path] = None) -> dict:
    """Return all streak data keyed by project name."""
    store_dir = store_dir or get_store_dir()
    return dict(_load_streaks(store_dir))
