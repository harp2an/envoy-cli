"""Tests for envoy.storage module."""

import pytest
from pathlib import Path
from unittest.mock import patch

import envoy.storage as storage


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    """Redirect all storage operations to a temporary directory."""
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def test_get_store_dir_creates_directory(tmp_path):
    store = storage.get_store_dir()
    assert store.exists()
    assert store.is_dir()


def test_load_manifest_empty_when_no_file():
    manifest = storage.load_manifest()
    assert manifest == {}


def test_store_env_creates_file():
    path = storage.store_env("my-project", "encrypted-blob")
    assert path.exists()
    assert path.read_text() == "encrypted-blob"


def test_store_env_updates_manifest():
    storage.store_env("my-project", "encrypted-blob")
    manifest = storage.load_manifest()
    assert "my-project" in manifest
    assert "updated_at" in manifest["my-project"]


def test_load_env_returns_data():
    storage.store_env("alpha", "secret-data")
    result = storage.load_env("alpha")
    assert result == "secret-data"


def test_load_env_returns_none_for_unknown_project():
    result = storage.load_env("nonexistent")
    assert result is None


def test_list_projects():
    storage.store_env("proj-a", "data-a")
    storage.store_env("proj-b", "data-b")
    projects = storage.list_projects()
    assert set(projects) == {"proj-a", "proj-b"}


def test_delete_env_removes_file_and_manifest_entry():
    storage.store_env("to-delete", "some-data")
    result = storage.delete_env("to-delete")
    assert result is True
    assert storage.load_env("to-delete") is None
    assert "to-delete" not in storage.list_projects()


def test_delete_env_returns_false_for_unknown_project():
    result = storage.delete_env("ghost")
    assert result is False


def test_store_env_overwrites_existing():
    storage.store_env("proj", "v1")
    storage.store_env("proj", "v2")
    assert storage.load_env("proj") == "v2"
    assert len(storage.list_projects()) == 1
