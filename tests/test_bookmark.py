"""Unit tests for envoy.bookmark."""

import pytest
from pathlib import Path
from envoy.bookmark import (
    BookmarkError,
    add_bookmark,
    remove_bookmark,
    get_bookmark,
    list_bookmarks,
)
from envoy.storage import save_manifest


@pytest.fixture()
def isolated_store(tmp_path):
    save_manifest(tmp_path, {"alpha": "alpha.env", "beta": "beta.env"})
    return tmp_path


def test_add_bookmark_success(isolated_store):
    add_bookmark(isolated_store, "mymark", "alpha", "DB_URL")
    entry = get_bookmark(isolated_store, "mymark")
    assert entry == {"project": "alpha", "key": "DB_URL"}


def test_add_bookmark_overwrites_existing(isolated_store):
    add_bookmark(isolated_store, "mymark", "alpha", "DB_URL")
    add_bookmark(isolated_store, "mymark", "beta", "API_KEY")
    entry = get_bookmark(isolated_store, "mymark")
    assert entry["project"] == "beta"
    assert entry["key"] == "API_KEY"


def test_add_bookmark_missing_project_raises(isolated_store):
    with pytest.raises(BookmarkError, match="not found"):
        add_bookmark(isolated_store, "mymark", "ghost", "KEY")


def test_add_bookmark_empty_name_raises(isolated_store):
    with pytest.raises(BookmarkError, match="empty"):
        add_bookmark(isolated_store, "", "alpha", "KEY")


def test_remove_bookmark_success(isolated_store):
    add_bookmark(isolated_store, "mymark", "alpha", "DB_URL")
    remove_bookmark(isolated_store, "mymark")
    assert get_bookmark(isolated_store, "mymark") is None


def test_remove_bookmark_missing_raises(isolated_store):
    with pytest.raises(BookmarkError, match="not found"):
        remove_bookmark(isolated_store, "nonexistent")


def test_get_bookmark_missing_returns_none(isolated_store):
    assert get_bookmark(isolated_store, "nope") is None


def test_list_bookmarks_empty(isolated_store):
    assert list_bookmarks(isolated_store) == []


def test_list_bookmarks_sorted(isolated_store):
    add_bookmark(isolated_store, "zzz", "alpha", "Z")
    add_bookmark(isolated_store, "aaa", "beta", "A")
    entries = list_bookmarks(isolated_store)
    assert [e["name"] for e in entries] == ["aaa", "zzz"]


def test_list_bookmarks_contains_all_fields(isolated_store):
    add_bookmark(isolated_store, "mark", "alpha", "SECRET")
    entries = list_bookmarks(isolated_store)
    assert entries[0] == {"name": "mark", "project": "alpha", "key": "SECRET"}
