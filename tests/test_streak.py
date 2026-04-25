"""Tests for envoy.streak."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from envoy.storage import save_manifest
from envoy.streak import (
    StreakError,
    get_streak,
    list_streaks,
    record_activity,
    reset_streak,
)


@pytest.fixture()
def isolated_store(tmp_path):
    manifest = {"alpha": "alpha.enc", "beta": "beta.enc"}
    save_manifest(tmp_path, manifest)
    return tmp_path


def _today():
    return date.today().isoformat()


def _yesterday():
    return (date.today() - timedelta(days=1)).isoformat()


def _days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()


def test_record_activity_creates_entry(isolated_store):
    result = record_activity("alpha", store_dir=isolated_store)
    assert result["current"] == 1
    assert result["longest"] == 1
    assert result["last_date"] == _today()


def test_record_activity_same_day_idempotent(isolated_store):
    record_activity("alpha", store_dir=isolated_store)
    result = record_activity("alpha", store_dir=isolated_store)
    assert result["current"] == 1


def test_record_activity_consecutive_days_increments(isolated_store):
    # Seed yesterday's entry manually
    streaks = {"alpha": {"current": 3, "longest": 5, "last_date": _yesterday()}}
    (isolated_store / "streaks.json").write_text(json.dumps(streaks))

    result = record_activity("alpha", store_dir=isolated_store)
    assert result["current"] == 4
    assert result["longest"] == 5  # unchanged


def test_record_activity_consecutive_beats_longest(isolated_store):
    streaks = {"alpha": {"current": 5, "longest": 5, "last_date": _yesterday()}}
    (isolated_store / "streaks.json").write_text(json.dumps(streaks))

    result = record_activity("alpha", store_dir=isolated_store)
    assert result["current"] == 6
    assert result["longest"] == 6


def test_record_activity_gap_resets_streak(isolated_store):
    streaks = {"alpha": {"current": 7, "longest": 7, "last_date": _days_ago(3)}}
    (isolated_store / "streaks.json").write_text(json.dumps(streaks))

    result = record_activity("alpha", store_dir=isolated_store)
    assert result["current"] == 1
    assert result["longest"] == 7  # preserved


def test_record_activity_unknown_project_raises(isolated_store):
    with pytest.raises(StreakError, match="Unknown project"):
        record_activity("ghost", store_dir=isolated_store)


def test_get_streak_missing_returns_none(isolated_store):
    assert get_streak("alpha", store_dir=isolated_store) is None


def test_get_streak_after_record(isolated_store):
    record_activity("alpha", store_dir=isolated_store)
    data = get_streak("alpha", store_dir=isolated_store)
    assert data is not None
    assert data["current"] == 1


def test_reset_streak_removes_entry(isolated_store):
    record_activity("alpha", store_dir=isolated_store)
    reset_streak("alpha", store_dir=isolated_store)
    assert get_streak("alpha", store_dir=isolated_store) is None


def test_reset_streak_missing_raises(isolated_store):
    with pytest.raises(StreakError, match="No streak data"):
        reset_streak("alpha", store_dir=isolated_store)


def test_list_streaks_empty(isolated_store):
    assert list_streaks(store_dir=isolated_store) == {}


def test_list_streaks_multiple_projects(isolated_store):
    record_activity("alpha", store_dir=isolated_store)
    record_activity("beta", store_dir=isolated_store)
    data = list_streaks(store_dir=isolated_store)
    assert set(data.keys()) == {"alpha", "beta"}
