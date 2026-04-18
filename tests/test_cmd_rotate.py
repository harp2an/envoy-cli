"""Tests for envoy.cmd_rotate."""

import argparse
import pytest

from envoy.cmd_rotate import cmd_rotate, register_rotate_parser
from envoy.storage import load_env, store_env


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _make_args(project=None):
    ns = argparse.Namespace(project=project)
    return ns


def _mock_passwords(current, new, confirm):
    """Return a getpass mock that maps prompt strings to passwords."""
    mapping = {
        "Current password: ": current,
        "New password: ": new,
        "Confirm new password: ": confirm,
    }
    return lambda prompt: mapping.get(prompt, "")


def test_register_rotate_parser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_rotate_parser(subs)
    args = parser.parse_args(["rotate", "myapp"])
    assert args.project == "myapp"


def test_register_rotate_parser_no_project():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_rotate_parser(subs)
    args = parser.parse_args(["rotate"])
    assert args.project is None


def test_cmd_rotate_single_project(monkeypatch, capsys):
    store_env("proj", "K=V", "old")
    monkeypatch.setattr("getpass.getpass", _mock_passwords("old", "new", "new"))
    cmd_rotate(_make_args(project="proj"))
    out = capsys.readouterr().out
    assert "proj" in out
    assert load_env("proj", "new") == "K=V"


def test_cmd_rotate_password_mismatch_exits(monkeypatch):
    passwords = ["old", "new1", "new2"]
    it = iter(passwords)
    monkeypatch.setattr("getpass.getpass", lambda _: next(it))
    with pytest.raises(SystemExit):
        cmd_rotate(_make_args(project="proj"))


def test_cmd_rotate_wrong_password_exits(monkeypatch):
    store_env("proj", "K=V", "correct")
    monkeypatch.setattr("getpass.getpass", _mock_passwords("wrong", "new", "new"))
    with pytest.raises(SystemExit):
        cmd_rotate(_make_args(project="proj"))
