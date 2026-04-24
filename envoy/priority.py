"""Priority management for envoy projects.

Allows assigning a numeric priority level to projects so they can be
ordered and filtered by importance.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from envoy.storage import get_store_dir, load_manifest


class PriorityError(Exception):
    pass


DEFAULT_PRIORITY = 0
MIN_PRIORITY = -100
MAX_PRIORITY = 100


def _priority_path(store_dir: Path) -> Path:
    return store_dir / "priorities.json"


def _load_priorities(store_dir: Path) -> Dict[str, int]:
    path = _priority_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_priorities(store_dir: Path, priorities: Dict[str, int]) -> None:
    _priority_path(store_dir).write_text(json.dumps(priorities, indent=2))


def set_priority(project: str, level: int, store_dir: Optional[Path] = None) -> int:
    """Assign a priority level to a project. Returns the set level."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise PriorityError(f"Project '{project}' not found in manifest.")
    if not (MIN_PRIORITY <= level <= MAX_PRIORITY):
        raise PriorityError(
            f"Priority must be between {MIN_PRIORITY} and {MAX_PRIORITY}, got {level}."
        )
    priorities = _load_priorities(store_dir)
    priorities[project] = level
    _save_priorities(store_dir, priorities)
    return level


def get_priority(project: str, store_dir: Optional[Path] = None) -> int:
    """Return the priority for a project, defaulting to DEFAULT_PRIORITY."""
    store_dir = store_dir or get_store_dir()
    priorities = _load_priorities(store_dir)
    return priorities.get(project, DEFAULT_PRIORITY)


def remove_priority(project: str, store_dir: Optional[Path] = None) -> None:
    """Remove explicit priority for a project (resets to default)."""
    store_dir = store_dir or get_store_dir()
    priorities = _load_priorities(store_dir)
    if project not in priorities:
        raise PriorityError(f"No priority set for project '{project}'.")
    del priorities[project]
    _save_priorities(store_dir, priorities)


def list_priorities(store_dir: Optional[Path] = None) -> List[Tuple[str, int]]:
    """Return all projects with explicit priorities, sorted highest first."""
    store_dir = store_dir or get_store_dir()
    priorities = _load_priorities(store_dir)
    return sorted(priorities.items(), key=lambda x: x[1], reverse=True)
