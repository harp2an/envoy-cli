"""Tests for envoy.cmd_history."""
from __future__ import annotations

import pytest
from argparse import Namespace
from unittest.mock import patch, MagicMock

from envoy.cmd_history import (
    cmd_history_list, cmd_history_restore, cmd_history_clear, register_history_parser
)
from envoy.history import HistoryError


def _args(**kwargs):
    defaults = {"project": "myproj"}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_register_history_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_history_parser(sub)
    args = p.parse_args(["history", "list", "myproj"])
    assert args.project == "myproj"


def test_cmd_history_list_empty(capsys):
    with patch("envoy.cmd_history.list_versions", return_value=[]):
        cmd_history_list(_args())
    out = capsys.readouterr().out
    assert "No history" in out


def test_cmd_history_list_with_entries(capsys):
    entries = [{"ciphertext": "c1", "label": "v1"}, {"ciphertext": "c2", "label": ""}]
    with patch("envoy.cmd_history.list_versions", return_value=entries):
        cmd_history_list(_args())
    out = capsys.readouterr().out
    assert "[v1]" in out
    assert "0:" in out


def test_cmd_history_restore_success(capsys):
    with patch("envoy.cmd_history.get_version", return_value="cipher"), \
         patch("envoy.cmd_history.decrypt", return_value="K=V"), \
         patch("envoy.cmd_history.store_env") as mock_store:
        cmd_history_restore(_args(index=0, password="pw"))
    mock_store.assert_called_once_with("myproj", "cipher")


def test_cmd_history_restore_bad_index_exits():
    with patch("envoy.cmd_history.get_version", side_effect=HistoryError("oops")):
        with pytest.raises(SystemExit):
            cmd_history_restore(_args(index=99, password="pw"))


def test_cmd_history_restore_wrong_password_exits():
    with patch("envoy.cmd_history.get_version", return_value="cipher"), \
         patch("envoy.cmd_history.decrypt", side_effect=Exception("bad")):
        with pytest.raises(SystemExit):
            cmd_history_restore(_args(index=0, password="wrong"))


def test_cmd_history_clear(capsys):
    with patch("envoy.cmd_history.clear_history") as mock_clear:
        cmd_history_clear(_args())
    mock_clear.assert_called_once_with("myproj")
    assert "cleared" in capsys.readouterr().out
