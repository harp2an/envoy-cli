"""Tests for envoy.merge."""

import pytest
from unittest.mock import patch

from envoy.merge import merge_envs, merge_projects, MergeError


@pytest.fixture
def isolated_store(tmp_path):
    from envoy.storage import store_env
    store_env("alpha", "A=1\nB=2\nC=3", "pass1", store_dir=tmp_path)
    store_env("beta", "B=99\nD=4", "pass2", store_dir=tmp_path)
    return tmp_path


def test_merge_envs_ours_keeps_base():
    base = {"A": "1", "B": "2"}
    other = {"B": "99", "C": "3"}
    result = merge_envs(base, other, strategy="ours")
    assert result["B"] == "2"
    assert result["C"] == "3"


def test_merge_envs_theirs_overrides():
    base = {"A": "1", "B": "2"}
    other = {"B": "99", "C": "3"}
    result = merge_envs(base, other, strategy="theirs")
    assert result["B"] == "99"
    assert result["C"] == "3"


def test_merge_envs_union_adds_new_keys():
    base = {"A": "1"}
    other = {"B": "2"}
    result = merge_envs(base, other, strategy="union")
    assert result["A"] == "1"
    assert result["B"] == "2"


def test_merge_envs_unknown_strategy_raises():
    with pytest.raises(MergeError, match="Unknown strategy"):
        merge_envs({}, {}, strategy="bad")


def test_merge_projects_roundtrip(isolated_store):
    from envoy.storage import load_env
    merged = merge_projects(
        "alpha", "beta", "pass1", "pass2", strategy="ours", store_dir=isolated_store
    )
    assert "A" in merged
    assert "B" in merged
    assert merged["B"] == "99"  # dst (beta) value kept under "ours" relative to dst
    assert "C" in merged
    assert "D" in merged


def test_merge_projects_theirs(isolated_store):
    merged = merge_projects(
        "alpha", "beta", "pass1", "pass2", strategy="theirs", store_dir=isolated_store
    )
    # src=alpha B=2 overrides dst=beta B=99 under theirs
    assert merged["B"] == "2"


def test_merge_projects_bad_password_raises(isolated_store):
    with pytest.raises(Exception):
        merge_projects("alpha", "beta", "wrong", "pass2", store_dir=isolated_store)
