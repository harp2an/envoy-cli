"""Tests for envoy.cmd_bookmark CLI handlers."""

import sys
import pytest
from unittest.mock import patch, MagicMock
from envoy.cmd_bookmark import (
    cmd_bookmark_add,
    cmd_bookmark_remove,
    cmd_bookmark_get,
    cmd_bookmark_list,
    register_bookmark_parser,
)


def _args(**kwargs):
    m = MagicMock()
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def test_register_bookmark_parser():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    register_bookmark_parser(sub)
    ns = root.parse_args(["bookmark", "list"])
    assert ns.func == cmd_bookmark_list


def test_register_bookmark_parser_add():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    register_bookmark_parser(sub)
    ns = root.parse_args(["bookmark", "add", "mymark", "proj", "KEY"])
    assert ns.name == "mymark"
    assert ns.project == "proj"
    assert ns.key == "KEY"


def test_cmd_bookmark_add_success(capsys):
    with patch("envoy.cmd_bookmark.get_store_dir"), \
         patch("envoy.cmd_bookmark.add_bookmark") as mock_add:
        cmd_bookmark_add(_args(name="m", project="p", key="K"))
    mock_add.assert_called_once()
    out = capsys.readouterr().out
    assert "m" in out


def test_cmd_bookmark_add_error_exits(capsys):
    from envoy.bookmark import BookmarkError
    with patch("envoy.cmd_bookmark.get_store_dir"), \
         patch("envoy.cmd_bookmark.add_bookmark", side_effect=BookmarkError("bad")):
        with pytest.raises(SystemExit):
            cmd_bookmark_add(_args(name="m", project="p", key="K"))


def test_cmd_bookmark_get_success(capsys):
    with patch("envoy.cmd_bookmark.get_store_dir"), \
         patch("envoy.cmd_bookmark.get_bookmark", return_value={"project": "p", "key": "K"}):
        cmd_bookmark_get(_args(name="m"))
    assert "p:K" in capsys.readouterr().out


def test_cmd_bookmark_get_missing_exits(capsys):
    with patch("envoy.cmd_bookmark.get_store_dir"), \
         patch("envoy.cmd_bookmark.get_bookmark", return_value=None):
        with pytest.raises(SystemExit):
            cmd_bookmark_get(_args(name="ghost"))


def test_cmd_bookmark_list_empty(capsys):
    with patch("envoy.cmd_bookmark.get_store_dir"), \
         patch("envoy.cmd_bookmark.list_bookmarks", return_value=[]):
        cmd_bookmark_list(_args())
    assert "No bookmarks" in capsys.readouterr().out


def test_cmd_bookmark_list_with_entries(capsys):
    entries = [{"name": "m", "project": "proj", "key": "KEY"}]
    with patch("envoy.cmd_bookmark.get_store_dir"), \
         patch("envoy.cmd_bookmark.list_bookmarks", return_value=entries):
        cmd_bookmark_list(_args())
    out = capsys.readouterr().out
    assert "proj" in out and "KEY" in out
