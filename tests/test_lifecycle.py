"""Tests for envoy.lifecycle and envoy.cmd_lifecycle."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from envoy.lifecycle import (
    LifecycleError, set_state, get_state, list_states, remove_state, VALID_STATES
)


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.lifecycle.get_store_dir", lambda: tmp_path)
    manifest = {"alpha": "alpha.enc", "beta": "beta.enc"}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr("envoy.lifecycle.load_manifest", lambda d: manifest)
    return tmp_path


def test_set_state_persists(isolated_store):
    entry = set_state("alpha", "active", store_dir=isolated_store)
    assert entry["state"] == "active"
    assert "updated_at" in entry
    assert "created_at" in entry


def test_set_state_updates_file(isolated_store):
    set_state("alpha", "inactive", store_dir=isolated_store)
    data = json.loads((isolated_store / "lifecycle.json").read_text())
    assert data["alpha"]["state"] == "inactive"


def test_set_state_invalid_state_raises(isolated_store):
    with pytest.raises(LifecycleError, match="Invalid state"):
        set_state("alpha", "flying", store_dir=isolated_store)


def test_set_state_missing_project_raises(isolated_store):
    with pytest.raises(LifecycleError, match="not found"):
        set_state("nonexistent", "active", store_dir=isolated_store)


def test_get_state_returns_none_when_unset(isolated_store):
    result = get_state("alpha", store_dir=isolated_store)
    assert result is None


def test_get_state_returns_entry_after_set(isolated_store):
    set_state("beta", "deprecated", store_dir=isolated_store)
    result = get_state("beta", store_dir=isolated_store)
    assert result is not None
    assert result["state"] == "deprecated"


def test_list_states_empty(isolated_store):
    result = list_states(store_dir=isolated_store)
    assert result == {}


def test_list_states_multiple_projects(isolated_store):
    set_state("alpha", "active", store_dir=isolated_store)
    set_state("beta", "archived", store_dir=isolated_store)
    result = list_states(store_dir=isolated_store)
    assert result["alpha"]["state"] == "active"
    assert result["beta"]["state"] == "archived"


def test_remove_state_returns_true(isolated_store):
    set_state("alpha", "active", store_dir=isolated_store)
    assert remove_state("alpha", store_dir=isolated_store) is True


def test_remove_state_returns_false_when_missing(isolated_store):
    assert remove_state("alpha", store_dir=isolated_store) is False


def test_remove_state_deletes_entry(isolated_store):
    set_state("alpha", "active", store_dir=isolated_store)
    remove_state("alpha", store_dir=isolated_store)
    data = json.loads((isolated_store / "lifecycle.json").read_text())
    assert "alpha" not in data


def test_overwrite_state_preserves_created_at(isolated_store):
    set_state("alpha", "active", store_dir=isolated_store)
    first = get_state("alpha", store_dir=isolated_store)
    set_state("alpha", "inactive", store_dir=isolated_store)
    second = get_state("alpha", store_dir=isolated_store)
    assert second["created_at"] == first["created_at"]
    assert second["state"] == "inactive"


def test_valid_states_constant():
    assert "active" in VALID_STATES
    assert "archived" in VALID_STATES
    assert "deprecated" in VALID_STATES
    assert "inactive" in VALID_STATES
