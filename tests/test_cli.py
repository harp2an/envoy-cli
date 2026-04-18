"""Tests for envoy.cli module."""

import sys
from unittest.mock import patch, MagicMock

import pytest

from envoy.cli import build_parser, cmd_ls, cmd_get, cmd_push


def test_parser_set_requires_project():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["set"])


def test_parser_get_parses_project():
    parser = build_parser()
    args = parser.parse_args(["get", "myapp"])
    assert args.project == "myapp"
    assert args.command == "get"


def test_parser_push_with_remote():
    parser = build_parser()
    args = parser.parse_args(["push", "myapp", "--remote", "http://example.com"])
    assert args.remote == "http://example.com"


def test_cmd_ls_no_projects(capsys):
    with patch("envoy.cli.list_projects", return_value=[]):
        args = MagicMock()
        cmd_ls(args)
    captured = capsys.readouterr()
    assert "No local projects" in captured.out


def test_cmd_ls_with_projects(capsys):
    with patch("envoy.cli.list_projects", return_value=["app1", "app2"]):
        cmd_ls(MagicMock())
    captured = capsys.readouterr()
    assert "app1" in captured.out
    assert "app2" in captured.out


def test_cmd_get_prints_env(capsys):
    args = MagicMock(project="myapp")
    with patch("envoy.cli.getpass.getpass", return_value="secret"):
        with patch("envoy.cli.load_env", return_value="KEY=val"):
            cmd_get(args)
    assert "KEY=val" in capsys.readouterr().out


def test_cmd_get_bad_password_exits():
    args = MagicMock(project="myapp")
    with patch("envoy.cli.getpass.getpass", return_value="wrong"):
        with patch("envoy.cli.load_env", side_effect=ValueError("bad password")):
            with pytest.raises(SystemExit):
                cmd_get(args)


def test_cmd_push_sync_error_exits():
    from envoy.sync import SyncError
    args = MagicMock(project="myapp", remote=None)
    with patch("envoy.cli.getpass.getpass", return_value="secret"):
        with patch("envoy.cli.push_env", side_effect=SyncError("no remote")):
            with pytest.raises(SystemExit):
                cmd_push(args)
