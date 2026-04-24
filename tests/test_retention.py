"""Tests for envoy.retention module."""
from __future__ import annotations

import pytest

from envoy.retention import (
    RetentionError,
    get_retention,
    list_retention,
    remove_retention,
    set_retention,
)
from envoy.storage import get_store_dir, store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(store_dir, project="alpha", password="pw"):
    store_env(store_dir, project, "KEY=val", password)


def test_set_retention_persists(isolated_store):
    _seed(isolated_store)
    result = set_retention(isolated_store, "alpha", max_versions=5, max_snapshots=3)
    assert result["max_versions"] == 5
    assert result["max_snapshots"] == 3


def test_get_retention_missing_returns_none(isolated_store):
    _seed(isolated_store)
    assert get_retention(isolated_store, "alpha") is None


def test_get_retention_after_set(isolated_store):
    _seed(isolated_store)
    set_retention(isolated_store, "alpha", max_versions=7, max_snapshots=2)
    policy = get_retention(isolated_store, "alpha")
    assert policy == {"max_versions": 7, "max_snapshots": 2}


def test_set_retention_missing_project_raises(isolated_store):
    with pytest.raises(RetentionError, match="not found"):
        set_retention(isolated_store, "ghost", max_versions=5, max_snapshots=3)


def test_set_retention_invalid_max_versions_raises(isolated_store):
    _seed(isolated_store)
    with pytest.raises(RetentionError, match="max_versions"):
        set_retention(isolated_store, "alpha", max_versions=0, max_snapshots=3)


def test_set_retention_invalid_max_snapshots_raises(isolated_store):
    _seed(isolated_store)
    with pytest.raises(RetentionError, match="max_snapshots"):
        set_retention(isolated_store, "alpha", max_versions=5, max_snapshots=0)


def test_remove_retention_success(isolated_store):
    _seed(isolated_store)
    set_retention(isolated_store, "alpha", max_versions=5, max_snapshots=3)
    remove_retention(isolated_store, "alpha")
    assert get_retention(isolated_store, "alpha") is None


def test_remove_retention_missing_raises(isolated_store):
    _seed(isolated_store)
    with pytest.raises(RetentionError, match="No retention policy"):
        remove_retention(isolated_store, "alpha")


def test_list_retention_empty(isolated_store):
    assert list_retention(isolated_store) == {}


def test_list_retention_multiple(isolated_store):
    store_env(isolated_store, "alpha", "A=1", "pw")
    store_env(isolated_store, "beta", "B=2", "pw")
    set_retention(isolated_store, "alpha", max_versions=5, max_snapshots=3)
    set_retention(isolated_store, "beta", max_versions=10, max_snapshots=7)
    policies = list_retention(isolated_store)
    assert "alpha" in policies
    assert "beta" in policies
    assert policies["beta"]["max_versions"] == 10
