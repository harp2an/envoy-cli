"""Tests for envoy.deprecate module."""
import pytest
from pathlib import Path

from envoy.storage import store_env, load_manifest
from envoy.deprecate import (
    DeprecationError,
    mark_deprecated,
    unmark_deprecated,
    list_deprecated,
    find_deprecated_across_projects,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    store_env("alpha", "KEY=val", "pw", store_dir=tmp_path)
    store_env("beta", "FOO=bar", "pw", store_dir=tmp_path)
    return tmp_path


def test_mark_deprecated_success(isolated_store):
    mark_deprecated("alpha", "KEY", reason="use NEW_KEY instead", store_dir=isolated_store)
    deps = list_deprecated("alpha", store_dir=isolated_store)
    assert "KEY" in deps
    assert deps["KEY"] == "use NEW_KEY instead"


def test_mark_deprecated_no_reason(isolated_store):
    mark_deprecated("alpha", "KEY", store_dir=isolated_store)
    deps = list_deprecated("alpha", store_dir=isolated_store)
    assert deps["KEY"] == ""


def test_mark_deprecated_missing_project_raises(isolated_store):
    with pytest.raises(DeprecationError, match="not found"):
        mark_deprecated("ghost", "KEY", store_dir=isolated_store)


def test_unmark_deprecated_success(isolated_store):
    mark_deprecated("alpha", "KEY", store_dir=isolated_store)
    unmark_deprecated("alpha", "KEY", store_dir=isolated_store)
    deps = list_deprecated("alpha", store_dir=isolated_store)
    assert "KEY" not in deps


def test_unmark_deprecated_not_marked_raises(isolated_store):
    with pytest.raises(DeprecationError, match="not marked deprecated"):
        unmark_deprecated("alpha", "UNKNOWN", store_dir=isolated_store)


def test_list_deprecated_empty_when_none(isolated_store):
    result = list_deprecated("alpha", store_dir=isolated_store)
    assert result == {}


def test_multiple_keys_same_project(isolated_store):
    mark_deprecated("alpha", "KEY", reason="old", store_dir=isolated_store)
    mark_deprecated("alpha", "OTHER", reason="also old", store_dir=isolated_store)
    deps = list_deprecated("alpha", store_dir=isolated_store)
    assert len(deps) == 2
    assert "KEY" in deps
    assert "OTHER" in deps


def test_find_across_projects(isolated_store):
    mark_deprecated("alpha", "KEY", reason="r1", store_dir=isolated_store)
    mark_deprecated("beta", "FOO", reason="r2", store_dir=isolated_store)
    all_deps = find_deprecated_across_projects(store_dir=isolated_store)
    assert "alpha" in all_deps
    assert "beta" in all_deps
    assert all_deps["alpha"]["KEY"] == "r1"
    assert all_deps["beta"]["FOO"] == "r2"


def test_find_across_projects_empty(isolated_store):
    result = find_deprecated_across_projects(store_dir=isolated_store)
    assert result == {}


def test_unmark_cleans_up_empty_project(isolated_store):
    mark_deprecated("alpha", "KEY", store_dir=isolated_store)
    unmark_deprecated("alpha", "KEY", store_dir=isolated_store)
    all_deps = find_deprecated_across_projects(store_dir=isolated_store)
    assert "alpha" not in all_deps
