"""Unit tests for envoy.alias."""

from __future__ import annotations

import pytest

from envoy.alias import (
    AliasError,
    add_alias,
    list_aliases,
    remove_alias,
    resolve_alias,
    update_alias,
)


@pytest.fixture()
def isolated_store(tmp_path):
    return tmp_path


def test_add_alias_success(isolated_store):
    add_alias("myapp", "my-application", store_dir=isolated_store)
    assert resolve_alias("myapp", store_dir=isolated_store) == "my-application"


def test_add_alias_duplicate_raises(isolated_store):
    add_alias("myapp", "project-a", store_dir=isolated_store)
    with pytest.raises(AliasError, match="already exists"):
        add_alias("myapp", "project-b", store_dir=isolated_store)


def test_update_alias_creates_new(isolated_store):
    update_alias("shortname", "long-project-name", store_dir=isolated_store)
    assert resolve_alias("shortname", store_dir=isolated_store) == "long-project-name"


def test_update_alias_overwrites_existing(isolated_store):
    add_alias("myapp", "project-a", store_dir=isolated_store)
    update_alias("myapp", "project-b", store_dir=isolated_store)
    assert resolve_alias("myapp", store_dir=isolated_store) == "project-b"


def test_remove_alias_success(isolated_store):
    add_alias("myapp", "project-a", store_dir=isolated_store)
    remove_alias("myapp", store_dir=isolated_store)
    assert resolve_alias("myapp", store_dir=isolated_store) is None


def test_remove_alias_missing_raises(isolated_store):
    with pytest.raises(AliasError, match="not found"):
        remove_alias("ghost", store_dir=isolated_store)


def test_resolve_alias_missing_returns_none(isolated_store):
    assert resolve_alias("nope", store_dir=isolated_store) is None


def test_list_aliases_empty(isolated_store):
    assert list_aliases(store_dir=isolated_store) == {}


def test_list_aliases_multiple(isolated_store):
    add_alias("a", "alpha", store_dir=isolated_store)
    add_alias("b", "beta", store_dir=isolated_store)
    result = list_aliases(store_dir=isolated_store)
    assert result == {"a": "alpha", "b": "beta"}


def test_aliases_persisted_across_calls(isolated_store):
    add_alias("x", "xray", store_dir=isolated_store)
    # Simulate a fresh call by calling list_aliases again
    aliases = list_aliases(store_dir=isolated_store)
    assert aliases["x"] == "xray"
