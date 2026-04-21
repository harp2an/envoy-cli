"""Unit tests for envoy.rollback."""

from __future__ import annotations

import pytest

from envoy.storage import store_env, load_env
from envoy.history import record_version, list_versions
from envoy.rollback import RollbackError, rollback_to_version, list_rollback_points


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return str(tmp_path)


PASSWORD = "s3cr3t"


def test_list_rollback_points_empty(isolated_store):
    points = list_rollback_points("alpha", store_dir=isolated_store)
    assert points == []


def test_rollback_no_history_raises(isolated_store):
    store_env("alpha", "KEY=1", PASSWORD, store_dir=isolated_store)
    with pytest.raises(RollbackError, match="No history"):
        rollback_to_version("alpha", 0, PASSWORD, store_dir=isolated_store)


def test_rollback_out_of_range_raises(isolated_store):
    store_env("alpha", "KEY=1", PASSWORD, store_dir=isolated_store)
    record_version("alpha", "KEY=1", PASSWORD, store_dir=isolated_store)
    with pytest.raises(RollbackError, match="out of range"):
        rollback_to_version("alpha", 5, PASSWORD, store_dir=isolated_store)


def test_rollback_restores_content(isolated_store):
    # Store v0 and record it in history.
    store_env("alpha", "KEY=original", PASSWORD, store_dir=isolated_store)
    record_version("alpha", "KEY=original", PASSWORD, store_dir=isolated_store)

    # Overwrite with new content (no history entry yet).
    store_env("alpha", "KEY=updated", PASSWORD, store_dir=isolated_store)

    # Rollback to index 0 should restore original.
    ts = rollback_to_version("alpha", 0, PASSWORD, store_dir=isolated_store)
    assert isinstance(ts, str) and len(ts) > 0

    restored = load_env("alpha", PASSWORD, store_dir=isolated_store)
    assert restored == "KEY=original"


def test_rollback_saves_current_as_new_history_entry(isolated_store):
    store_env("beta", "K=v1", PASSWORD, store_dir=isolated_store)
    record_version("beta", "K=v1", PASSWORD, store_dir=isolated_store)
    store_env("beta", "K=v2", PASSWORD, store_dir=isolated_store)

    before_count = len(list_versions("beta", store_dir=isolated_store))
    rollback_to_version("beta", 0, PASSWORD, store_dir=isolated_store)
    after_count = len(list_versions("beta", store_dir=isolated_store))

    # Current state (v2) should have been saved before rollback.
    assert after_count == before_count + 1


def test_list_rollback_points_returns_versions(isolated_store):
    store_env("gamma", "X=1", PASSWORD, store_dir=isolated_store)
    record_version("gamma", "X=1", PASSWORD, store_dir=isolated_store)
    record_version("gamma", "X=2", PASSWORD, store_dir=isolated_store)
    points = list_rollback_points("gamma", store_dir=isolated_store)
    assert len(points) == 2
