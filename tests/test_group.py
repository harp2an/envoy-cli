"""Tests for envoy.group and envoy.cmd_group."""

from __future__ import annotations

import pytest

from envoy.group import (
    GroupError,
    add_to_group,
    delete_group,
    find_by_group,
    list_groups,
    remove_from_group,
)
from envoy.storage import store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.group.get_store_dir", lambda: tmp_path)
    return tmp_path


def _seed(store_dir, project, password="pw"):
    store_env(project, "KEY=val", password, store_dir=store_dir)


def test_add_to_group_success(isolated_store):
    _seed(isolated_store, "alpha")
    add_to_group("team", "alpha", store_dir=isolated_store)
    assert "alpha" in find_by_group("team", store_dir=isolated_store)


def test_add_to_group_missing_project_raises(isolated_store):
    with pytest.raises(GroupError, match="does not exist"):
        add_to_group("team", "ghost", store_dir=isolated_store)


def test_add_to_group_duplicate_raises(isolated_store):
    _seed(isolated_store, "alpha")
    add_to_group("team", "alpha", store_dir=isolated_store)
    with pytest.raises(GroupError, match="already in group"):
        add_to_group("team", "alpha", store_dir=isolated_store)


def test_remove_from_group_success(isolated_store):
    _seed(isolated_store, "alpha")
    add_to_group("team", "alpha", store_dir=isolated_store)
    remove_from_group("team", "alpha", store_dir=isolated_store)
    assert list_groups(store_dir=isolated_store) == {}


def test_remove_nonexistent_raises(isolated_store):
    with pytest.raises(GroupError, match="not in group"):
        remove_from_group("team", "alpha", store_dir=isolated_store)


def test_list_groups_empty(isolated_store):
    assert list_groups(store_dir=isolated_store) == {}


def test_list_groups_multiple(isolated_store):
    _seed(isolated_store, "alpha")
    _seed(isolated_store, "beta")
    add_to_group("g1", "alpha", store_dir=isolated_store)
    add_to_group("g1", "beta", store_dir=isolated_store)
    add_to_group("g2", "alpha", store_dir=isolated_store)
    groups = list_groups(store_dir=isolated_store)
    assert set(groups["g1"]) == {"alpha", "beta"}
    assert groups["g2"] == ["alpha"]


def test_delete_group_success(isolated_store):
    _seed(isolated_store, "alpha")
    add_to_group("team", "alpha", store_dir=isolated_store)
    delete_group("team", store_dir=isolated_store)
    assert "team" not in list_groups(store_dir=isolated_store)


def test_delete_nonexistent_group_raises(isolated_store):
    with pytest.raises(GroupError, match="does not exist"):
        delete_group("ghost", store_dir=isolated_store)


def test_find_by_group_unknown_raises(isolated_store):
    with pytest.raises(GroupError, match="does not exist"):
        find_by_group("nope", store_dir=isolated_store)
