"""Tests for envoy.cmd_trend CLI commands."""

from __future__ import annotations

import argparse
import pytest
from unittest.mock import patch, MagicMock

from envoy.cmd_trend import (
    cmd_trend_record,
    cmd_trend_list,
    cmd_trend_summary,
    cmd_trend_clear,
    register_trend_parser,
)
from envoy.trend import TrendError


def _args(**kwargs):
    base = {"project": "alpha", "metric": "score", "value": 7.5}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_register_trend_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register_trend_parser(sub)
    args = p.parse_args(["trend", "record", "alpha", "score", "3.14"])
    assert args.project == "alpha"
    assert args.metric == "score"
    assert args.value == 3.14


def test_register_trend_parser_summary():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register_trend_parser(sub)
    args = p.parse_args(["trend", "summary", "beta", "latency"])
    assert args.project == "beta"
    assert args.metric == "latency"


def test_cmd_trend_record_success(capsys):
    entry = {"metric": "score", "value": 7.5, "timestamp": "2024-01-01T00:00:00"}
    with patch("envoy.cmd_trend.record_trend", return_value=entry):
        cmd_trend_record(_args())
    out = capsys.readouterr().out
    assert "score=7.5" in out


def test_cmd_trend_record_error_exits(capsys):
    with patch("envoy.cmd_trend.record_trend", side_effect=TrendError("bad")):
        with pytest.raises(SystemExit):
            cmd_trend_record(_args())


def test_cmd_trend_list_with_data(capsys):
    points = [{"metric": "score", "value": 5.0, "timestamp": "2024-01-01T00:00:00"}]
    with patch("envoy.cmd_trend.get_trend", return_value=points):
        cmd_trend_list(_args())
    out = capsys.readouterr().out
    assert "score=5.0" in out


def test_cmd_trend_list_empty(capsys):
    with patch("envoy.cmd_trend.get_trend", return_value=[]):
        cmd_trend_list(_args())
    out = capsys.readouterr().out
    assert "No data" in out


def test_cmd_trend_summary_success(capsys):
    summary = {
        "project": "alpha", "metric": "score",
        "count": 3, "min": 1.0, "max": 5.0, "avg": 3.0, "direction": "up",
    }
    with patch("envoy.cmd_trend.summarise_trend", return_value=summary):
        cmd_trend_summary(_args())
    out = capsys.readouterr().out
    assert "up" in out
    assert "3.0" in out


def test_cmd_trend_summary_error_exits(capsys):
    with patch("envoy.cmd_trend.summarise_trend", side_effect=TrendError("none")):
        with pytest.raises(SystemExit):
            cmd_trend_summary(_args())


def test_cmd_trend_clear_success(capsys):
    with patch("envoy.cmd_trend.clear_trends", return_value=4):
        cmd_trend_clear(_args())
    out = capsys.readouterr().out
    assert "4" in out


def test_cmd_trend_clear_error_exits(capsys):
    with patch("envoy.cmd_trend.clear_trends", side_effect=TrendError("oops")):
        with pytest.raises(SystemExit):
            cmd_trend_clear(_args())
