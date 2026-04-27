"""User feedback/notes attached to projects."""

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir, load_manifest


class FeedbackError(Exception):
    pass


def _feedback_path(store_dir: Path) -> Path:
    return store_dir / "feedback.json"


def _load_feedback(store_dir: Path) -> dict:
    path = _feedback_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_feedback(store_dir: Path, data: dict) -> None:
    _feedback_path(store_dir).write_text(json.dumps(data, indent=2))


def add_feedback(project: str, note: str, store_dir: Optional[Path] = None) -> str:
    """Append a feedback note to a project. Returns the note."""
    if store_dir is None:
        store_dir = get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise FeedbackError(f"Project '{project}' not found.")
    if not note or not note.strip():
        raise FeedbackError("Feedback note must not be empty.")
    data = _load_feedback(store_dir)
    data.setdefault(project, [])
    data[project].append(note.strip())
    _save_feedback(store_dir, data)
    return note.strip()


def get_feedback(project: str, store_dir: Optional[Path] = None) -> list:
    """Return all feedback notes for a project."""
    if store_dir is None:
        store_dir = get_store_dir()
    data = _load_feedback(store_dir)
    return data.get(project, [])


def remove_feedback(project: str, index: int, store_dir: Optional[Path] = None) -> str:
    """Remove feedback note at given 0-based index. Returns removed note."""
    if store_dir is None:
        store_dir = get_store_dir()
    data = _load_feedback(store_dir)
    notes = data.get(project, [])
    if not notes:
        raise FeedbackError(f"No feedback found for project '{project}'.")
    if index < 0 or index >= len(notes):
        raise FeedbackError(f"Index {index} out of range (0-{len(notes) - 1}).")
    removed = notes.pop(index)
    data[project] = notes
    _save_feedback(store_dir, data)
    return removed


def clear_feedback(project: str, store_dir: Optional[Path] = None) -> int:
    """Clear all feedback for a project. Returns number of notes removed."""
    if store_dir is None:
        store_dir = get_store_dir()
    data = _load_feedback(store_dir)
    count = len(data.get(project, []))
    data[project] = []
    _save_feedback(store_dir, data)
    return count
