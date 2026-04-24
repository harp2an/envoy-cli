"""Tests for envoy.cmd_dependency."""
from __future__ import annotations

import argparse
import pytest

from envoy.cmd_dependency import (
    cmd_dep_add,
    cmd_dep_dependents,
    cmd_dep_list,
    cmd_dep_remove,
    register_dependency_parser,
)
from envoy.dependency import add_dependency
from envoy.storage import save_manifest


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.dependency.get_store_dir", lambda: tmp_path)
    manifest = {"alpha": {"file": "alpha.enc"}, "beta": {"file": "beta.enc"}}
    save_manifest(tmp_path, manifest)
    return tmp_path


def _args(**kwargs):
    ns = argparse.Namespace()
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_register_dependency_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_dependency_parser(sub)
    args = p.parse_args(["dependency", "list", "alpha"])
    assert args.project == "alpha"


def test_cmd_dep_add_success(isolated_store, capsys):
    cmd_dep_add(_args(project="alpha", depends_on="beta"))
    out = capsys.readouterr().out
    assert "alpha -> beta" in out


def test_cmd_dep_add_error_exits(isolated_store):
    with pytest.raises(SystemExit):
        cmd_dep_add(_args(project="alpha", depends_on="missing"))


def test_cmd_dep_remove_success(isolated_store, capsys):
    add_dependency("alpha", "beta", store_dir=isolated_store)
    cmd_dep_remove(_args(project="alpha", depends_on="beta"))
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_dep_remove_error_exits(isolated_store):
    with pytest.raises(SystemExit):
        cmd_dep_remove(_args(project="alpha", depends_on="beta"))


def test_cmd_dep_list_empty(isolated_store, capsys):
    cmd_dep_list(_args(project="alpha"))
    out = capsys.readouterr().out
    assert "No dependencies" in out


def test_cmd_dep_list_with_entries(isolated_store, capsys):
    add_dependency("alpha", "beta", store_dir=isolated_store)
    cmd_dep_list(_args(project="alpha"))
    out = capsys.readouterr().out
    assert "beta" in out


def test_cmd_dep_dependents_empty(isolated_store, capsys):
    cmd_dep_dependents(_args(project="beta"))
    out = capsys.readouterr().out
    assert "No projects" in out


def test_cmd_dep_dependents_with_entries(isolated_store, capsys):
    add_dependency("alpha", "beta", store_dir=isolated_store)
    cmd_dep_dependents(_args(project="beta"))
    out = capsys.readouterr().out
    assert "alpha" in out
