"""Tests for envoy.share module."""

import pytest
from unittest.mock import patch
from pathlib import Path
from envoy.share import create_share, revoke_share, resolve_share, list_shares, ShareError


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.share.get_store_dir", lambda: tmp_path)
    yield tmp_path


def test_create_share_returns_token():
    token = create_share("myproject")
    assert isinstance(token, str)
    assert len(token) > 10


def test_create_share_persists():
    token = create_share("alpha", note="for bob")
    shares = list_shares()
    assert any(s["token"] == token for s in shares)


def test_resolve_share_returns_metadata():
    token = create_share("beta", note="test")
    meta = resolve_share(token)
    assert meta["project"] == "beta"
    assert meta["note"] == "test"


def test_resolve_unknown_token_returns_none():
    result = resolve_share("nonexistent-token")
    assert result is None


def test_revoke_share_removes_token():
    token = create_share("gamma")
    revoke_share(token)
    assert resolve_share(token) is None


def test_revoke_unknown_token_raises():
    with pytest.raises(ShareError):
        revoke_share("bad-token")


def test_list_shares_empty():
    assert list_shares() == []


def test_list_shares_multiple():
    create_share("p1")
    create_share("p2")
    shares = list_shares()
    projects = [s["project"] for s in shares]
    assert "p1" in projects
    assert "p2" in projects


def test_tokens_are_unique():
    t1 = create_share("proj")
    t2 = create_share("proj")
    assert t1 != t2
