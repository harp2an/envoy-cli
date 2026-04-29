"""Insight module: generate a summary report for a project's metadata signals."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir, load_manifest


class InsightError(Exception):
    pass


def _insight_path(store_dir: Path) -> Path:
    return store_dir / "insights.json"


def _load_insights(store_dir: Path) -> dict:
    p = _insight_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_insights(store_dir: Path, data: dict) -> None:
    _insight_path(store_dir).write_text(json.dumps(data, indent=2))


def generate_insight(project: str, signals: dict[str, Any], store_dir: Path | None = None) -> dict:
    """Compute an insight record from arbitrary signal dict and persist it."""
    if store_dir is None:
        store_dir = get_store_dir()

    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise InsightError(f"Project '{project}' not found in manifest.")

    if not signals:
        raise InsightError("Signals dict must not be empty.")

    score = _score_signals(signals)
    record: dict[str, Any] = {
        "project": project,
        "signals": signals,
        "score": score,
        "summary": _build_summary(signals, score),
    }

    insights = _load_insights(store_dir)
    insights[project] = record
    _save_insights(store_dir, insights)
    return record


def get_insight(project: str, store_dir: Path | None = None) -> dict | None:
    if store_dir is None:
        store_dir = get_store_dir()
    return _load_insights(store_dir).get(project)


def list_insights(store_dir: Path | None = None) -> list[dict]:
    if store_dir is None:
        store_dir = get_store_dir()
    return list(_load_insights(store_dir).values())


def remove_insight(project: str, store_dir: Path | None = None) -> None:
    if store_dir is None:
        store_dir = get_store_dir()
    insights = _load_insights(store_dir)
    if project not in insights:
        raise InsightError(f"No insight found for project '{project}'.")
    del insights[project]
    _save_insights(store_dir, insights)


def _score_signals(signals: dict[str, Any]) -> int:
    """Simple heuristic: +10 per truthy signal value, capped at 100."""
    return min(sum(10 for v in signals.values() if v), 100)


def _build_summary(signals: dict[str, Any], score: int) -> str:
    active = [k for k, v in signals.items() if v]
    inactive = [k for k, v in signals.items() if not v]
    parts = [f"Score: {score}/100."]
    if active:
        parts.append("Active: " + ", ".join(active) + ".")
    if inactive:
        parts.append("Missing: " + ", ".join(inactive) + ".")
    return " ".join(parts)
