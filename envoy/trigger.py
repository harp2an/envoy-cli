"""Trigger rules: fire actions when specific env keys change."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir


class TriggerError(Exception):
    pass


def _trigger_path(store_dir: Path) -> Path:
    return store_dir / "triggers.json"


def _load_triggers(store_dir: Path) -> dict[str, list[dict]]:
    path = _trigger_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_triggers(store_dir: Path, data: dict[str, list[dict]]) -> None:
    _trigger_path(store_dir).write_text(json.dumps(data, indent=2))


_VALID_ACTIONS = {"log", "webhook", "export"}
_VALID_EVENTS = {"set", "delete", "rotate"}


def add_trigger(
    project: str,
    key_pattern: str,
    event: str,
    action: str,
    action_target: str,
    store_dir: Path | None = None,
) -> dict[str, Any]:
    """Register a trigger for *project* that fires *action* when *event* matches *key_pattern*."""
    if store_dir is None:
        store_dir = get_store_dir()
    if event not in _VALID_EVENTS:
        raise TriggerError(f"Unknown event '{event}'. Valid: {sorted(_VALID_EVENTS)}")
    if action not in _VALID_ACTIONS:
        raise TriggerError(f"Unknown action '{action}'. Valid: {sorted(_VALID_ACTIONS)}")
    data = _load_triggers(store_dir)
    triggers = data.setdefault(project, [])
    rule: dict[str, Any] = {
        "key_pattern": key_pattern,
        "event": event,
        "action": action,
        "action_target": action_target,
    }
    triggers.append(rule)
    _save_triggers(store_dir, data)
    return rule


def remove_trigger(
    project: str,
    index: int,
    store_dir: Path | None = None,
) -> None:
    """Remove trigger at *index* for *project*."""
    if store_dir is None:
        store_dir = get_store_dir()
    data = _load_triggers(store_dir)
    triggers = data.get(project, [])
    if index < 0 or index >= len(triggers):
        raise TriggerError(f"No trigger at index {index} for project '{project}'")
    triggers.pop(index)
    data[project] = triggers
    _save_triggers(store_dir, data)


def list_triggers(
    project: str,
    store_dir: Path | None = None,
) -> list[dict]:
    """Return all triggers for *project*."""
    if store_dir is None:
        store_dir = get_store_dir()
    return _load_triggers(store_dir).get(project, [])


def fire_triggers(
    project: str,
    key: str,
    event: str,
    store_dir: Path | None = None,
) -> list[dict]:
    """Return triggers that match *key* and *event* for *project* (for inspection/dispatch)."""
    import fnmatch
    if store_dir is None:
        store_dir = get_store_dir()
    matched = []
    for rule in list_triggers(project, store_dir):
        if rule["event"] == event and fnmatch.fnmatch(key, rule["key_pattern"]):
            matched.append(rule)
    return matched
