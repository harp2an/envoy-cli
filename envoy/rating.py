"""Project rating/scoring module for envoy-cli."""

import json
from pathlib import Path
from envoy.storage import get_store_dir, load_manifest


class RatingError(Exception):
    pass


VALID_SCORES = {1, 2, 3, 4, 5}


def _rating_path(store_dir: Path) -> Path:
    return store_dir / "ratings.json"


def _load_ratings(store_dir: Path) -> dict:
    p = _rating_path(store_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_ratings(store_dir: Path, data: dict) -> None:
    with open(_rating_path(store_dir), "w") as f:
        json.dump(data, f, indent=2)


def set_rating(project: str, score: int, note: str = "") -> dict:
    """Set a numeric rating (1-5) for a project."""
    if score not in VALID_SCORES:
        raise RatingError(f"Score must be one of {sorted(VALID_SCORES)}, got {score}")
    store_dir = get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise RatingError(f"Project '{project}' not found")
    ratings = _load_ratings(store_dir)
    entry = {"score": score, "note": note}
    ratings[project] = entry
    _save_ratings(store_dir, ratings)
    return entry


def get_rating(project: str) -> dict | None:
    """Return the rating entry for a project, or None if not rated."""
    store_dir = get_store_dir()
    ratings = _load_ratings(store_dir)
    return ratings.get(project)


def remove_rating(project: str) -> None:
    """Remove a rating from a project."""
    store_dir = get_store_dir()
    ratings = _load_ratings(store_dir)
    if project not in ratings:
        raise RatingError(f"No rating found for project '{project}'")
    del ratings[project]
    _save_ratings(store_dir, ratings)


def list_ratings() -> dict:
    """Return all project ratings."""
    store_dir = get_store_dir()
    return _load_ratings(store_dir)
