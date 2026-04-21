"""Tests for envoy.badge."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envoy.badge import (
    BadgeError,
    generate_badge,
    get_badge,
    list_badges,
    remove_badge,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    """Patch get_store_dir and pre-populate a minimal manifest."""
    import envoy.storage as storage
    import envoy.badge as badge_mod

    monkeypatch.setattr(storage, "get_store_dir", lambda: tmp_path)
    monkeypatch.setattr(badge_mod, "get_store_dir", lambda: tmp_path)

    manifest = {
        "alpha": {"keys": 5, "updated": "2024-01-01T00:00:00"},
        "beta": {"keys": 3, "updated": "2024-02-01T00:00:00"},
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    return tmp_path


def test_generate_badge_returns_dict(isolated_store):
    badge = generate_badge("alpha", isolated_store)
    assert badge["project"] == "alpha"
    assert badge["status"] == "ok"
    assert badge["keys"] == 5


def test_generate_badge_persists(isolated_store):
    generate_badge("alpha", isolated_store)
    stored = json.loads((isolated_store / "badges.json").read_text())
    assert "alpha" in stored


def test_generate_badge_missing_project_raises(isolated_store):
    with pytest.raises(BadgeError, match="not found"):
        generate_badge("nonexistent", isolated_store)


def test_get_badge_returns_none_when_missing(isolated_store):
    assert get_badge("alpha", isolated_store) is None


def test_get_badge_returns_stored(isolated_store):
    generate_badge("alpha", isolated_store)
    badge = get_badge("alpha", isolated_store)
    assert badge is not None
    assert badge["project"] == "alpha"


def test_list_badges_empty(isolated_store):
    assert list_badges(isolated_store) == []


def test_list_badges_multiple(isolated_store):
    generate_badge("alpha", isolated_store)
    generate_badge("beta", isolated_store)
    badges = list_badges(isolated_store)
    assert len(badges) == 2
    projects = {b["project"] for b in badges}
    assert projects == {"alpha", "beta"}


def test_remove_badge_success(isolated_store):
    generate_badge("alpha", isolated_store)
    remove_badge("alpha", isolated_store)
    assert get_badge("alpha", isolated_store) is None


def test_remove_badge_missing_raises(isolated_store):
    with pytest.raises(BadgeError, match="No badge found"):
        remove_badge("alpha", isolated_store)


def test_generate_badge_overwrites_existing(isolated_store):
    generate_badge("alpha", isolated_store)
    badge = generate_badge("alpha", isolated_store)
    assert badge["keys"] == 5
    badges = list_badges(isolated_store)
    assert len(badges) == 1
