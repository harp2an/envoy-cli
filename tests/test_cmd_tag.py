"""Tests for envoy.cmd_tag."""

import sys
import pytest
from argparse import Namespace
from unittest.mock import patch

from envoy.cmd_tag import (
    cmd_tag_add, cmd_tag_remove, cmd_tag_list, cmd_tag_find,
    register_tag_parser,
)
from envoy.tag import TagError


def _args(**kwargs):
    defaults = {"project": "myproject", "tag": "prod"}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_register_tag_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_tag_parser(sub)
    args = p.parse_args(["tag", "add", "proj", "mytag"])
    assert args.project == "proj"
    assert args.tag == "mytag"


def test_cmd_tag_add_success(capsys):
    with patch("envoy.cmd_tag.add_tag") as mock:
        cmd_tag_add(_args())
        mock.assert_called_once_with("myproject", "prod")
    out = capsys.readouterr().out
    assert "added" in out


def test_cmd_tag_add_error_exits(capsys):
    with patch("envoy.cmd_tag.add_tag", side_effect=TagError("dup")):
        with pytest.raises(SystemExit):
            cmd_tag_add(_args())


def test_cmd_tag_remove_success(capsys):
    with patch("envoy.cmd_tag.remove_tag"):
        cmd_tag_remove(_args())
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_tag_list_with_tags(capsys):
    with patch("envoy.cmd_tag.list_tags", return_value=["prod", "staging"]):
        cmd_tag_list(_args())
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_cmd_tag_list_empty(capsys):
    with patch("envoy.cmd_tag.list_tags", return_value=[]):
        cmd_tag_list(_args())
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_find_results(capsys):
    with patch("envoy.cmd_tag.find_by_tag", return_value=["alpha", "beta"]):
        cmd_tag_find(_args())
    out = capsys.readouterr().out
    assert "alpha" in out


def test_cmd_tag_find_empty(capsys):
    with patch("envoy.cmd_tag.find_by_tag", return_value=[]):
        cmd_tag_find(_args())
    out = capsys.readouterr().out
    assert "No projects" in out
