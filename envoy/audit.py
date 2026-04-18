"""Audit log for tracking env push/pull operations."""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

AUDIT_FILENAME = "audit.log"


def get_audit_path(store_dir: str) -> str:
    return os.path.join(store_dir, AUDIT_FILENAME)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_event(store_dir: str, action: str, project: str, remote: str = "", details: str = "") -> None:
    """Append a single audit event to the log."""
    entry: Dict[str, Any] = {
        "timestamp": _now_iso(),
        "action": action,
        "project": project,
        "remote": remote,
        "details": details,
    }
    path = get_audit_path(store_dir)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def load_events(store_dir: str) -> List[Dict[str, Any]]:
    """Return all audit events as a list of dicts."""
    path = get_audit_path(store_dir)
    if not os.path.exists(path):
        return []
    events = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_events(store_dir: str) -> None:
    """Remove the audit log file."""
    path = get_audit_path(store_dir)
    if os.path.exists(path):
        os.remove(path)
