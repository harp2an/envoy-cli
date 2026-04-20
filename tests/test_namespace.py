"""Tests for envoy.namespace and envoy.cmd_namespace."""

from __future__ import annotations

import pytest
from unittest.mock import patch

from envoy.namespace import (
    NamespaceError,
    add_to_namespace,
    delete_namespace,
    get_namespace_projects,
    list_namespaces,
    remove_from_namespace,
)
from envoy.storage import store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    with patch("envoy.namespace.get_store_dir", return_value=tmp_path), \
         patch("envoy.namespace.load_manifest", side_effect=lambda sd=None: _manifest(tmp_path)):
        yield tmp_path


def _manifest(store_dir):
    from envoy.storage import load_manifest
    return load_manifest(store_dir)


def _seed(store_dir, project="alpha"):
    store_env(project, "KEY=val", "pw", store_dir=store_dir)


def test_add_to_namespace_success(isolated_store):
    _seed(isolated_store)
    add_to_namespace("team-a", "alpha", store_dir=isolated_store)
    data = list_namespaces(store_dir=isolated_store)
    assert "team-a" in data
    assert "alpha" in data["team-a"]


def test_add_to_namespace_missing_project_raises(isolated_store):
    with pytest.raises(NamespaceError, match="does not exist"):
        add_to_namespace("team-a", "ghost", store_dir=isolated_store)


def test_add_duplicate_raises(isolated_store):
    _seed(isolated_store)
    add_to_namespace("team-a", "alpha", store_dir=isolated_store)
    with pytest.raises(NamespaceError, match="already in namespace"):
        add_to_namespace("team-a", "alpha", store_dir=isolated_store)


def test_remove_from_namespace_success(isolated_store):
    _seed(isolated_store)
    add_to_namespace("team-a", "alpha", store_dir=isolated_store)
    remove_from_namespace("team-a", "alpha", store_dir=isolated_store)
    data = list_namespaces(store_dir=isolated_store)
    assert "team-a" not in data


def test_remove_nonexistent_raises(isolated_store):
    with pytest.raises(NamespaceError):
        remove_from_namespace("team-a", "alpha", store_dir=isolated_store)


def test_get_namespace_projects(isolated_store):
    _seed(isolated_store, "proj1")
    _seed(isolated_store, "proj2")
    add_to_namespace("ns1", "proj1", store_dir=isolated_store)
    add_to_namespace("ns1", "proj2", store_dir=isolated_store)
    projects = get_namespace_projects("ns1", store_dir=isolated_store)
    assert set(projects) == {"proj1", "proj2"}


def test_get_namespace_missing_raises(isolated_store):
    with pytest.raises(NamespaceError, match="does not exist"):
        get_namespace_projects("nope", store_dir=isolated_store)


def test_delete_namespace(isolated_store):
    _seed(isolated_store)
    add_to_namespace("temp", "alpha", store_dir=isolated_store)
    delete_namespace("temp", store_dir=isolated_store)
    assert "temp" not in list_namespaces(store_dir=isolated_store)


def test_delete_nonexistent_namespace_raises(isolated_store):
    with pytest.raises(NamespaceError, match="does not exist"):
        delete_namespace("nope", store_dir=isolated_store)


def test_list_namespaces_empty(isolated_store):
    assert list_namespaces(store_dir=isolated_store) == {}
