"""Tests for envoy.label."""

import pytest
from pathlib import Path

from envoy.label import (
    LabelError,
    set_label,
    remove_label,
    get_labels,
    find_by_label,
)
from envoy.storage import get_store_dir, store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return get_store_dir()


def _seed(store_dir: Path, project: str) -> None:
    store_env(store_dir, project, "KEY=val", password="pw")


# ---------------------------------------------------------------------------
# set_label
# ---------------------------------------------------------------------------

def test_set_label_persists(isolated_store):
    _seed(isolated_store, "alpha")
    set_label(isolated_store, "alpha", "env", "production")
    labels = get_labels(isolated_store, "alpha")
    assert labels["env"] == "production"


def test_set_label_overwrites_existing(isolated_store):
    _seed(isolated_store, "alpha")
    set_label(isolated_store, "alpha", "env", "staging")
    set_label(isolated_store, "alpha", "env", "production")
    assert get_labels(isolated_store, "alpha")["env"] == "production"


def test_set_label_missing_project_raises(isolated_store):
    with pytest.raises(LabelError, match="not found"):
        set_label(isolated_store, "ghost", "env", "prod")


def test_set_label_empty_key_raises(isolated_store):
    _seed(isolated_store, "alpha")
    with pytest.raises(LabelError, match="empty"):
        set_label(isolated_store, "alpha", "", "val")


# ---------------------------------------------------------------------------
# get_labels
# ---------------------------------------------------------------------------

def test_get_labels_returns_empty_for_unlabelled(isolated_store):
    _seed(isolated_store, "beta")
    assert get_labels(isolated_store, "beta") == {}


def test_get_labels_multiple_keys(isolated_store):
    _seed(isolated_store, "beta")
    set_label(isolated_store, "beta", "team", "backend")
    set_label(isolated_store, "beta", "env", "staging")
    labels = get_labels(isolated_store, "beta")
    assert labels == {"team": "backend", "env": "staging"}


# ---------------------------------------------------------------------------
# remove_label
# ---------------------------------------------------------------------------

def test_remove_label_success(isolated_store):
    _seed(isolated_store, "gamma")
    set_label(isolated_store, "gamma", "env", "dev")
    remove_label(isolated_store, "gamma", "env")
    assert "env" not in get_labels(isolated_store, "gamma")


def test_remove_label_missing_raises(isolated_store):
    _seed(isolated_store, "gamma")
    with pytest.raises(LabelError, match="not found"):
        remove_label(isolated_store, "gamma", "nonexistent")


# ---------------------------------------------------------------------------
# find_by_label
# ---------------------------------------------------------------------------

def test_find_by_label_key_only(isolated_store):
    for p in ("p1", "p2", "p3"):
        _seed(isolated_store, p)
    set_label(isolated_store, "p1", "env", "prod")
    set_label(isolated_store, "p2", "env", "staging")
    result = find_by_label(isolated_store, "env")
    assert set(result) == {"p1", "p2"}


def test_find_by_label_key_and_value(isolated_store):
    for p in ("p1", "p2"):
        _seed(isolated_store, p)
    set_label(isolated_store, "p1", "env", "prod")
    set_label(isolated_store, "p2", "env", "staging")
    result = find_by_label(isolated_store, "env", "prod")
    assert result == ["p1"]


def test_find_by_label_no_match_returns_empty(isolated_store):
    _seed(isolated_store, "solo")
    assert find_by_label(isolated_store, "missing_key") == []
