"""Tests for envoy.trigger."""
from __future__ import annotations

import pytest
from pathlib import Path

from envoy.trigger import (
    TriggerError,
    add_trigger,
    remove_trigger,
    list_triggers,
    fire_triggers,
)
from envoy.storage import save_manifest, load_manifest


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.trigger.get_store_dir", lambda: tmp_path)
    manifest = {"projects": {"alpha": {"file": "alpha.enc"}}}
    save_manifest(tmp_path, manifest)
    return tmp_path


def test_list_triggers_empty(isolated_store):
    assert list_triggers("alpha", store_dir=isolated_store) == []


def test_add_trigger_success(isolated_store):
    rule = add_trigger("alpha", "DB_*", "set", "log", "my-label", store_dir=isolated_store)
    assert rule["key_pattern"] == "DB_*"
    assert rule["event"] == "set"
    assert rule["action"] == "log"
    assert rule["action_target"] == "my-label"


def test_add_trigger_persists(isolated_store):
    add_trigger("alpha", "SECRET", "rotate", "webhook", "https://example.com", store_dir=isolated_store)
    rules = list_triggers("alpha", store_dir=isolated_store)
    assert len(rules) == 1
    assert rules[0]["key_pattern"] == "SECRET"


def test_add_trigger_invalid_event_raises(isolated_store):
    with pytest.raises(TriggerError, match="Unknown event"):
        add_trigger("alpha", "KEY", "update", "log", "lbl", store_dir=isolated_store)


def test_add_trigger_invalid_action_raises(isolated_store):
    with pytest.raises(TriggerError, match="Unknown action"):
        add_trigger("alpha", "KEY", "set", "email", "addr", store_dir=isolated_store)


def test_remove_trigger_success(isolated_store):
    add_trigger("alpha", "A", "set", "log", "l1", store_dir=isolated_store)
    add_trigger("alpha", "B", "delete", "log", "l2", store_dir=isolated_store)
    remove_trigger("alpha", 0, store_dir=isolated_store)
    rules = list_triggers("alpha", store_dir=isolated_store)
    assert len(rules) == 1
    assert rules[0]["key_pattern"] == "B"


def test_remove_trigger_out_of_range_raises(isolated_store):
    with pytest.raises(TriggerError, match="No trigger at index"):
        remove_trigger("alpha", 99, store_dir=isolated_store)


def test_fire_triggers_matches_glob(isolated_store):
    add_trigger("alpha", "DB_*", "set", "log", "lbl", store_dir=isolated_store)
    add_trigger("alpha", "SECRET", "set", "log", "lbl2", store_dir=isolated_store)
    matched = fire_triggers("alpha", "DB_HOST", "set", store_dir=isolated_store)
    assert len(matched) == 1
    assert matched[0]["key_pattern"] == "DB_*"


def test_fire_triggers_no_match(isolated_store):
    add_trigger("alpha", "DB_*", "set", "log", "lbl", store_dir=isolated_store)
    matched = fire_triggers("alpha", "DB_HOST", "delete", store_dir=isolated_store)
    assert matched == []


def test_multiple_projects_isolated(isolated_store):
    add_trigger("alpha", "X", "set", "log", "l", store_dir=isolated_store)
    assert list_triggers("beta", store_dir=isolated_store) == []
