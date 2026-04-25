"""Scorecard: compute a health/quality score for a project based on metadata."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir, load_manifest


class ScorecardError(Exception):
    pass


def _scorecard_path(store_dir: Path) -> Path:
    return store_dir / "scorecards.json"


def _load_scorecards(store_dir: Path) -> dict[str, Any]:
    p = _scorecard_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_scorecards(store_dir: Path, data: dict[str, Any]) -> None:
    _scorecard_path(store_dir).write_text(json.dumps(data, indent=2))


SCORE_WEIGHTS: dict[str, int] = {
    "has_env_file": 30,
    "has_description": 20,
    "has_tags": 15,
    "has_annotation": 15,
    "has_rating": 10,
    "has_retention": 10,
}


def compute_score(project: str, store_dir: Path | None = None) -> dict[str, Any]:
    """Compute and persist a scorecard for *project*."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ScorecardError(f"Project '{project}' not found.")

    entry = manifest[project]
    checks: dict[str, bool] = {
        "has_env_file": bool(entry.get("file")),
        "has_description": bool(entry.get("description")),
        "has_tags": bool(entry.get("tags")),
        "has_annotation": bool(entry.get("annotation")),
        "has_rating": bool(entry.get("rating")),
        "has_retention": bool(entry.get("retention")),
    }

    total = sum(SCORE_WEIGHTS[k] for k, v in checks.items() if v)
    result: dict[str, Any] = {"project": project, "score": total, "checks": checks}

    data = _load_scorecards(store_dir)
    data[project] = result
    _save_scorecards(store_dir, data)
    return result


def get_scorecard(project: str, store_dir: Path | None = None) -> dict[str, Any] | None:
    store_dir = store_dir or get_store_dir()
    return _load_scorecards(store_dir).get(project)


def list_scorecards(store_dir: Path | None = None) -> list[dict[str, Any]]:
    store_dir = store_dir or get_store_dir()
    return list(_load_scorecards(store_dir).values())


def remove_scorecard(project: str, store_dir: Path | None = None) -> None:
    store_dir = store_dir or get_store_dir()
    data = _load_scorecards(store_dir)
    if project not in data:
        raise ScorecardError(f"No scorecard for '{project}'.")
    del data[project]
    _save_scorecards(store_dir, data)
