"""Integration tests: policy enforcement end-to-end with real storage."""

from __future__ import annotations

import pytest

from envoy.diff import parse_pairs
from envoy.policy import check_policy, set_policy
from envoy.storage import load_env, store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(store_dir, project, content, password="pw"):
    store_env(store_dir, project, content, password)
    return project


def test_policy_passes_after_store(isolated_store):
    _seed(isolated_store, "app", "DB_URL=postgres://localhost\nSECRET=abc")
    set_policy(isolated_store, "app", {"required_keys": ["DB_URL", "SECRET"]})
    raw = load_env(isolated_store, "app", "pw")
    pairs = parse_pairs(raw)
    assert check_policy(isolated_store, "app", pairs) == []


def test_policy_fails_after_partial_store(isolated_store):
    _seed(isolated_store, "app", "DB_URL=postgres://localhost")
    set_policy(isolated_store, "app", {"required_keys": ["DB_URL", "API_KEY"]})
    raw = load_env(isolated_store, "app", "pw")
    pairs = parse_pairs(raw)
    violations = check_policy(isolated_store, "app", pairs)
    assert any("API_KEY" in v for v in violations)


def test_policy_survives_re_store(isolated_store):
    _seed(isolated_store, "app", "X=1")
    set_policy(isolated_store, "app", {"max_keys": 2})
    # Re-store with two keys — still compliant
    store_env(isolated_store, "app", "X=1\nY=2", "pw")
    raw = load_env(isolated_store, "app", "pw")
    pairs = parse_pairs(raw)
    assert check_policy(isolated_store, "app", pairs) == []


def test_forbidden_key_caught_in_integration(isolated_store):
    _seed(isolated_store, "svc", "ADMIN_TOKEN=hunter2\nPORT=8080")
    set_policy(isolated_store, "svc", {"forbidden_keys": ["ADMIN_TOKEN"]})
    raw = load_env(isolated_store, "svc", "pw")
    pairs = parse_pairs(raw)
    violations = check_policy(isolated_store, "svc", pairs)
    assert any("ADMIN_TOKEN" in v for v in violations)
