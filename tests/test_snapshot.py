"""Tests for envoy.snapshot module."""

import os
import pytest

from envoy.crypto import encrypt
from envoy.storage import store_env
from envoy.snapshot import SnapshotError, create_snapshot, delete_snapshot, list_snapshots, restore_snapshot


PASSWORD = "hunter2"
PROJECT = "myapp"
PLAINTEXT = "KEY=value\nFOO=bar"


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    store_env(PROJECT, ciphertext)
    return tmp_path


def test_create_snapshot_returns_tag(isolated_store):
    tag = create_snapshot(PROJECT, PASSWORD)
    assert isinstance(tag, str)
    assert len(tag) > 0


def test_create_snapshot_file_exists(isolated_store):
    tag = create_snapshot(PROJECT, PASSWORD, label="v1")
    snap_file = isolated_store / "snapshots" / PROJECT / "v1.enc"
    assert snap_file.exists()


def test_create_snapshot_duplicate_label_raises(isolated_store):
    create_snapshot(PROJECT, PASSWORD, label="v1")
    with pytest.raises(SnapshotError, match="already exists"):
        create_snapshot(PROJECT, PASSWORD, label="v1")


def test_list_snapshots_empty(isolated_store):
    assert list_snapshots(PROJECT) == []


def test_list_snapshots_returns_sorted(isolated_store):
    create_snapshot(PROJECT, PASSWORD, label="b")
    create_snapshot(PROJECT, PASSWORD, label="a")
    assert list_snapshots(PROJECT) == ["a", "b"]


def test_restore_snapshot_succeeds(isolated_store):
    tag = create_snapshot(PROJECT, PASSWORD, label="snap1")
    restore_snapshot(PROJECT, tag, PASSWORD)


def test_restore_snapshot_wrong_password_raises(isolated_store):
    tag = create_snapshot(PROJECT, PASSWORD, label="snap2")
    with pytest.raises(Exception):
        restore_snapshot(PROJECT, tag, "wrongpass")


def test_restore_missing_snapshot_raises(isolated_store):
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot(PROJECT, "ghost", PASSWORD)


def test_delete_snapshot(isolated_store):
    tag = create_snapshot(PROJECT, PASSWORD, label="del1")
    delete_snapshot(PROJECT, tag)
    assert "del1" not in list_snapshots(PROJECT)


def test_delete_missing_snapshot_raises(isolated_store):
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot(PROJECT, "nope")
