"""forecast.py – predict future env key usage based on historical trends."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir, load_manifest


class ForecastError(Exception):
    """Raised when a forecast operation fails."""


def _forecast_path(store_dir: Path) -> Path:
    return store_dir / "forecasts.json"


def _load_forecasts(store_dir: Path) -> dict[str, Any]:
    p = _forecast_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_forecasts(store_dir: Path, data: dict[str, Any]) -> None:
    _forecast_path(store_dir).write_text(json.dumps(data, indent=2))


def generate_forecast(
    project: str,
    signals: dict[str, float],
    *,
    store_dir: Path | None = None,
) -> dict[str, Any]:
    """Generate a key-usage forecast for *project* from *signals*.

    *signals* maps metric names (e.g. ``"push_count"``, ``"pull_count"``,
    ``"age_days"``) to numeric values.  Returns the stored forecast record.
    """
    if store_dir is None:
        store_dir = get_store_dir()

    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ForecastError(f"Unknown project: {project!r}")

    if not signals:
        raise ForecastError("signals must not be empty")

    allowed = {"push_count", "pull_count", "age_days", "key_count", "access_count"}
    unknown = set(signals) - allowed
    if unknown:
        raise ForecastError(f"Unknown signal(s): {', '.join(sorted(unknown))}")

    # Simple weighted score: higher push/pull activity → higher predicted usage
    weights = {
        "push_count": 0.35,
        "pull_count": 0.30,
        "access_count": 0.20,
        "key_count": 0.10,
        "age_days": 0.05,
    }
    score = sum(signals.get(k, 0.0) * w for k, w in weights.items())
    score = round(min(max(score, 0.0), 100.0), 4)

    record: dict[str, Any] = {
        "project": project,
        "signals": signals,
        "predicted_usage_score": score,
        "recommendation": _recommend(score),
    }

    data = _load_forecasts(store_dir)
    data[project] = record
    _save_forecasts(store_dir, data)
    return record


def get_forecast(project: str, *, store_dir: Path | None = None) -> dict[str, Any] | None:
    """Return the latest forecast for *project*, or ``None`` if absent."""
    if store_dir is None:
        store_dir = get_store_dir()
    return _load_forecasts(store_dir).get(project)


def list_forecasts(*, store_dir: Path | None = None) -> list[dict[str, Any]]:
    """Return all stored forecasts."""
    if store_dir is None:
        store_dir = get_store_dir()
    return list(_load_forecasts(store_dir).values())


def remove_forecast(project: str, *, store_dir: Path | None = None) -> None:
    """Delete the forecast for *project*."""
    if store_dir is None:
        store_dir = get_store_dir()
    data = _load_forecasts(store_dir)
    if project not in data:
        raise ForecastError(f"No forecast found for project: {project!r}")
    del data[project]
    _save_forecasts(store_dir, data)


def _recommend(score: float) -> str:
    if score >= 70:
        return "high-usage – consider caching or replication"
    if score >= 40:
        return "moderate-usage – monitor periodically"
    return "low-usage – no immediate action needed"
