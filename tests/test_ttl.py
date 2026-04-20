"""Tests for envoy.ttl module."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envoy.ttl import (
    TTLError,
    get_ttl,
    is_expired,
    list_ttls,
    remove_ttl,
    set_ttl,
)


@pytest.fixture
def isolated_store(tmp_path: Path) -> Path:
    return tmp_path


def test_set_ttl_returns_expiry_string(isolated_store):
    expiry = set_ttl("myproject", 3600, store_dir=isolated_store)
    assert isinstance(expiry, str)
    assert "T" in expiry  # ISO format


def test_set_ttl_persists(isolated_store):
    set_ttl("myproject", 3600, store_dir=isolated_store)
    result = get_ttl("myproject", store_dir=isolated_store)
    assert result is not None
    assert result["seconds"] == 3600
    assert "expires_at" in result


def test_get_ttl_missing_returns_none(isolated_store):
    result = get_ttl("ghost", store_dir=isolated_store)
    assert result is None


def test_set_ttl_zero_raises(isolated_store):
    with pytest.raises(TTLError, match="positive"):
        set_ttl("myproject", 0, store_dir=isolated_store)


def test_set_ttl_negative_raises(isolated_store):
    with pytest.raises(TTLError, match="positive"):
        set_ttl("myproject", -60, store_dir=isolated_store)


def test_remove_ttl_success(isolated_store):
    set_ttl("myproject", 3600, store_dir=isolated_store)
    remove_ttl("myproject", store_dir=isolated_store)
    assert get_ttl("myproject", store_dir=isolated_store) is None


def test_remove_ttl_missing_raises(isolated_store):
    with pytest.raises(TTLError, match="No TTL set"):
        remove_ttl("ghost", store_dir=isolated_store)


def test_is_expired_not_expired(isolated_store):
    set_ttl("myproject", 3600, store_dir=isolated_store)
    assert is_expired("myproject", store_dir=isolated_store) is False


def test_is_expired_expired(isolated_store):
    set_ttl("myproject", 1, store_dir=isolated_store)
    time.sleep(1.1)
    assert is_expired("myproject", store_dir=isolated_store) is True


def test_is_expired_no_ttl_returns_false(isolated_store):
    assert is_expired("ghost", store_dir=isolated_store) is False


def test_list_ttls_empty(isolated_store):
    assert list_ttls(store_dir=isolated_store) == {}


def test_list_ttls_multiple(isolated_store):
    set_ttl("alpha", 100, store_dir=isolated_store)
    set_ttl("beta", 200, store_dir=isolated_store)
    result = list_ttls(store_dir=isolated_store)
    assert set(result.keys()) == {"alpha", "beta"}
    assert result["beta"]["seconds"] == 200
