"""Unit tests for envoy.profile."""
from __future__ import annotations

import pytest

from envoy.profile import (
    ProfileError,
    get_profile,
    list_profiles,
    remove_profile,
    set_profile,
)
from envoy.storage import save_manifest


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(store_dir, *projects):
    manifest = {p: f"{p}.env" for p in projects}
    save_manifest(store_dir, manifest)


def test_set_profile_persists(isolated_store):
    _seed(isolated_store, "alpha")
    set_profile("alpha", "dev", {"DEBUG": "1"}, store_dir=isolated_store)
    result = get_profile("alpha", "dev", store_dir=isolated_store)
    assert result == {"DEBUG": "1"}


def test_get_profile_missing_returns_none(isolated_store):
    _seed(isolated_store, "alpha")
    assert get_profile("alpha", "staging", store_dir=isolated_store) is None


def test_set_profile_missing_project_raises(isolated_store):
    with pytest.raises(ProfileError, match="not found"):
        set_profile("ghost", "dev", {}, store_dir=isolated_store)


def test_set_profile_empty_name_raises(isolated_store):
    _seed(isolated_store, "alpha")
    with pytest.raises(ProfileError, match="empty"):
        set_profile("alpha", "", {}, store_dir=isolated_store)


def test_set_profile_overwrites_existing(isolated_store):
    _seed(isolated_store, "alpha")
    set_profile("alpha", "dev", {"A": "1"}, store_dir=isolated_store)
    set_profile("alpha", "dev", {"A": "2", "B": "3"}, store_dir=isolated_store)
    assert get_profile("alpha", "dev", store_dir=isolated_store) == {"A": "2", "B": "3"}


def test_remove_profile_success(isolated_store):
    _seed(isolated_store, "alpha")
    set_profile("alpha", "dev", {"X": "1"}, store_dir=isolated_store)
    remove_profile("alpha", "dev", store_dir=isolated_store)
    assert get_profile("alpha", "dev", store_dir=isolated_store) is None


def test_remove_profile_missing_raises(isolated_store):
    _seed(isolated_store, "alpha")
    with pytest.raises(ProfileError, match="not found"):
        remove_profile("alpha", "nonexistent", store_dir=isolated_store)


def test_list_profiles_empty(isolated_store):
    _seed(isolated_store, "alpha")
    assert list_profiles("alpha", store_dir=isolated_store) == []


def test_list_profiles_multiple(isolated_store):
    _seed(isolated_store, "alpha")
    set_profile("alpha", "dev", {}, store_dir=isolated_store)
    set_profile("alpha", "prod", {}, store_dir=isolated_store)
    names = sorted(list_profiles("alpha", store_dir=isolated_store))
    assert names == ["dev", "prod"]


def test_list_profiles_isolated_per_project(isolated_store):
    _seed(isolated_store, "alpha", "beta")
    set_profile("alpha", "dev", {}, store_dir=isolated_store)
    set_profile("beta", "staging", {}, store_dir=isolated_store)
    assert list_profiles("alpha", store_dir=isolated_store) == ["dev"]
    assert list_profiles("beta", store_dir=isolated_store) == ["staging"]
