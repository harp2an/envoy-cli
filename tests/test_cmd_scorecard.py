"""Tests for envoy.cmd_scorecard."""
from __future__ import annotations

import json
import pytest
from argparse import Namespace
from unittest.mock import patch

from envoy.cmd_scorecard import (
    cmd_scorecard_compute,
    cmd_scorecard_get,
    cmd_scorecard_list,
    cmd_scorecard_remove,
    register_scorecard_parser,
)
from envoy.scorecard import ScorecardError


def _args(**kw) -> Namespace:
    return Namespace(**kw)


_SAMPLE = {
    "project": "myproject",
    "score": 50,
    "checks": {"has_env_file": True, "has_description": False,
               "has_tags": False, "has_annotation": False,
               "has_rating": False, "has_retention": False},
}


def test_register_scorecard_parser():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    register_scorecard_parser(sub)
    args = root.parse_args(["scorecard", "list"])
    assert args.scorecard_cmd == "list"


def test_cmd_scorecard_compute_success(capsys):
    with patch("envoy.cmd_scorecard.compute_score", return_value=_SAMPLE):
        cmd_scorecard_compute(_args(project="myproject"))
    out = capsys.readouterr().out
    assert "50/100" in out
    assert "has_env_file" in out


def test_cmd_scorecard_compute_error_exits():
    with patch("envoy.cmd_scorecard.compute_score", side_effect=ScorecardError("not found")):
        with pytest.raises(SystemExit):
            cmd_scorecard_compute(_args(project="bad"))


def test_cmd_scorecard_get_found(capsys):
    with patch("envoy.cmd_scorecard.get_scorecard", return_value=_SAMPLE):
        cmd_scorecard_get(_args(project="myproject"))
    out = capsys.readouterr().out
    assert "50/100" in out


def test_cmd_scorecard_get_missing(capsys):
    with patch("envoy.cmd_scorecard.get_scorecard", return_value=None):
        cmd_scorecard_get(_args(project="unknown"))
    assert "No scorecard" in capsys.readouterr().out


def test_cmd_scorecard_list_empty(capsys):
    with patch("envoy.cmd_scorecard.list_scorecards", return_value=[]):
        cmd_scorecard_list(_args())
    assert "No scorecards" in capsys.readouterr().out


def test_cmd_scorecard_list_with_entries(capsys):
    cards = [_SAMPLE, {**_SAMPLE, "project": "other", "score": 80}]
    with patch("envoy.cmd_scorecard.list_scorecards", return_value=cards):
        cmd_scorecard_list(_args())
    out = capsys.readouterr().out
    assert "myproject" in out
    assert "other" in out


def test_cmd_scorecard_remove_success(capsys):
    with patch("envoy.cmd_scorecard.remove_scorecard"):
        cmd_scorecard_remove(_args(project="myproject"))
    assert "removed" in capsys.readouterr().out


def test_cmd_scorecard_remove_error_exits():
    with patch("envoy.cmd_scorecard.remove_scorecard", side_effect=ScorecardError("No scorecard")):
        with pytest.raises(SystemExit):
            cmd_scorecard_remove(_args(project="bad"))
