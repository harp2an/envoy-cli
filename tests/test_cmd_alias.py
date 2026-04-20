"""Tests for envoy.cmd_alias CLI handlers."""

from __future__ import annotations

import sys
from argparse import Namespace
from unittest.mock import patch

import pytest

from envoy.cmd_alias import (
    cmd_alias_add,
    cmd_alias_list,
    cmd_alias_remove,
    cmd_alias_resolve,
    cmd_alias_update,
    register_alias_parser,
)


def _args(**kwargs) -> Namespace:
    return Namespace(**kwargs)


def test_register_alias_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_alias_parser(sub)
    args = p.parse_args(["alias", "list"])
    assert args.func == cmd_alias_list


def test_cmd_alias_add_success(tmp_path, capsys):
    with patch("envoy.cmd_alias.add_alias") as mock_add:
        cmd_alias_add(_args(alias="app", project="my-app"))
    mock_add.assert_called_once_with("app", "my-app")
    out = capsys.readouterr().out
    assert "app" in out and "my-app" in out


def test_cmd_alias_add_error_exits(capsys):
    from envoy.alias import AliasError
    with patch("envoy.cmd_alias.add_alias", side_effect=AliasError("already exists")):
        with pytest.raises(SystemExit) as exc:
            cmd_alias_add(_args(alias="app", project="other"))
    assert exc.value.code == 1
    assert "already exists" in capsys.readouterr().err


def test_cmd_alias_update_success(capsys):
    with patch("envoy.cmd_alias.update_alias") as mock_upd:
        cmd_alias_update(_args(alias="app", project="new-project"))
    mock_upd.assert_called_once_with("app", "new-project")
    assert "updated" in capsys.readouterr().out


def test_cmd_alias_remove_success(capsys):
    with patch("envoy.cmd_alias.remove_alias") as mock_rm:
        cmd_alias_remove(_args(alias="app"))
    mock_rm.assert_called_once_with("app")
    assert "removed" in capsys.readouterr().out


def test_cmd_alias_remove_error_exits(capsys):
    from envoy.alias import AliasError
    with patch("envoy.cmd_alias.remove_alias", side_effect=AliasError("not found")):
        with pytest.raises(SystemExit) as exc:
            cmd_alias_remove(_args(alias="ghost"))
    assert exc.value.code == 1


def test_cmd_alias_resolve_found(capsys):
    with patch("envoy.cmd_alias.resolve_alias", return_value="my-project"):
        cmd_alias_resolve(_args(alias="myapp"))
    assert "my-project" in capsys.readouterr().out


def test_cmd_alias_resolve_not_found_exits(capsys):
    with patch("envoy.cmd_alias.resolve_alias", return_value=None):
        with pytest.raises(SystemExit) as exc:
            cmd_alias_resolve(_args(alias="ghost"))
    assert exc.value.code == 1


def test_cmd_alias_list_empty(capsys):
    with patch("envoy.cmd_alias.list_aliases", return_value={}):
        cmd_alias_list(_args())
    assert "No aliases" in capsys.readouterr().out


def test_cmd_alias_list_with_entries(capsys):
    with patch("envoy.cmd_alias.list_aliases", return_value={"a": "alpha", "b": "beta"}):
        cmd_alias_list(_args())
    out = capsys.readouterr().out
    assert "a -> alpha" in out
    assert "b -> beta" in out
