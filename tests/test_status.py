"""Tests for envoy.status."""
from __future__ import annotations

import json
import pytest

from envoy.storage import store_env, get_store_dir
from envoy.status import get_status, ProjectStatus, StatusError


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: str(tmp_path))
    monkeypatch.setattr("envoy.status.get_store_dir", lambda: str(tmp_path))
    return str(tmp_path)


def _seed(store_dir: str, project: str = "alpha", password: str = "pw") -> None:
    store_env(project, "KEY=val", password, store_dir)


def test_get_status_missing_project(isolated_store):
    status = get_status("ghost", isolated_store)
    assert status.project == "ghost"
    assert status.exists is False
    assert status.locked is False
    assert status.pinned_version is None
    assert status.tags == []


def test_get_status_existing_project(isolated_store):
    _seed(isolated_store)
    status = get_status("alpha", isolated_store)
    assert status.exists is True
    assert status.project == "alpha"


def test_get_status_not_locked_by_default(isolated_store):
    _seed(isolated_store)
    status = get_status("alpha", isolated_store)
    assert status.locked is False


def test_get_status_locked(isolated_store):
    from envoy.lock import acquire_lock
    _seed(isolated_store)
    acquire_lock("alpha", "tester", isolated_store)
    status = get_status("alpha", isolated_store)
    assert status.locked is True


def test_get_status_no_tags_by_default(isolated_store):
    _seed(isolated_store)
    status = get_status("alpha", isolated_store)
    assert status.tags == []


def test_get_status_with_tag(isolated_store):
    from envoy.tag import add_tag
    from envoy.storage import load_manifest, save_manifest
    _seed(isolated_store)
    manifest = load_manifest(isolated_store)
    manifest = add_tag(manifest, "alpha", "production")
    save_manifest(isolated_store, manifest)
    status = get_status("alpha", isolated_store)
    assert "production" in status.tags


def test_get_status_as_dict(isolated_store):
    _seed(isolated_store)
    status = get_status("alpha", isolated_store)
    d = status.as_dict()
    assert d["project"] == "alpha"
    assert "exists" in d
    assert "locked" in d
    assert "pinned_version" in d
    assert "tags" in d
    assert "ttl_expiry" in d
    assert "ttl_expired" in d


def test_get_status_ttl_expired(isolated_store):
    from envoy.ttl import set_ttl
    import time
    _seed(isolated_store)
    set_ttl("alpha", 1, isolated_store)
    time.sleep(1.1)
    status = get_status("alpha", isolated_store)
    assert status.ttl_expired is True
    assert status.ttl_expiry is not None
