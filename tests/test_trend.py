"""Tests for envoy.trend."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.storage import save_manifest
from envoy.trend import (
    record_trend,
    get_trend,
    summarise_trend,
    clear_trends,
    TrendError,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.trend.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    save_manifest(tmp_path, {"alpha": "alpha.enc", "beta": "beta.enc"})
    return tmp_path


def test_record_trend_returns_entry(isolated_store):
    entry = record_trend("alpha", "score", 42.0, isolated_store)
    assert entry["metric"] == "score"
    assert entry["value"] == 42.0
    assert "timestamp" in entry


def test_record_trend_persists(isolated_store):
    record_trend("alpha", "score", 10.0, isolated_store)
    points = get_trend("alpha", "score", isolated_store)
    assert len(points) == 1
    assert points[0]["value"] == 10.0


def test_record_multiple_points(isolated_store):
    for v in [1.0, 2.0, 3.0]:
        record_trend("alpha", "score", v, isolated_store)
    points = get_trend("alpha", "score", isolated_store)
    assert len(points) == 3


def test_record_trend_missing_project_raises(isolated_store):
    with pytest.raises(TrendError, match="not found"):
        record_trend("missing", "score", 1.0, isolated_store)


def test_record_trend_empty_metric_raises(isolated_store):
    with pytest.raises(TrendError, match="empty"):
        record_trend("alpha", "  ", 1.0, isolated_store)


def test_get_trend_empty_when_none(isolated_store):
    points = get_trend("alpha", "nonexistent", isolated_store)
    assert points == []


def test_get_trend_filters_by_metric(isolated_store):
    record_trend("alpha", "score", 5.0, isolated_store)
    record_trend("alpha", "latency", 99.0, isolated_store)
    assert len(get_trend("alpha", "score", isolated_store)) == 1
    assert len(get_trend("alpha", "latency", isolated_store)) == 1


def test_summarise_trend_direction_up(isolated_store):
    record_trend("alpha", "score", 1.0, isolated_store)
    record_trend("alpha", "score", 5.0, isolated_store)
    s = summarise_trend("alpha", "score", isolated_store)
    assert s["direction"] == "up"
    assert s["min"] == 1.0
    assert s["max"] == 5.0
    assert s["avg"] == 3.0


def test_summarise_trend_direction_down(isolated_store):
    record_trend("beta", "score", 10.0, isolated_store)
    record_trend("beta", "score", 2.0, isolated_store)
    s = summarise_trend("beta", "score", isolated_store)
    assert s["direction"] == "down"


def test_summarise_trend_no_data_raises(isolated_store):
    with pytest.raises(TrendError, match="No data"):
        summarise_trend("alpha", "ghost", isolated_store)


def test_clear_trends_removes_entries(isolated_store):
    record_trend("alpha", "score", 1.0, isolated_store)
    record_trend("alpha", "score", 2.0, isolated_store)
    removed = clear_trends("alpha", isolated_store)
    assert removed == 2
    assert get_trend("alpha", "score", isolated_store) == []


def test_clear_trends_empty_returns_zero(isolated_store):
    assert clear_trends("alpha", isolated_store) == 0
