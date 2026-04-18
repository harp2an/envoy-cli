"""Integration tests for tag feature using real storage."""

import pytest
from pathlib import Path

from envoy.storage import store_env, get_store_dir, load_manifest
from envoy.tag import add_tag, remove_tag, list_tags, find_by_tag, TagError


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path / "store"))
    return tmp_path / "store"


def test_add_and_list_tag(isolated_store):
    store_env("proj", "KEY=val", "pass")
    add_tag("proj", "production")
    assert "production" in list_tags("proj")


def test_multiple_tags(isolated_store):
    store_env("proj", "KEY=val", "pass")
    add_tag("proj", "production")
    add_tag("proj", "eu-west")
    tags = list_tags("proj")
    assert set(tags) == {"production", "eu-west"}


def test_remove_tag_persists(isolated_store):
    store_env("proj", "KEY=val", "pass")
    add_tag("proj", "production")
    remove_tag("proj", "production")
    assert list_tags("proj") == []


def test_find_by_tag_across_projects(isolated_store):
    store_env("alpha", "A=1", "pass")
    store_env("beta", "B=2", "pass")
    store_env("gamma", "C=3", "pass")
    add_tag("alpha", "prod")
    add_tag("gamma", "prod")
    result = find_by_tag("prod")
    assert set(result) == {"alpha", "gamma"}


def test_tag_missing_project_raises(isolated_store):
    with pytest.raises(TagError):
        add_tag("nonexistent", "x")
