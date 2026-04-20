"""Integration tests: alias resolution against real storage + store_env."""

from __future__ import annotations

import pytest

from envoy.alias import add_alias, resolve_alias, update_alias, remove_alias
from envoy.storage import store_env, load_env, load_manifest


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def test_alias_resolves_to_stored_project(isolated_store):
    store_env("production-backend", "SECRET=abc\nDB=postgres", "pass", store_dir=isolated_store)
    add_alias("prod", "production-backend", store_dir=isolated_store)

    project = resolve_alias("prod", store_dir=isolated_store)
    assert project == "production-backend"

    content = load_env(project, "pass", store_dir=isolated_store)
    assert "SECRET=abc" in content


def test_alias_update_points_to_new_project(isolated_store):
    store_env("project-v1", "VER=1", "pw", store_dir=isolated_store)
    store_env("project-v2", "VER=2", "pw", store_dir=isolated_store)

    add_alias("current", "project-v1", store_dir=isolated_store)
    assert resolve_alias("current", store_dir=isolated_store) == "project-v1"

    update_alias("current", "project-v2", store_dir=isolated_store)
    assert resolve_alias("current", store_dir=isolated_store) == "project-v2"


def test_alias_does_not_affect_manifest(isolated_store):
    store_env("myproject", "K=V", "pw", store_dir=isolated_store)
    add_alias("mp", "myproject", store_dir=isolated_store)

    manifest = load_manifest(store_dir=isolated_store)
    # aliases.json should not pollute the project manifest
    assert "mp" not in manifest
    assert "myproject" in manifest


def test_remove_alias_does_not_delete_project(isolated_store):
    store_env("safe-project", "KEY=VALUE", "pw", store_dir=isolated_store)
    add_alias("temp", "safe-project", store_dir=isolated_store)
    remove_alias("temp", store_dir=isolated_store)

    assert resolve_alias("temp", store_dir=isolated_store) is None
    # Project data must still be intact
    content = load_env("safe-project", "pw", store_dir=isolated_store)
    assert "KEY=VALUE" in content
