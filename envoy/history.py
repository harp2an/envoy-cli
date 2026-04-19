"""Track per-project env change history (last N versions)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

from envoy.storage import get_store_dir

MAX_HISTORY = 10
HISTORY_FILE = "history.json"


class HistoryError(Exception):
    pass


def _history_path(project: str) -> Path:
    return get_store_dir() / project / HISTORY_FILE


def _load_raw(project: str) -> List[Dict[str, Any]]:
    p = _history_path(project)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_raw(project: str, entries: List[Dict[str, Any]]) -> None:
    p = _history_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(entries, indent=2))


def record_version(project: str, ciphertext: str, label: str = "") -> None:
    """Append a ciphertext snapshot to the project history."""
    from envoy.audit import record_event
    entries = _load_raw(project)
    entries.append({"ciphertext": ciphertext, "label": label})
    entries = entries[-MAX_HISTORY:]
    _save_raw(project, entries)
    record_event("history_record", project=project, label=label)


def list_versions(project: str) -> List[Dict[str, Any]]:
    """Return history entries (oldest first) for a project."""
    return _load_raw(project)


def get_version(project: str, index: int) -> str:
    """Return ciphertext at history index (0 = oldest)."""
    entries = _load_raw(project)
    if not entries:
        raise HistoryError(f"No history for project '{project}'")
    try:
        return entries[index]["ciphertext"]
    except IndexError:
        raise HistoryError(f"History index {index} out of range for '{project}'")


def clear_history(project: str) -> None:
    p = _history_path(project)
    if p.exists():
        p.unlink()
