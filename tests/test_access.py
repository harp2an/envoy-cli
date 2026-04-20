"""Tests for envoy.access and envoy.cmd_access."""

from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path

import pytest

from envoy.access import (
    AccessError,
    grant_access,
    revoke_access,
    list_access,
    check_access,
)
from envoy.cmd_access import (
    cmd_access_grant,
    cmd_access_revoke,
    cmd_access_list,
    cmd_access_check,
    register_access_parser,
)


@pytest.fixture()
def store(tmp_path: Path):
    return tmp_path


# --- access module ---

def test_grant_and_check(store):
    grant_access("proj", "alice", "read", store_dir=store)
    assert check_access("proj", "alice", "read", store_dir=store) is True


def test_check_missing_returns_false(store):
    assert check_access("proj", "bob", "write", store_dir=store) is False


def test_grant_invalid_permission_raises(store):
    with pytest.raises(AccessError, match="Invalid permission"):
        grant_access("proj", "alice", "superuser", store_dir=store)


def test_grant_duplicate_does_not_duplicate(store):
    grant_access("proj", "alice", "read", store_dir=store)
    grant_access("proj", "alice", "read", store_dir=store)
    acl = list_access("proj", store_dir=store)
    assert acl["alice"].count("read") == 1


def test_revoke_removes_permission(store):
    grant_access("proj", "alice", "write", store_dir=store)
    revoke_access("proj", "alice", "write", store_dir=store)
    assert check_access("proj", "alice", "write", store_dir=store) is False


def test_revoke_missing_identity_raises(store):
    with pytest.raises(AccessError, match="No access entry"):
        revoke_access("proj", "nobody", "read", store_dir=store)


def test_revoke_missing_permission_raises(store):
    grant_access("proj", "alice", "read", store_dir=store)
    with pytest.raises(AccessError, match="does not have"):
        revoke_access("proj", "alice", "write", store_dir=store)


def test_list_access_empty(store):
    assert list_access("proj", store_dir=store) == {}


def test_list_access_multiple(store):
    grant_access("proj", "alice", "read", store_dir=store)
    grant_access("proj", "bob", "admin", store_dir=store)
    acl = list_access("proj", store_dir=store)
    assert "alice" in acl and "bob" in acl


# --- cmd_access ---

def _args(**kwargs) -> Namespace:
    return Namespace(**kwargs)


def test_cmd_access_grant_success(store, capsys, monkeypatch):
    monkeypatch.setattr("envoy.access.get_store_dir", lambda: store)
    cmd_access_grant(_args(project="p", identity="alice", permission="read"))
    out = capsys.readouterr().out
    assert "Granted" in out


def test_cmd_access_revoke_error_exits(store, monkeypatch):
    monkeypatch.setattr("envoy.access.get_store_dir", lambda: store)
    with pytest.raises(SystemExit):
        cmd_access_revoke(_args(project="p", identity="ghost", permission="read"))


def test_cmd_access_list_empty(store, capsys, monkeypatch):
    monkeypatch.setattr("envoy.access.get_store_dir", lambda: store)
    cmd_access_list(_args(project="p"))
    assert "No access rules" in capsys.readouterr().out


def test_cmd_access_check_allowed(store, capsys, monkeypatch):
    monkeypatch.setattr("envoy.access.get_store_dir", lambda: store)
    grant_access("p", "alice", "write", store_dir=store)
    cmd_access_check(_args(project="p", identity="alice", permission="write"))
    assert "ALLOWED" in capsys.readouterr().out


def test_register_access_parser():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="cmd")
    register_access_parser(sub)
    args = root.parse_args(["access", "grant", "myproj", "alice", "read"])
    assert args.project == "myproj"
    assert args.permission == "read"
