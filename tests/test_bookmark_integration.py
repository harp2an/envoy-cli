"""Integration tests for bookmark with real storage."""

import pytest
from envoy.storage import save_manifest
from envoy.bookmark import (
    BookmarkError,
    add_bookmark,
    remove_bookmark,
    get_bookmark,
    list_bookmarks,
)


@pytest.fixture()
def isolated_store(tmp_path):
    save_manifest(tmp_path, {"web": "web.env", "worker": "worker.env"})
    return tmp_path


def test_add_and_retrieve_bookmark(isolated_store):
    add_bookmark(isolated_store, "db", "web", "DATABASE_URL")
    entry = get_bookmark(isolated_store, "db")
    assert entry["project"] == "web"
    assert entry["key"] == "DATABASE_URL"


def test_multiple_bookmarks_independent(isolated_store):
    add_bookmark(isolated_store, "b1", "web", "KEY1")
    add_bookmark(isolated_store, "b2", "worker", "KEY2")
    assert get_bookmark(isolated_store, "b1")["project"] == "web"
    assert get_bookmark(isolated_store, "b2")["project"] == "worker"


def test_remove_bookmark_persists(isolated_store):
    add_bookmark(isolated_store, "temp", "web", "TMP")
    remove_bookmark(isolated_store, "temp")
    assert get_bookmark(isolated_store, "temp") is None
    entries = list_bookmarks(isolated_store)
    assert all(e["name"] != "temp" for e in entries)


def test_overwrite_bookmark(isolated_store):
    add_bookmark(isolated_store, "ref", "web", "OLD_KEY")
    add_bookmark(isolated_store, "ref", "worker", "NEW_KEY")
    entry = get_bookmark(isolated_store, "ref")
    assert entry["key"] == "NEW_KEY"
    assert len(list_bookmarks(isolated_store)) == 1


def test_list_bookmarks_after_remove(isolated_store):
    add_bookmark(isolated_store, "a", "web", "KA")
    add_bookmark(isolated_store, "b", "worker", "KB")
    remove_bookmark(isolated_store, "a")
    entries = list_bookmarks(isolated_store)
    assert len(entries) == 1
    assert entries[0]["name"] == "b"
