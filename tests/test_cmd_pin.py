"""Tests for envoy/cmd_pin.py."""
import argparse
import sys
import pytest
from unittest.mock import patch, MagicMock

from envoy.cmd_pin import (
    cmd_pin_set,
    cmd_pin_get,
    cmd_pin_remove,
    cmd_pin_list,
    register_pin_parser,
)
from envoy.pin import PinError


def _args(**kwargs):
    base = argparse.Namespace(store_dir=None)
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


def test_register_pin_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_pin_parser(sub, "/tmp/store")
    args = p.parse_args(["pin", "set", "myproject", "v1.2"])
    assert args.project == "myproject"
    assert args.version == "v1.2"


def test_register_pin_parser_list():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_pin_parser(sub, "/tmp/store")
    args = p.parse_args(["pin", "list"])
    assert args.pin_cmd == "list"


def test_cmd_pin_set_success(capsys):
    with patch("envoy.cmd_pin.pin_project") as mock_pin:
        cmd_pin_set(_args(project="alpha", version="v2.0"))
    mock_pin.assert_called_once_with("alpha", "v2.0", store_dir=None)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "v2.0" in out


def test_cmd_pin_set_error_exits():
    with patch("envoy.cmd_pin.pin_project", side_effect=PinError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_pin_set(_args(project="alpha", version="v2.0"))
    assert exc.value.code == 1


def test_cmd_pin_get_found(capsys):
    entry = {"version": "v1.0", "pinned_at": "2024-01-01T00:00:00"}
    with patch("envoy.cmd_pin.get_pin", return_value=entry):
        cmd_pin_get(_args(project="alpha"))
    out = capsys.readouterr().out
    assert "v1.0" in out
    assert "alpha" in out


def test_cmd_pin_get_not_found(capsys):
    with patch("envoy.cmd_pin.get_pin", return_value=None):
        cmd_pin_get(_args(project="ghost"))
    out = capsys.readouterr().out
    assert "No pin" in out


def test_cmd_pin_remove_success(capsys):
    with patch("envoy.cmd_pin.unpin_project") as mock_rm:
        cmd_pin_remove(_args(project="alpha"))
    mock_rm.assert_called_once_with("alpha", store_dir=None)
    assert "Removed" in capsys.readouterr().out


def test_cmd_pin_remove_error_exits():
    with patch("envoy.cmd_pin.unpin_project", side_effect=PinError("not pinned")):
        with pytest.raises(SystemExit) as exc:
            cmd_pin_remove(_args(project="ghost"))
    assert exc.value.code == 1


def test_cmd_pin_list_empty(capsys):
    with patch("envoy.cmd_pin.list_pins", return_value={}):
        cmd_pin_list(_args())
    assert "No pinned" in capsys.readouterr().out


def test_cmd_pin_list_with_entries(capsys):
    pins = {
        "alpha": {"version": "v1", "pinned_at": "2024-01-01T00:00:00"},
        "beta": {"version": "v2", "pinned_at": "2024-02-01T00:00:00"},
    }
    with patch("envoy.cmd_pin.list_pins", return_value=pins):
        cmd_pin_list(_args())
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out
    assert "v1" in out
    assert "v2" in out
