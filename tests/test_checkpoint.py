"""Tests for envoy.checkpoint."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.storage import store_env, load_env
from envoy.crypto import encrypt, decrypt
from envoy.checkpoint import (
    CheckpointError,
    create_checkpoint,
    restore_checkpoint,
    list_checkpoints,
    delete_checkpoint,
)


PASSWORD = "s3cr3t"
PROJECT = "myapp"


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(project: str, content: str, password: str, store_dir: Path) -> None:
    ciphertext = encrypt(content, password)
    store_env(project, ciphertext, store_dir=store_dir)


def test_create_checkpoint_returns_timestamp(isolated_store):
    _seed(PROJECT, "KEY=val", PASSWORD, isolated_store)
    ts = create_checkpoint(PROJECT, "v1", PASSWORD, store_dir=isolated_store)
    assert "T" in ts  # ISO format


def test_create_checkpoint_persists(isolated_store):
    _seed(PROJECT, "KEY=val", PASSWORD, isolated_store)
    create_checkpoint(PROJECT, "v1", PASSWORD, store_dir=isolated_store)
    checkpoints = list_checkpoints(PROJECT, store_dir=isolated_store)
    assert len(checkpoints) == 1
    assert checkpoints[0]["name"] == "v1"


def test_create_checkpoint_duplicate_raises(isolated_store):
    _seed(PROJECT, "KEY=val", PASSWORD, isolated_store)
    create_checkpoint(PROJECT, "v1", PASSWORD, store_dir=isolated_store)
    with pytest.raises(CheckpointError, match="already exists"):
        create_checkpoint(PROJECT, "v1", PASSWORD, store_dir=isolated_store)


def test_restore_checkpoint_overwrites_current(isolated_store):
    original = "KEY=original"
    _seed(PROJECT, original, PASSWORD, isolated_store)
    create_checkpoint(PROJECT, "snap", PASSWORD, store_dir=isolated_store)

    # Overwrite with new content
    _seed(PROJECT, "KEY=changed", PASSWORD, isolated_store)
    changed = decrypt(load_env(PROJECT, store_dir=isolated_store), PASSWORD)
    assert changed == "KEY=changed"

    # Restore checkpoint
    restore_checkpoint(PROJECT, "snap", PASSWORD, store_dir=isolated_store)
    restored = decrypt(load_env(PROJECT, store_dir=isolated_store), PASSWORD)
    assert restored == original


def test_restore_unknown_checkpoint_raises(isolated_store):
    _seed(PROJECT, "KEY=val", PASSWORD, isolated_store)
    with pytest.raises(CheckpointError, match="not found"):
        restore_checkpoint(PROJECT, "ghost", PASSWORD, store_dir=isolated_store)


def test_list_checkpoints_empty(isolated_store):
    _seed(PROJECT, "KEY=val", PASSWORD, isolated_store)
    assert list_checkpoints(PROJECT, store_dir=isolated_store) == []


def test_list_checkpoints_sorted_by_timestamp(isolated_store):
    _seed(PROJECT, "A=1", PASSWORD, isolated_store)
    create_checkpoint(PROJECT, "first", PASSWORD, store_dir=isolated_store)
    _seed(PROJECT, "A=2", PASSWORD, isolated_store)
    create_checkpoint(PROJECT, "second", PASSWORD, store_dir=isolated_store)
    names = [c["name"] for c in list_checkpoints(PROJECT, store_dir=isolated_store)]
    assert names == ["first", "second"]


def test_delete_checkpoint_removes_entry(isolated_store):
    _seed(PROJECT, "KEY=val", PASSWORD, isolated_store)
    create_checkpoint(PROJECT, "v1", PASSWORD, store_dir=isolated_store)
    delete_checkpoint(PROJECT, "v1", store_dir=isolated_store)
    assert list_checkpoints(PROJECT, store_dir=isolated_store) == []


def test_delete_unknown_checkpoint_raises(isolated_store):
    _seed(PROJECT, "KEY=val", PASSWORD, isolated_store)
    with pytest.raises(CheckpointError, match="not found"):
        delete_checkpoint(PROJECT, "missing", store_dir=isolated_store)
