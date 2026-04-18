import pytest
import argparse
from unittest.mock import patch, MagicMock
from envoy.cmd_diff import cmd_diff, register_diff_parser
from envoy.diff import DiffError


def _make_args(**kwargs):
    defaults = {
        "project_a": "alpha",
        "project_b": "beta",
        "password": "",
        "password_a": None,
        "password_b": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_register_diff_parser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    register_diff_parser(sub)
    args = root.parse_args(["diff", "alpha", "beta"])
    assert args.project_a == "alpha"
    assert args.project_b == "beta"


def test_register_diff_parser_passwords():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    register_diff_parser(sub)
    args = root.parse_args(
        ["diff", "alpha", "beta", "--password-a", "pa", "--password-b", "pb"]
    )
    assert args.password_a == "pa"
    assert args.password_b == "pb"


def test_cmd_diff_no_differences(capsys):
    args = _make_args()
    with patch("envoy.cmd_diff.diff_projects", return_value=[]) as mock_diff:
        with patch("envoy.cmd_diff.format_diff", return_value="") as mock_fmt:
            cmd_diff(args)
            mock_diff.assert_called_once_with("alpha", "beta", "", "")
    captured = capsys.readouterr()
    assert "No differences" in captured.out


def test_cmd_diff_with_output(capsys):
    args = _make_args()
    fake_results = [("added", "KEY", None, "val")]
    with patch("envoy.cmd_diff.diff_projects", return_value=fake_results):
        with patch("envoy.cmd_diff.format_diff", return_value="+ KEY=val"):
            cmd_diff(args)
    captured = capsys.readouterr()
    assert "+ KEY=val" in captured.out


def test_cmd_diff_error_exits(capsys):
    args = _make_args()
    with patch("envoy.cmd_diff.diff_projects", side_effect=DiffError("not found")):
        with pytest.raises(SystemExit) as exc:
            cmd_diff(args)
        assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cmd_diff_uses_per_project_passwords():
    args = _make_args(password_a="pa", password_b="pb")
    with patch("envoy.cmd_diff.diff_projects", return_value=[]) as mock_diff:
        with patch("envoy.cmd_diff.format_diff", return_value=""):
            cmd_diff(args)
    mock_diff.assert_called_once_with("alpha", "beta", "pa", "pb")
