"""Reminder module: schedule human-readable reminders tied to projects."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir, load_manifest


class ReminderError(Exception):
    pass


def _reminder_path(store_dir: Path) -> Path:
    return store_dir / "reminders.json"


def _load_reminders(store_dir: Path) -> dict:
    p = _reminder_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_reminders(store_dir: Path, data: dict) -> None:
    _reminder_path(store_dir).write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def set_reminder(
    project: str,
    message: str,
    due_in_days: int,
    store_dir: Optional[Path] = None,
) -> str:
    """Create or overwrite a reminder for *project*. Returns the due-date ISO string."""
    if store_dir is None:
        store_dir = get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ReminderError(f"Project '{project}' not found.")
    if due_in_days <= 0:
        raise ReminderError("due_in_days must be a positive integer.")
    if not message.strip():
        raise ReminderError("Reminder message must not be empty.")
    due = (datetime.utcnow() + timedelta(days=due_in_days)).date().isoformat()
    data = _load_reminders(store_dir)
    data[project] = {"message": message.strip(), "due": due, "created": _now_iso()}
    _save_reminders(store_dir, data)
    return due


def get_reminder(project: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    if store_dir is None:
        store_dir = get_store_dir()
    return _load_reminders(store_dir).get(project)


def remove_reminder(project: str, store_dir: Optional[Path] = None) -> None:
    if store_dir is None:
        store_dir = get_store_dir()
    data = _load_reminders(store_dir)
    if project not in data:
        raise ReminderError(f"No reminder found for project '{project}'.")
    del data[project]
    _save_reminders(store_dir, data)


def list_reminders(store_dir: Optional[Path] = None) -> list:
    """Return all reminders sorted by due date ascending."""
    if store_dir is None:
        store_dir = get_store_dir()
    data = _load_reminders(store_dir)
    rows = [{"project": p, **v} for p, v in data.items()]
    return sorted(rows, key=lambda r: r["due"])


def due_soon(days: int = 7, store_dir: Optional[Path] = None) -> list:
    """Return reminders due within *days* days from today."""
    if store_dir is None:
        store_dir = get_store_dir()
    cutoff = (datetime.utcnow() + timedelta(days=days)).date().isoformat()
    today = datetime.utcnow().date().isoformat()
    return [
        r for r in list_reminders(store_dir)
        if today <= r["due"] <= cutoff
    ]
