"""Trend analysis for project activity and scoring over time."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from envoy.storage import get_store_dir, load_manifest


class TrendError(Exception):
    pass


def _trend_path(store_dir: Path) -> Path:
    return store_dir / "trends.json"


def _load_trends(store_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    p = _trend_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_trends(store_dir: Path, data: Dict[str, List[Dict[str, Any]]]) -> None:
    _trend_path(store_dir).write_text(json.dumps(data, indent=2))


def record_trend(
    project: str,
    metric: str,
    value: float,
    store_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Record a metric data point for a project."""
    sd = store_dir or get_store_dir()
    manifest = load_manifest(sd)
    if project not in manifest:
        raise TrendError(f"Project '{project}' not found")
    if not metric.strip():
        raise TrendError("Metric name must not be empty")

    from envoy.audit import _now_iso
    entry = {"metric": metric, "value": value, "timestamp": _now_iso()}

    trends = _load_trends(sd)
    trends.setdefault(project, []).append(entry)
    _save_trends(sd, trends)
    return entry


def get_trend(
    project: str,
    metric: str,
    store_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Return all recorded data points for a metric in a project."""
    sd = store_dir or get_store_dir()
    trends = _load_trends(sd)
    return [
        e for e in trends.get(project, []) if e["metric"] == metric
    ]


def summarise_trend(
    project: str,
    metric: str,
    store_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Return min, max, average and direction for a metric."""
    points = get_trend(project, metric, store_dir)
    if not points:
        raise TrendError(f"No data for metric '{metric}' in project '{project}'")
    values = [p["value"] for p in points]
    avg = sum(values) / len(values)
    direction = "stable"
    if len(values) >= 2:
        direction = "up" if values[-1] > values[0] else ("down" if values[-1] < values[0] else "stable")
    return {
        "project": project,
        "metric": metric,
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "avg": round(avg, 4),
        "direction": direction,
    }


def clear_trends(
    project: str,
    store_dir: Optional[Path] = None,
) -> int:
    """Remove all trend data for a project. Returns number of entries removed."""
    sd = store_dir or get_store_dir()
    trends = _load_trends(sd)
    removed = len(trends.pop(project, []))
    _save_trends(sd, trends)
    return removed
