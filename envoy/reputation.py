"""Reputation scoring for projects based on aggregate activity signals."""

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir, load_manifest


class ReputationError(Exception):
    pass


def _reputation_path(store_dir: Path) -> Path:
    return store_dir / "reputation.json"


def _load_reputations(store_dir: Path) -> dict:
    path = _reputation_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_reputations(store_dir: Path, data: dict) -> None:
    _reputation_path(store_dir).write_text(json.dumps(data, indent=2))


def _compute_score(signals: dict) -> int:
    """Compute a reputation score (0-100) from weighted signals."""
    weights = {
        "has_rating": 15,
        "has_annotation": 10,
        "has_metadata": 10,
        "has_tags": 10,
        "has_history": 20,
        "has_audit": 15,
        "has_snapshot": 20,
    }
    score = sum(weights[k] for k, v in signals.items() if v and k in weights)
    return min(score, 100)


def compute_reputation(
    project: str,
    store_dir: Optional[Path] = None,
    signals: Optional[dict] = None,
) -> dict:
    """Compute and persist a reputation record for *project*."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ReputationError(f"Project '{project}' not found.")

    if signals is None:
        signals = {}

    score = _compute_score(signals)
    record = {"project": project, "score": score, "signals": signals}

    data = _load_reputations(store_dir)
    data[project] = record
    _save_reputations(store_dir, data)
    return record


def get_reputation(project: str, store_dir: Optional[Path] = None) -> Optional[dict]:
    """Return the stored reputation record for *project*, or None."""
    store_dir = store_dir or get_store_dir()
    return _load_reputations(store_dir).get(project)


def list_reputations(store_dir: Optional[Path] = None) -> list:
    """Return all reputation records sorted by score descending."""
    store_dir = store_dir or get_store_dir()
    data = _load_reputations(store_dir)
    return sorted(data.values(), key=lambda r: r["score"], reverse=True)


def remove_reputation(project: str, store_dir: Optional[Path] = None) -> None:
    """Delete the reputation record for *project*."""
    store_dir = store_dir or get_store_dir()
    data = _load_reputations(store_dir)
    if project not in data:
        raise ReputationError(f"No reputation record for '{project}'.")
    del data[project]
    _save_reputations(store_dir, data)
