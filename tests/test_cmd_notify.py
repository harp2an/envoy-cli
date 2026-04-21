"""Tests for envoy.cmd_notify."""
from __future__ import annotations

import sys
import pytest
from argparse import Namespace
from unittest.mock import patch, MagicMock

from envoy.cmd_notify import (
    cmd_notify_add,
    cmd_notify_remove,
    cmd_notify_list,
    register_notify_parser,
)
from envoy.notify import NotifyError


def _args(**kwargs):
    defaults = {"project": "myproj", "event": "push", "channel": "stdout", "target": ""}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_register_notify_parser():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    register_notify_parser(sub)
    parsed = root.parse_args(["notify", "add", "proj", "push", "stdout"])
    assert parsed.project == "proj"
    assert parsed.event == "push"


def test_register_notify_parser_list():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    register_notify_parser(sub)
    parsed = root.parse_args(["notify", "list"])
    assert parsed.notify_cmd == "list"


def test_cmd_notify_add_success(capsys):
    with patch("envoy.cmd_notify.add_rule") as mock_add:
        mock_add.return_value = MagicMock(project="p", event="push", channel="stdout", target="")
        cmd_notify_add(_args())
    out = capsys.readouterr().out
    assert "Added rule" in out


def test_cmd_notify_add_error_exits(capsys):
    with patch("envoy.cmd_notify.add_rule", side_effect=NotifyError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_notify_add(_args())
    assert exc.value.code == 1


def test_cmd_notify_remove_success(capsys):
    with patch("envoy.cmd_notify.remove_rule"):
        cmd_notify_remove(_args())
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_notify_remove_error_exits():
    with patch("envoy.cmd_notify.remove_rule", side_effect=NotifyError("nope")):
        with pytest.raises(SystemExit):
            cmd_notify_remove(_args())


def test_cmd_notify_list_empty(capsys):
    with patch("envoy.cmd_notify.list_rules", return_value=[]):
        cmd_notify_list(Namespace(project=None))
    assert "No notification" in capsys.readouterr().out


def test_cmd_notify_list_with_rules(capsys):
    from envoy.notify import NotifyRule
    rule = NotifyRule(project="proj", event="push", channel="stdout")
    with patch("envoy.cmd_notify.list_rules", return_value=[rule]):
        cmd_notify_list(Namespace(project=None))
    out = capsys.readouterr().out
    assert "proj" in out
    assert "push" in out
