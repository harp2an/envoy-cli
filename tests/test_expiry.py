"""Tests for envoy.expiry module."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from envoy.expiry import (
    ExpiryError,
    set_expiry,
    get_expiry,
    remove_expiry,
    is_expired,
    list_expiries,
)
from envoy.storage import store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    store_env("alpha", "KEY=val", "pw", store_dir=tmp_path)
    store_env("beta", "X=1", "pw", store_dir=tmp_path)
    return tmp_path


def test_set_expiry_returns_iso(isolated_store):
    result = set_expiry("alpha", "2099-01-01T00:00:00", store_dir=isolated_store)
    assert result == "2099-01-01T00:00:00"


def test_set_expiry_persists(isolated_store):
    set_expiry("alpha", "2099-06-15T12:00:00", store_dir=isolated_store)
    assert get_expiry("alpha", store_dir=isolated_store) == "2099-06-15T12:00:00"


def test_get_expiry_missing_returns_none(isolated_store):
    assert get_expiry("alpha", store_dir=isolated_store) is None


def test_set_expiry_missing_project_raises(isolated_store):
    with pytest.raises(ExpiryError, match="not found"):
        set_expiry("ghost", "2099-01-01T00:00:00", store_dir=isolated_store)


def test_set_expiry_invalid_format_raises(isolated_store):
    with pytest.raises(ExpiryError, match="Invalid datetime"):
        set_expiry("alpha", "not-a-date", store_dir=isolated_store)


def test_remove_expiry_success(isolated_store):
    set_expiry("alpha", "2099-01-01T00:00:00", store_dir=isolated_store)
    remove_expiry("alpha", store_dir=isolated_store)
    assert get_expiry("alpha", store_dir=isolated_store) is None


def test_remove_expiry_not_set_raises(isolated_store):
    with pytest.raises(ExpiryError, match="No expiry set"):
        remove_expiry("alpha", store_dir=isolated_store)


def test_is_expired_future_returns_false(isolated_store):
    set_expiry("alpha", "2099-12-31T23:59:59", store_dir=isolated_store)
    assert is_expired("alpha", store_dir=isolated_store) is False


def test_is_expired_past_returns_true(isolated_store):
    set_expiry("alpha", "2000-01-01T00:00:00", store_dir=isolated_store)
    assert is_expired("alpha", store_dir=isolated_store) is True


def test_is_expired_no_expiry_returns_false(isolated_store):
    assert is_expired("alpha", store_dir=isolated_store) is False


def test_list_expiries_empty_when_none_set(isolated_store):
    assert list_expiries(store_dir=isolated_store) == {}


def test_list_expiries_returns_all(isolated_store):
    set_expiry("alpha", "2099-01-01T00:00:00", store_dir=isolated_store)
    set_expiry("beta", "2088-06-01T00:00:00", store_dir=isolated_store)
    result = list_expiries(store_dir=isolated_store)
    assert set(result.keys()) == {"alpha", "beta"}
