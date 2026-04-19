"""Tests for envoy.prune and envoy.cmd_prune."""

from __future__ import annotations

import argparse
import pytest

from envoy.storage import store_env, load_manifest, get_store_dir
from envoy.prune import PruneError, list_orphaned, prune_orphaned, prune_project
from envoy.cmd_prune import cmd_prune, register_prune_parser


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return str(tmp_path)


def _seed(project: str, content: str = "KEY=val", password: str = "pw", store=None):
    store_env(project, content, password, store_dir=store)


def test_list_orphaned_empty(isolated_store):
    assert list_orphaned(store_dir=isolated_store) == []


def test_list_orphaned_detects_missing_file(isolated_store):
    _seed("alpha", store=isolated_store)
    env_path = get_store_dir(isolated_store) / "alpha.env"
    env_path.unlink()
    orphaned = list_orphaned(store_dir=isolated_store)
    assert "alpha" in orphaned


def test_prune_orphaned_removes_from_manifest(isolated_store):
    _seed("alpha", store=isolated_store)
    env_path = get_store_dir(isolated_store) / "alpha.env"
    env_path.unlink()
    removed = prune_orphaned(store_dir=isolated_store)
    assert "alpha" in removed
    manifest = load_manifest(isolated_store)
    assert "alpha" not in manifest


def test_prune_orphaned_nothing_to_do(isolated_store):
    _seed("beta", store=isolated_store)
    removed = prune_orphaned(store_dir=isolated_store)
    assert removed == []


def test_prune_project_removes_file_and_manifest(isolated_store):
    _seed("gamma", store=isolated_store)
    prune_project("gamma", store_dir=isolated_store)
    manifest = load_manifest(isolated_store)
    assert "gamma" not in manifest
    env_path = get_store_dir(isolated_store) / "gamma.env"
    assert not env_path.exists()


def test_prune_project_missing_raises(isolated_store):
    with pytest.raises(PruneError):
        prune_project("no_such", store_dir=isolated_store)


def _args(**kwargs):
    base = {"project": None, "dry_run": False, "store": None}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_cmd_prune_dry_run_no_orphans(isolated_store, capsys):
    _seed("delta", store=isolated_store)
    cmd_prune(_args(dry_run=True, store=isolated_store))
    out = capsys.readouterr().out
    assert "No orphaned" in out


def test_cmd_prune_specific_project(isolated_store, capsys):
    _seed("epsilon", store=isolated_store)
    cmd_prune(_args(project="epsilon", store=isolated_store))
    out = capsys.readouterr().out
    assert "epsilon" in out


def test_register_prune_parser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_prune_parser(subs)
    args = parser.parse_args(["prune", "--dry-run"])
    assert args.dry_run is True
