"""Tests for envoy.metadata."""

import pytest
from pathlib import Path
from envoy.storage import store_env, get_store_dir
from envoy.metadata import (
    MetadataError,
    set_metadata,
    get_metadata,
    remove_metadata,
    list_metadata,
    clear_metadata,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.metadata.get_store_dir", lambda: tmp_path)
    store_env("alpha", "KEY=1", "pass", store_dir=tmp_path)
    store_env("beta", "KEY=2", "pass", store_dir=tmp_path)
    return tmp_path


def test_set_and_get_metadata(isolated_store):
    set_metadata("alpha", "owner", "alice", store_dir=isolated_store)
    assert get_metadata("alpha", "owner", store_dir=isolated_store) == "alice"


def test_get_metadata_missing_key_returns_none(isolated_store):
    assert get_metadata("alpha", "nonexistent", store_dir=isolated_store) is None


def test_set_metadata_missing_project_raises(isolated_store):
    with pytest.raises(MetadataError, match="not found"):
        set_metadata("ghost", "k", "v", store_dir=isolated_store)


def test_set_metadata_empty_key_raises(isolated_store):
    with pytest.raises(MetadataError, match="empty"):
        set_metadata("alpha", "", "v", store_dir=isolated_store)


def test_set_metadata_overwrites_existing(isolated_store):
    set_metadata("alpha", "env", "staging", store_dir=isolated_store)
    set_metadata("alpha", "env", "production", store_dir=isolated_store)
    assert get_metadata("alpha", "env", store_dir=isolated_store) == "production"


def test_remove_metadata_success(isolated_store):
    set_metadata("alpha", "tier", "free", store_dir=isolated_store)
    remove_metadata("alpha", "tier", store_dir=isolated_store)
    assert get_metadata("alpha", "tier", store_dir=isolated_store) is None


def test_remove_metadata_missing_key_raises(isolated_store):
    with pytest.raises(MetadataError, match="not found"):
        remove_metadata("alpha", "missing", store_dir=isolated_store)


def test_list_metadata_returns_all_keys(isolated_store):
    set_metadata("beta", "region", "us-east", store_dir=isolated_store)
    set_metadata("beta", "team", "platform", store_dir=isolated_store)
    result = list_metadata("beta", store_dir=isolated_store)
    assert result == {"region": "us-east", "team": "platform"}


def test_list_metadata_empty_project(isolated_store):
    assert list_metadata("alpha", store_dir=isolated_store) == {}


def test_metadata_isolated_per_project(isolated_store):
    set_metadata("alpha", "color", "red", store_dir=isolated_store)
    assert get_metadata("beta", "color", store_dir=isolated_store) is None


def test_clear_metadata_removes_all(isolated_store):
    set_metadata("alpha", "a", "1", store_dir=isolated_store)
    set_metadata("alpha", "b", "2", store_dir=isolated_store)
    clear_metadata("alpha", store_dir=isolated_store)
    assert list_metadata("alpha", store_dir=isolated_store) == {}


def test_clear_metadata_nonexistent_project_is_noop(isolated_store):
    # Should not raise even if the project has no metadata entry
    clear_metadata("alpha", store_dir=isolated_store)
