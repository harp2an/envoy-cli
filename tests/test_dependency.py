"""Tests for envoy.dependency."""
from __future__ import annotations

import pytest

from envoy.dependency import (
    DependencyError,
    add_dependency,
    list_dependencies,
    list_dependents,
    remove_dependency,
)
from envoy.storage import save_manifest, get_store_dir


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.dependency.get_store_dir", lambda: tmp_path)
    manifest = {"alpha": {"file": "alpha.enc"}, "beta": {"file": "beta.enc"}, "gamma": {"file": "gamma.enc"}}
    save_manifest(tmp_path, manifest)
    return tmp_path


def test_add_dependency_success(isolated_store):
    add_dependency("alpha", "beta", store_dir=isolated_store)
    deps = list_dependencies("alpha", store_dir=isolated_store)
    assert "beta" in deps


def test_add_dependency_missing_project_raises(isolated_store):
    with pytest.raises(DependencyError, match="not found"):
        add_dependency("alpha", "nonexistent", store_dir=isolated_store)


def test_add_dependency_self_raises(isolated_store):
    with pytest.raises(DependencyError, match="itself"):
        add_dependency("alpha", "alpha", store_dir=isolated_store)


def test_add_dependency_duplicate_raises(isolated_store):
    add_dependency("alpha", "beta", store_dir=isolated_store)
    with pytest.raises(DependencyError, match="already depends"):
        add_dependency("alpha", "beta", store_dir=isolated_store)


def test_remove_dependency_success(isolated_store):
    add_dependency("alpha", "beta", store_dir=isolated_store)
    remove_dependency("alpha", "beta", store_dir=isolated_store)
    assert list_dependencies("alpha", store_dir=isolated_store) == []


def test_remove_dependency_missing_raises(isolated_store):
    with pytest.raises(DependencyError, match="does not depend"):
        remove_dependency("alpha", "beta", store_dir=isolated_store)


def test_list_dependencies_empty(isolated_store):
    assert list_dependencies("alpha", store_dir=isolated_store) == []


def test_list_dependencies_multiple(isolated_store):
    add_dependency("alpha", "beta", store_dir=isolated_store)
    add_dependency("alpha", "gamma", store_dir=isolated_store)
    deps = list_dependencies("alpha", store_dir=isolated_store)
    assert set(deps) == {"beta", "gamma"}


def test_list_dependents(isolated_store):
    add_dependency("alpha", "beta", store_dir=isolated_store)
    add_dependency("gamma", "beta", store_dir=isolated_store)
    dependents = list_dependents("beta", store_dir=isolated_store)
    assert set(dependents) == {"alpha", "gamma"}


def test_list_dependents_empty(isolated_store):
    assert list_dependents("alpha", store_dir=isolated_store) == []
