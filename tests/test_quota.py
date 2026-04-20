"""Tests for envoy.quota and envoy.cmd_quota."""

from __future__ import annotations

import pytest
from argparse import Namespace
from pathlib import Path

from envoy.storage import store_env
from envoy.quota import (
    QuotaError,
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
    DEFAULT_MAX_KEYS,
    DEFAULT_MAX_BYTES,
)
from envoy.cmd_quota import cmd_quota_set, cmd_quota_get, cmd_quota_remove, register_quota_parser


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    store_env("alpha", "KEY=val\n", "pass", store_dir=tmp_path)
    return tmp_path


def test_get_quota_defaults_when_not_set(isolated_store):
    q = get_quota("alpha", store_dir=isolated_store)
    assert q["max_keys"] == DEFAULT_MAX_KEYS
    assert q["max_bytes"] == DEFAULT_MAX_BYTES


def test_set_and_get_quota(isolated_store):
    set_quota("alpha", max_keys=10, max_bytes=1024, store_dir=isolated_store)
    q = get_quota("alpha", store_dir=isolated_store)
    assert q["max_keys"] == 10
    assert q["max_bytes"] == 1024


def test_set_quota_missing_project_raises(isolated_store):
    with pytest.raises(QuotaError, match="not found"):
        set_quota("ghost", max_keys=5, store_dir=isolated_store)


def test_set_quota_invalid_max_keys_raises(isolated_store):
    with pytest.raises(QuotaError, match="max_keys"):
        set_quota("alpha", max_keys=0, store_dir=isolated_store)


def test_set_quota_invalid_max_bytes_raises(isolated_store):
    with pytest.raises(QuotaError, match="max_bytes"):
        set_quota("alpha", max_bytes=-1, store_dir=isolated_store)


def test_remove_quota(isolated_store):
    set_quota("alpha", max_keys=5, store_dir=isolated_store)
    remove_quota("alpha", store_dir=isolated_store)
    q = get_quota("alpha", store_dir=isolated_store)
    assert q["max_keys"] == DEFAULT_MAX_KEYS


def test_remove_quota_not_set_raises(isolated_store):
    with pytest.raises(QuotaError, match="No custom quota"):
        remove_quota("alpha", store_dir=isolated_store)


def test_check_quota_passes(isolated_store):
    set_quota("alpha", max_keys=5, max_bytes=1024, store_dir=isolated_store)
    check_quota("alpha", "A=1\nB=2\n", store_dir=isolated_store)


def test_check_quota_exceeds_keys(isolated_store):
    set_quota("alpha", max_keys=1, store_dir=isolated_store)
    with pytest.raises(QuotaError, match="Key count"):
        check_quota("alpha", "A=1\nB=2\n", store_dir=isolated_store)


def test_check_quota_exceeds_bytes(isolated_store):
    set_quota("alpha", max_bytes=5, store_dir=isolated_store)
    with pytest.raises(QuotaError, match="bytes"):
        check_quota("alpha", "A=very_long_value\n", store_dir=isolated_store)


def test_cmd_quota_set_success(isolated_store, capsys):
    args = Namespace(project="alpha", max_keys=20, max_bytes=2048)
    cmd_quota_set(args, store_dir=isolated_store)
    out = capsys.readouterr().out
    assert "alpha" in out and "max_keys=20" in out


def test_cmd_quota_set_error_exits(isolated_store):
    args = Namespace(project="missing", max_keys=5, max_bytes=None)
    with pytest.raises(SystemExit):
        cmd_quota_set(args, store_dir=isolated_store)


def test_cmd_quota_get_prints(isolated_store, capsys):
    args = Namespace(project="alpha")
    cmd_quota_get(args, store_dir=isolated_store)
    out = capsys.readouterr().out
    assert "max_keys" in out


def test_cmd_quota_remove_success(isolated_store, capsys):
    set_quota("alpha", max_keys=3, store_dir=isolated_store)
    args = Namespace(project="alpha")
    cmd_quota_remove(args, store_dir=isolated_store)
    out = capsys.readouterr().out
    assert "defaults restored" in out


def test_register_quota_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_quota_parser(sub)
    args = p.parse_args(["quota", "get", "myproject"])
    assert args.project == "myproject"
