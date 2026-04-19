"""Tests for envoy.clone module."""

import pytest
from unittest.mock import patch
from envoy.clone import CloneError, clone_project, clone_with_rename


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def test_clone_project_success(isolated_store):
    from envoy.storage import store_env, load_env
    store_env("alpha", "KEY=val", "pass")
    clone_project("alpha", "beta", "pass")
    result = load_env("beta", "pass")
    assert result == "KEY=val"


def test_clone_project_missing_src_raises(isolated_store):
    with pytest.raises(CloneError, match="not found"):
        clone_project("missing", "dst", "pass")


def test_clone_project_dst_exists_raises(isolated_store):
    from envoy.storage import store_env
    store_env("alpha", "KEY=val", "pass")
    store_env("beta", "OTHER=1", "pass")
    with pytest.raises(CloneError, match="already exists"):
        clone_project("alpha", "beta", "pass")


def test_clone_project_new_password(isolated_store):
    from envoy.storage import store_env, load_env
    store_env("alpha", "X=1", "oldpass")
    clone_project("alpha", "beta", "oldpass", new_password="newpass")
    result = load_env("beta", "newpass")
    assert result == "X=1"


def test_clone_with_rename_prefix(isolated_store):
    from envoy.storage import store_env, load_env
    store_env("alpha", "FOO=bar", "pass")
    clone_with_rename("alpha", "beta", "pass", prefix="APP_")
    result = load_env("beta", "pass")
    assert "APP_FOO=bar" in result


def test_clone_records_audit(isolated_store):
    from envoy.storage import store_env
    from envoy.audit import load_events
    store_env("alpha", "K=v", "pass")
    clone_project("alpha", "beta", "pass")
    events = load_events()
    assert any(e["action"] == "clone" for e in events)
