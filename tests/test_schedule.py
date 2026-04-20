"""Tests for envoy.schedule."""

from __future__ import annotations

import pytest

from envoy.schedule import (
    ScheduleError,
    get_schedule,
    list_schedules,
    remove_schedule,
    set_schedule,
)
from envoy.storage import save_manifest, get_store_dir


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    monkeypatch.setattr("envoy.storage._store_dir_override", None, raising=False)
    import envoy.storage as st
    monkeypatch.setattr(st, "get_store_dir", lambda: tmp_path)
    import envoy.schedule as sc
    monkeypatch.setattr(sc, "get_store_dir", lambda: tmp_path)
    monkeypatch.setattr(sc, "load_manifest", lambda d: {"alpha": {}, "beta": {}})
    return tmp_path


def test_set_schedule_persists(isolated_store):
    entry = set_schedule("alpha", "daily", store_dir=isolated_store)
    assert entry["interval"] == "daily"
    assert entry["direction"] == "push"
    schedules = list_schedules(store_dir=isolated_store)
    assert "alpha" in schedules
    assert schedules["alpha"]["interval"] == "daily"


def test_set_schedule_direction_pull(isolated_store):
    entry = set_schedule("beta", "hourly", direction="pull", store_dir=isolated_store)
    assert entry["direction"] == "pull"


def test_set_schedule_invalid_interval_raises(isolated_store):
    with pytest.raises(ScheduleError, match="Invalid interval"):
        set_schedule("alpha", "minutely", store_dir=isolated_store)


def test_set_schedule_invalid_direction_raises(isolated_store):
    with pytest.raises(ScheduleError, match="Invalid direction"):
        set_schedule("alpha", "daily", direction="sync", store_dir=isolated_store)


def test_set_schedule_missing_project_raises(isolated_store):
    with pytest.raises(ScheduleError, match="not found"):
        set_schedule("ghost", "weekly", store_dir=isolated_store)


def test_get_schedule_returns_none_when_not_set(isolated_store):
    result = get_schedule("alpha", store_dir=isolated_store)
    assert result is None


def test_get_schedule_returns_entry(isolated_store):
    set_schedule("alpha", "weekly", store_dir=isolated_store)
    result = get_schedule("alpha", store_dir=isolated_store)
    assert result is not None
    assert result["interval"] == "weekly"


def test_remove_schedule_success(isolated_store):
    set_schedule("alpha", "daily", store_dir=isolated_store)
    remove_schedule("alpha", store_dir=isolated_store)
    assert get_schedule("alpha", store_dir=isolated_store) is None


def test_remove_schedule_missing_raises(isolated_store):
    with pytest.raises(ScheduleError, match="No schedule found"):
        remove_schedule("alpha", store_dir=isolated_store)


def test_list_schedules_empty(isolated_store):
    assert list_schedules(store_dir=isolated_store) == {}


def test_list_schedules_multiple(isolated_store):
    set_schedule("alpha", "daily", store_dir=isolated_store)
    set_schedule("beta", "hourly", direction="pull", store_dir=isolated_store)
    schedules = list_schedules(store_dir=isolated_store)
    assert len(schedules) == 2
    assert schedules["beta"]["direction"] == "pull"
