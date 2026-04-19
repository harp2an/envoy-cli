"""Tests for envoy.cmd_share CLI commands."""

import pytest
import sys
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from envoy.cmd_share import (
    cmd_share_create, cmd_share_revoke, cmd_share_resolve,
    cmd_share_list, register_share_parser,
)
from envoy.share import ShareError


def _args(**kwargs):
    return SimpleNamespace(**kwargs)


def test_register_share_parser():
    import argparse
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd")
    register_share_parser(sp)
    args = p.parse_args(["share", "list"])
    assert args.share_cmd == "list"


def test_cmd_share_create_prints_token(capsys):
    with patch("envoy.cmd_share.create_share", return_value="tok123"):
        cmd_share_create(_args(project="myproj", note=""))
    out = capsys.readouterr().out
    assert "tok123" in out


def test_cmd_share_revoke_success(capsys):
    with patch("envoy.cmd_share.revoke_share") as mock_rev:
        cmd_share_revoke(_args(token="tok123"))
    out = capsys.readouterr().out
    assert "revoked" in out.lower()


def test_cmd_share_revoke_error_exits(capsys):
    with patch("envoy.cmd_share.revoke_share", side_effect=ShareError("not found")):
        with pytest.raises(SystemExit):
            cmd_share_revoke(_args(token="bad"))


def test_cmd_share_resolve_found(capsys):
    with patch("envoy.cmd_share.resolve_share", return_value={"project": "p1", "note": "hi"}):
        cmd_share_resolve(_args(token="tok"))
    out = capsys.readouterr().out
    assert "p1" in out
    assert "hi" in out


def test_cmd_share_resolve_not_found_exits():
    with patch("envoy.cmd_share.resolve_share", return_value=None):
        with pytest.raises(SystemExit):
            cmd_share_resolve(_args(token="missing"))


def test_cmd_share_list_empty(capsys):
    with patch("envoy.cmd_share.list_shares", return_value=[]):
        cmd_share_list(_args())
    assert "No active" in capsys.readouterr().out


def test_cmd_share_list_with_entries(capsys):
    shares = [{"token": "abc", "project": "proj1", "note": ""}]
    with patch("envoy.cmd_share.list_shares", return_value=shares):
        cmd_share_list(_args())
    out = capsys.readouterr().out
    assert "abc" in out
    assert "proj1" in out
