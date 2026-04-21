"""Unit tests for envoy.policy."""

from __future__ import annotations

import pytest

from envoy.policy import (
    PolicyError,
    check_policy,
    get_policy,
    remove_policy,
    set_policy,
)
from envoy.storage import get_store_dir, store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    store_env(tmp_path, "alpha", "KEY=val", "pw")
    store_env(tmp_path, "beta", "A=1\nB=2\nC=3", "pw")
    return tmp_path


def test_set_policy_persists(isolated_store):
    set_policy(isolated_store, "alpha", {"required_keys": ["KEY"]})
    p = get_policy(isolated_store, "alpha")
    assert p == {"required_keys": ["KEY"]}


def test_get_policy_missing_returns_none(isolated_store):
    assert get_policy(isolated_store, "alpha") is None


def test_set_policy_missing_project_raises(isolated_store):
    with pytest.raises(PolicyError, match="not found"):
        set_policy(isolated_store, "ghost", {"max_keys": 5})


def test_set_policy_unknown_rule_raises(isolated_store):
    with pytest.raises(PolicyError, match="Unknown policy rule"):
        set_policy(isolated_store, "alpha", {"bad_rule": True})


def test_remove_policy_success(isolated_store):
    set_policy(isolated_store, "alpha", {"max_keys": 10})
    remove_policy(isolated_store, "alpha")
    assert get_policy(isolated_store, "alpha") is None


def test_remove_policy_missing_raises(isolated_store):
    with pytest.raises(PolicyError, match="No policy set"):
        remove_policy(isolated_store, "alpha")


def test_check_policy_no_policy_returns_empty(isolated_store):
    assert check_policy(isolated_store, "alpha", {"KEY": "val"}) == []


def test_check_policy_required_key_missing(isolated_store):
    set_policy(isolated_store, "alpha", {"required_keys": ["KEY", "MISSING"]})
    violations = check_policy(isolated_store, "alpha", {"KEY": "val"})
    assert any("MISSING" in v for v in violations)


def test_check_policy_forbidden_key_present(isolated_store):
    set_policy(isolated_store, "alpha", {"forbidden_keys": ["SECRET"]})
    violations = check_policy(isolated_store, "alpha", {"SECRET": "oops"})
    assert any("SECRET" in v for v in violations)


def test_check_policy_max_keys_exceeded(isolated_store):
    set_policy(isolated_store, "beta", {"max_keys": 2})
    violations = check_policy(isolated_store, "beta", {"A": "1", "B": "2", "C": "3"})
    assert any("Too many keys" in v for v in violations)


def test_check_policy_all_pass(isolated_store):
    set_policy(isolated_store, "beta", {
        "required_keys": ["A"],
        "forbidden_keys": ["X"],
        "max_keys": 5,
    })
    assert check_policy(isolated_store, "beta", {"A": "1", "B": "2"}) == []
