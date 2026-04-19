"""Tests for envoy.watch."""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envoy.watch import _mtime, watch_file, make_store_callback


def test_mtime_missing_file(tmp_path):
    missing = tmp_path / "nope.env"
    assert _mtime(missing) == 0.0


def test_mtime_existing_file(tmp_path):
    f = tmp_path / "a.env"
    f.write_text("X=1")
    assert _mtime(f) > 0.0


def test_watch_file_calls_on_change(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")

    calls = []

    def on_change(p):
        calls.append(p)

    # Patch sleep and simulate mtime change on second iteration
    original_mtime = env_file.stat().st_mtime
    mtime_sequence = [original_mtime, original_mtime + 1.0]
    mtime_iter = iter(mtime_sequence)

    with patch("envoy.watch.time.sleep"), \
         patch("envoy.watch._mtime", side_effect=lambda p: next(mtime_iter)):
        watch_file(env_file, on_change, interval=0.0, max_iterations=1)

    assert len(calls) == 1
    assert calls[0] == env_file


def test_watch_file_no_change_no_callback(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")
    fixed_mtime = env_file.stat().st_mtime

    calls = []

    with patch("envoy.watch.time.sleep"), \
         patch("envoy.watch._mtime", return_value=fixed_mtime):
        watch_file(env_file, lambda p: calls.append(p), interval=0.0, max_iterations=3)

    assert calls == []


def test_make_store_callback_invokes_store_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val")

    with patch("envoy.watch.store_env") as mock_store:
        cb = make_store_callback("myproject", "secret")
        cb(env_file)
        mock_store.assert_called_once_with("myproject", "KEY=val", "secret")


def test_watch_file_accepts_string_path(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("B=2")
    fixed = env_file.stat().st_mtime

    with patch("envoy.watch.time.sleep"), \
         patch("envoy.watch._mtime", return_value=fixed):
        # Should not raise even when path is a string
        watch_file(str(env_file), lambda p: None, interval=0.0, max_iterations=1)
