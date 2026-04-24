"""Tests for envoy.priority."""

import pytest

from envoy.priority import (
    DEFAULT_PRIORITY,
    PriorityError,
    get_priority,
    list_priorities,
    remove_priority,
    set_priority,
)
from envoy.storage import store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(store_dir, project: str) -> None:
    store_env(project, "KEY=val", "password", store_dir=store_dir)


# ---------------------------------------------------------------------------
# set_priority
# ---------------------------------------------------------------------------

def test_set_priority_persists(isolated_store):
    _seed(isolated_store, "alpha")
    level = set_priority("alpha", 10, store_dir=isolated_store)
    assert level == 10
    assert get_priority("alpha", store_dir=isolated_store) == 10


def test_set_priority_overwrites_existing(isolated_store):
    _seed(isolated_store, "alpha")
    set_priority("alpha", 5, store_dir=isolated_store)
    set_priority("alpha", 42, store_dir=isolated_store)
    assert get_priority("alpha", store_dir=isolated_store) == 42


def test_set_priority_missing_project_raises(isolated_store):
    with pytest.raises(PriorityError, match="not found"):
        set_priority("ghost", 1, store_dir=isolated_store)


def test_set_priority_too_high_raises(isolated_store):
    _seed(isolated_store, "alpha")
    with pytest.raises(PriorityError, match="between"):
        set_priority("alpha", 101, store_dir=isolated_store)


def test_set_priority_too_low_raises(isolated_store):
    _seed(isolated_store, "alpha")
    with pytest.raises(PriorityError, match="between"):
        set_priority("alpha", -101, store_dir=isolated_store)


def test_set_priority_boundary_values(isolated_store):
    _seed(isolated_store, "alpha")
    _seed(isolated_store, "beta")
    assert set_priority("alpha", 100, store_dir=isolated_store) == 100
    assert set_priority("beta", -100, store_dir=isolated_store) == -100


# ---------------------------------------------------------------------------
# get_priority
# ---------------------------------------------------------------------------

def test_get_priority_default_when_not_set(isolated_store):
    _seed(isolated_store, "alpha")
    assert get_priority("alpha", store_dir=isolated_store) == DEFAULT_PRIORITY


# ---------------------------------------------------------------------------
# remove_priority
# ---------------------------------------------------------------------------

def test_remove_priority_success(isolated_store):
    _seed(isolated_store, "alpha")
    set_priority("alpha", 7, store_dir=isolated_store)
    remove_priority("alpha", store_dir=isolated_store)
    assert get_priority("alpha", store_dir=isolated_store) == DEFAULT_PRIORITY


def test_remove_priority_not_set_raises(isolated_store):
    _seed(isolated_store, "alpha")
    with pytest.raises(PriorityError, match="No priority set"):
        remove_priority("alpha", store_dir=isolated_store)


# ---------------------------------------------------------------------------
# list_priorities
# ---------------------------------------------------------------------------

def test_list_priorities_empty(isolated_store):
    assert list_priorities(store_dir=isolated_store) == []


def test_list_priorities_sorted_descending(isolated_store):
    for name in ("alpha", "beta", "gamma"):
        _seed(isolated_store, name)
    set_priority("alpha", 5, store_dir=isolated_store)
    set_priority("beta", 20, store_dir=isolated_store)
    set_priority("gamma", -3, store_dir=isolated_store)
    result = list_priorities(store_dir=isolated_store)
    assert result == [("beta", 20), ("alpha", 5), ("gamma", -3)]
