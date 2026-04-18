"""Tests for envoy.search module."""

import pytest
from unittest.mock import patch

from envoy.crypto import encrypt
from envoy.search import search_key, search_value


ENV_A = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"
ENV_B = "DB_HOST=remotehost\nAPI_KEY=abc123\nDEBUG=false\n"


@pytest.fixture()
def mock_store(tmp_path):
    password = "testpass"
    from envoy.storage import store_env
    store_env("project_a", encrypt(ENV_A, password), store_dir=str(tmp_path))
    store_env("project_b", encrypt(ENV_B, password), store_dir=str(tmp_path))
    return str(tmp_path), password


def test_search_key_found_in_multiple(mock_store):
    store_dir, password = mock_store
    results = search_key("DB_HOST", password, store_dir=store_dir)
    assert set(results.keys()) == {"project_a", "project_b"}
    assert results["project_a"] == "localhost"
    assert results["project_b"] == "remotehost"


def test_search_key_found_in_one(mock_store):
    store_dir, password = mock_store
    results = search_key("API_KEY", password, store_dir=store_dir)
    assert list(results.keys()) == ["project_b"]
    assert results["project_b"] == "abc123"


def test_search_key_not_found(mock_store):
    store_dir, password = mock_store
    results = search_key("NONEXISTENT", password, store_dir=store_dir)
    assert results == {}


def test_search_value_pattern(mock_store):
    store_dir, password = mock_store
    results = search_value("abc123", password, store_dir=store_dir)
    assert "project_a" in results
    assert "project_b" in results
    assert results["project_a"] == {"SECRET": "abc123"}
    assert results["project_b"] == {"API_KEY": "abc123"}


def test_search_value_no_match(mock_store):
    store_dir, password = mock_store
    results = search_value("zzznomatch", password, store_dir=store_dir)
    assert results == {}


def test_search_key_wrong_password_skips(mock_store):
    store_dir, _ = mock_store
    results = search_key("DB_HOST", "wrongpass", store_dir=store_dir)
    assert results == {}
