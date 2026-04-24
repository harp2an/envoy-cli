"""Tests for envoy.cmd_retention CLI commands."""
from __future__ import annotations

import sys
import types
import pytest

from envoy.cmd_retention import (
    cmd_retention_get,
    cmd_retention_list,
    cmd_retention_remove,
    cmd_retention_set,
    register_retention_parser,
)
from envoy.storage import store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _args(**kwargs):
    ns = types.SimpleNamespace(project="alpha", max_versions=10, max_snapshots=5)
    ns.__dict__.update(kwargs)
    return ns


def test_register_retention_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_retention_parser(sub)
    args = p.parse_args(["retention", "list"])
    assert args.retention_cmd == "list"


def test_register_retention_parser_set():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_retention_parser(sub)
    args = p.parse_args(["retention", "set", "myproject", "--max-versions", "8", "--max-snapshots", "4"])
    assert args.project == "myproject"
    assert args.max_versions == 8
    assert args.max_snapshots == 4


def test_cmd_retention_set_success(isolated_store, capsys):
    store_env(isolated_store, "alpha", "K=V", "pw")
    cmd_retention_set(_args())
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "max_versions=10" in out


def test_cmd_retention_set_error_exits(isolated_store):
    with pytest.raises(SystemExit):
        cmd_retention_set(_args(project="ghost"))


def test_cmd_retention_get_not_set(isolated_store, capsys):
    store_env(isolated_store, "alpha", "K=V", "pw")
    cmd_retention_get(_args())
    out = capsys.readouterr().out
    assert "No retention policy" in out


def test_cmd_retention_get_after_set(isolated_store, capsys):
    store_env(isolated_store, "alpha", "K=V", "pw")
    cmd_retention_set(_args())
    cmd_retention_get(_args())
    out = capsys.readouterr().out
    assert "max_versions=10" in out


def test_cmd_retention_remove_success(isolated_store, capsys):
    store_env(isolated_store, "alpha", "K=V", "pw")
    cmd_retention_set(_args())
    cmd_retention_remove(_args())
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_retention_remove_error_exits(isolated_store):
    store_env(isolated_store, "alpha", "K=V", "pw")
    with pytest.raises(SystemExit):
        cmd_retention_remove(_args())


def test_cmd_retention_list_empty(isolated_store, capsys):
    cmd_retention_list(_args())
    out = capsys.readouterr().out
    assert "No retention" in out


def test_cmd_retention_list_with_entries(isolated_store, capsys):
    store_env(isolated_store, "alpha", "K=V", "pw")
    cmd_retention_set(_args())
    cmd_retention_list(_args())
    out = capsys.readouterr().out
    assert "alpha" in out
