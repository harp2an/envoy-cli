"""Tests for envoy.lock."""

import time
import pytest

from envoy.lock import (
    LockError,
    ProjectLock,
    acquire_lock,
    is_locked,
    release_lock,
    LOCK_TIMEOUT,
    _lock_path,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.lock.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    yield tmp_path


def test_acquire_creates_lock_file(isolated_store):
    acquire_lock("myproject")
    assert _lock_path("myproject").exists()


def test_is_locked_true_after_acquire(isolated_store):
    acquire_lock("myproject")
    assert is_locked("myproject") is True


def test_is_locked_false_before_acquire(isolated_store):
    assert is_locked("myproject") is False


def test_release_removes_lock_file(isolated_store):
    acquire_lock("myproject")
    release_lock("myproject")
    assert not _lock_path("myproject").exists()


def test_is_locked_false_after_release(isolated_store):
    acquire_lock("myproject")
    release_lock("myproject")
    assert is_locked("myproject") is False


def test_acquire_locked_project_raises(isolated_store):
    acquire_lock("myproject")
    with pytest.raises(LockError, match="locked"):
        acquire_lock("myproject")


def test_acquire_stale_lock_succeeds(isolated_store, monkeypatch):
    acquire_lock("myproject")
    path = _lock_path("myproject")
    import json
    data = json.loads(path.read_text())
    data["acquired_at"] = time.time() - LOCK_TIMEOUT - 1
    path.write_text(json.dumps(data))
    acquire_lock("myproject")  # should not raise
    assert is_locked("myproject")


def test_project_lock_context_manager(isolated_store):
    with ProjectLock("proj"):
        assert is_locked("proj")
    assert not is_locked("proj")


def test_release_nonexistent_lock_is_noop(isolated_store):
    release_lock("ghost")  # should not raise
