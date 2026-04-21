"""Unit tests for envoy.cmd_policy."""

from __future__ import annotations

import argparse
import sys
import types

import pytest

from envoy.cmd_policy import (
    cmd_policy_get,
    cmd_policy_remove,
    cmd_policy_set,
    register_policy_parser,
)
from envoy.policy import set_policy
from envoy.storage import store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    store_env(tmp_path, "proj", "KEY=value", "secret")
    return tmp_path


def _args(**kwargs):
    ns = argparse.Namespace(**kwargs)
    return ns


def test_register_policy_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_policy_parser(sub)
    args = p.parse_args(["policy", "set", "proj", "--required-keys", "A,B"])
    assert args.project == "proj"
    assert args.required_keys == "A,B"


def test_cmd_policy_set_success(isolated_store, capsys):
    args = _args(project="proj", required_keys="KEY", forbidden_keys="", max_keys=None)
    cmd_policy_set(args)
    out = capsys.readouterr().out
    assert "Policy set" in out


def test_cmd_policy_set_error_exits(isolated_store):
    args = _args(project="ghost", required_keys="", forbidden_keys="", max_keys=None)
    with pytest.raises(SystemExit):
        cmd_policy_set(args)


def test_cmd_policy_get_none(isolated_store, capsys):
    cmd_policy_get(_args(project="proj"))
    out = capsys.readouterr().out
    assert "No policy" in out


def test_cmd_policy_get_with_policy(isolated_store, capsys):
    set_policy(isolated_store, "proj", {"max_keys": 3})
    cmd_policy_get(_args(project="proj"))
    out = capsys.readouterr().out
    assert "max_keys" in out


def test_cmd_policy_remove_success(isolated_store, capsys):
    set_policy(isolated_store, "proj", {"max_keys": 3})
    cmd_policy_remove(_args(project="proj"))
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_policy_remove_error_exits(isolated_store):
    with pytest.raises(SystemExit):
        cmd_policy_remove(_args(project="proj"))
