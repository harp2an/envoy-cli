"""Tests for envoy.cmd_profile CLI commands."""
from __future__ import annotations

import json
from argparse import Namespace
from unittest.mock import patch

import pytest

from envoy.cmd_profile import (
    cmd_profile_get,
    cmd_profile_list,
    cmd_profile_remove,
    cmd_profile_set,
    register_profile_parser,
)
from envoy.profile import ProfileError


def _args(**kwargs) -> Namespace:
    defaults = {"project": "myapp", "profile": "dev", "override": []}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_register_profile_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_profile_parser(sub)
    args = p.parse_args(["profile", "list", "myapp"])
    assert args.project == "myapp"


def test_cmd_profile_set_success(capsys):
    with patch("envoy.cmd_profile.set_profile") as mock_set:
        cmd_profile_set(_args(override=["DEBUG=1", "LOG=verbose"]))
    mock_set.assert_called_once_with("myapp", "dev", {"DEBUG": "1", "LOG": "verbose"})
    out = capsys.readouterr().out
    assert "set" in out


def test_cmd_profile_set_invalid_override_exits(capsys):
    with pytest.raises(SystemExit):
        cmd_profile_set(_args(override=["BADPAIR"]))


def test_cmd_profile_set_error_exits(capsys):
    with patch("envoy.cmd_profile.set_profile", side_effect=ProfileError("oops")):
        with pytest.raises(SystemExit):
            cmd_profile_set(_args())


def test_cmd_profile_get_found(capsys):
    with patch("envoy.cmd_profile.get_profile", return_value={"A": "1"}):
        cmd_profile_get(_args())
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data == {"A": "1"}


def test_cmd_profile_get_not_found(capsys):
    with patch("envoy.cmd_profile.get_profile", return_value=None):
        cmd_profile_get(_args())
    assert "No profile" in capsys.readouterr().out


def test_cmd_profile_remove_success(capsys):
    with patch("envoy.cmd_profile.remove_profile") as mock_rm:
        cmd_profile_remove(_args())
    mock_rm.assert_called_once_with("myapp", "dev")
    assert "removed" in capsys.readouterr().out


def test_cmd_profile_remove_error_exits(capsys):
    with patch("envoy.cmd_profile.remove_profile", side_effect=ProfileError("gone")):
        with pytest.raises(SystemExit):
            cmd_profile_remove(_args())


def test_cmd_profile_list_empty(capsys):
    with patch("envoy.cmd_profile.list_profiles", return_value=[]):
        cmd_profile_list(_args())
    assert "No profiles" in capsys.readouterr().out


def test_cmd_profile_list_with_entries(capsys):
    with patch("envoy.cmd_profile.list_profiles", return_value=["dev", "prod"]):
        cmd_profile_list(_args())
    out = capsys.readouterr().out
    assert "dev" in out and "prod" in out
