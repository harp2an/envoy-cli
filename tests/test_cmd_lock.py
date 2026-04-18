"""Tests for envoy.cmd_lock."""

import sys
import types
import pytest

from envoy.cmd_lock import cmd_lock_acquire, cmd_lock_release, cmd_lock_status, register_lock_parser
from envoy.lock import acquire_lock, is_locked


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.lock.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    yield tmp_path


def _args(**kwargs):
    ns = types.SimpleNamespace(owner="envoy", project=None)
    ns.__dict__.update(kwargs)
    return ns


def test_cmd_lock_acquire_success(capsys):
    cmd_lock_acquire(_args(project="alpha"))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert is_locked("alpha")


def test_cmd_lock_acquire_already_locked_exits(capsys):
    acquire_lock("alpha")
    with pytest.raises(SystemExit):
        cmd_lock_acquire(_args(project="alpha"))


def test_cmd_lock_release_success(capsys):
    acquire_lock("beta")
    cmd_lock_release(_args(project="beta"))
    out = capsys.readouterr().out
    assert "released" in out
    assert not is_locked("beta")


def test_cmd_lock_release_no_lock_prints_message(capsys):
    cmd_lock_release(_args(project="ghost"))
    out = capsys.readouterr().out
    assert "No active lock" in out


def test_cmd_lock_status_shows_locked(capsys, monkeypatch):
    monkeypatch.setattr("envoy.cmd_lock.load_manifest", lambda: {"gamma": {}})
    acquire_lock("gamma")
    cmd_lock_status(_args(project="gamma"))
    out = capsys.readouterr().out
    assert "LOCKED" in out


def test_cmd_lock_status_shows_unlocked(capsys, monkeypatch):
    monkeypatch.setattr("envoy.cmd_lock.load_manifest", lambda: {})
    cmd_lock_status(_args(project="delta"))
    out = capsys.readouterr().out
    assert "unlocked" in out


def test_register_lock_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_lock_parser(sub)
    args = p.parse_args(["lock", "acquire", "myproj"])
    assert args.project == "myproj"
