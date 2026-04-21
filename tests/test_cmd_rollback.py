"""Tests for envoy.cmd_rollback."""

from __future__ import annotations

import argparse
import pytest
from unittest.mock import patch, MagicMock

from envoy.cmd_rollback import (
    cmd_rollback_list,
    cmd_rollback_restore,
    register_rollback_parser,
)
from envoy.rollback import RollbackError


def _args(**kwargs):
    base = {"project": "myproject", "index": 0}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_register_rollback_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    register_rollback_parser(sub)
    parsed = parser.parse_args(["rollback", "list", "myproject"])
    assert parsed.project == "myproject"


def test_register_rollback_parser_restore():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    register_rollback_parser(sub)
    parsed = parser.parse_args(["rollback", "restore", "myproject", "2"])
    assert parsed.project == "myproject"
    assert parsed.index == 2


def test_cmd_rollback_list_empty(capsys):
    with patch("envoy.cmd_rollback.list_rollback_points", return_value=[]):
        cmd_rollback_list(_args())
    out = capsys.readouterr().out
    assert "No rollback points" in out


def test_cmd_rollback_list_with_entries(capsys):
    points = [
        {"timestamp": "2024-01-01T00:00:00", "label": "before-deploy"},
        {"timestamp": "2024-01-02T00:00:00", "label": ""},
    ]
    with patch("envoy.cmd_rollback.list_rollback_points", return_value=points):
        cmd_rollback_list(_args())
    out = capsys.readouterr().out
    assert "2024-01-01" in out
    assert "before-deploy" in out
    assert "2024-01-02" in out


def test_cmd_rollback_restore_success(capsys):
    with patch("envoy.cmd_rollback.getpass", return_value="pass"), \
         patch("envoy.cmd_rollback.rollback_to_version", return_value="2024-01-01T00:00:00"):
        cmd_rollback_restore(_args())
    out = capsys.readouterr().out
    assert "Rolled back" in out
    assert "2024-01-01" in out


def test_cmd_rollback_restore_error_exits():
    with patch("envoy.cmd_rollback.getpass", return_value="bad"), \
         patch("envoy.cmd_rollback.rollback_to_version",
               side_effect=RollbackError("out of range")), \
         pytest.raises(SystemExit):
        cmd_rollback_restore(_args())
