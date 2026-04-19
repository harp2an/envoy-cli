"""Tests for envoy.rename and envoy.cmd_rename."""

import os
import pytest
from unittest.mock import MagicMock
from envoy.rename import rename_project, RenameError
from envoy.cmd_rename import cmd_rename, register_rename_parser


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(store_dir, name="alpha"):
    from envoy.storage import store_env
    store_env(name, "KEY=val", "pw")


def test_rename_success(isolated_store):
    _seed(isolated_store)
    rename_project("alpha", "beta")
    from envoy.storage import load_manifest
    m = load_manifest()
    assert "beta" in m
    assert "alpha" not in m
    assert os.path.exists(os.path.join(isolated_store, m["beta"]["file"]))


def test_rename_missing_project_raises(isolated_store):
    with pytest.raises(RenameError, match="does not exist"):
        rename_project("ghost", "phantom")


def test_rename_duplicate_dst_raises(isolated_store):
    _seed(isolated_store, "alpha")
    _seed(isolated_store, "beta")
    with pytest.raises(RenameError, match="already exists"):
        rename_project("alpha", "beta")


def test_rename_same_name_raises(isolated_store):
    _seed(isolated_store)
    with pytest.raises(RenameError, match="identical"):
        rename_project("alpha", "alpha")


def test_rename_empty_name_raises(isolated_store):
    with pytest.raises(RenameError, match="must not be empty"):
        rename_project("", "beta")


def test_cmd_rename_success(isolated_store, capsys):
    _seed(isolated_store)
    args = MagicMock(old_name="alpha", new_name="gamma")
    cmd_rename(args)
    out = capsys.readouterr().out
    assert "gamma" in out


def test_cmd_rename_failure_exits(isolated_store):
    args = MagicMock(old_name="nope", new_name="x(SystemExit):
        cmd_rename(args)


def test_register_rename_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register_rename_parser(sub)
    parsed = p.parse_args(["rename", "a", "b"])
    assert parsed.old_name == "a"
    assert parsed.new_name == "b"
