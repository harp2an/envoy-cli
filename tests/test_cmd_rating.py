"""Tests for envoy/cmd_rating.py"""

import pytest
import argparse
from unittest.mock import patch, MagicMock
from envoy.cmd_rating import (
    cmd_rating_set, cmd_rating_get, cmd_rating_remove, cmd_rating_list,
    register_rating_parser,
)
from envoy.rating import RatingError


def _args(**kwargs):
    base = {"project": "alpha", "score": 4, "note": "", "func": None}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_register_rating_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_rating_parser(sub)
    args = parser.parse_args(["rating", "list"])
    assert args.rating_cmd == "list"


def test_register_rating_parser_set():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_rating_parser(sub)
    args = parser.parse_args(["rating", "set", "myproject", "3", "--note", "ok"])
    assert args.project == "myproject"
    assert args.score == 3
    assert args.note == "ok"


def test_cmd_rating_set_success(capsys):
    with patch("envoy.cmd_rating.set_rating", return_value={"score": 4, "note": ""}):
        cmd_rating_set(_args(score=4, note=""))
    out = capsys.readouterr().out
    assert "4/5" in out
    assert "alpha" in out


def test_cmd_rating_set_with_note(capsys):
    with patch("envoy.cmd_rating.set_rating", return_value={"score": 5, "note": "great"}):
        cmd_rating_set(_args(score=5, note="great"))
    out = capsys.readouterr().out
    assert "great" in out


def test_cmd_rating_set_error_exits():
    with patch("envoy.cmd_rating.set_rating", side_effect=RatingError("bad")):
        with pytest.raises(SystemExit):
            cmd_rating_set(_args())


def test_cmd_rating_get_found(capsys):
    with patch("envoy.cmd_rating.get_rating", return_value={"score": 3, "note": "ok"}):
        cmd_rating_get(_args())
    out = capsys.readouterr().out
    assert "3/5" in out


def test_cmd_rating_get_not_found(capsys):
    with patch("envoy.cmd_rating.get_rating", return_value=None):
        cmd_rating_get(_args())
    assert "No rating" in capsys.readouterr().out


def test_cmd_rating_remove_success(capsys):
    with patch("envoy.cmd_rating.remove_rating"):
        cmd_rating_remove(_args())
    assert "removed" in capsys.readouterr().out


def test_cmd_rating_remove_error_exits():
    with patch("envoy.cmd_rating.remove_rating", side_effect=RatingError("nope")):
        with pytest.raises(SystemExit):
            cmd_rating_remove(_args())


def test_cmd_rating_list_empty(capsys):
    with patch("envoy.cmd_rating.list_ratings", return_value={}):
        cmd_rating_list(_args())
    assert "No ratings" in capsys.readouterr().out


def test_cmd_rating_list_with_entries(capsys):
    data = {"alpha": {"score": 5, "note": ""}, "beta": {"score": 2, "note": "meh"}}
    with patch("envoy.cmd_rating.list_ratings", return_value=data):
        cmd_rating_list(_args())
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "5/5" in out
    assert "meh" in out
