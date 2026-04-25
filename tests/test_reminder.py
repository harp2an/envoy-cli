"""Tests for envoy.reminder."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from envoy.storage import save_manifest
from envoy.reminder import (
    ReminderError,
    set_reminder,
    get_reminder,
    remove_reminder,
    list_reminders,
    due_soon,
)


@pytest.fixture()
def isolated_store(tmp_path):
    manifest = {"alpha": "alpha.enc", "beta": "beta.enc"}
    save_manifest(tmp_path, manifest)
    return tmp_path


def test_set_reminder_returns_due_date(isolated_store):
    due = set_reminder("alpha", "Check configs", 3, store_dir=isolated_store)
    expected = (datetime.utcnow() + timedelta(days=3)).date().isoformat()
    assert due == expected


def test_set_reminder_persists(isolated_store):
    set_reminder("alpha", "Rotate keys", 5, store_dir=isolated_store)
    r = get_reminder("alpha", store_dir=isolated_store)
    assert r is not None
    assert r["message"] == "Rotate keys"
    assert "due" in r
    assert "created" in r


def test_set_reminder_missing_project_raises(isolated_store):
    with pytest.raises(ReminderError, match="not found"):
        set_reminder("ghost", "hello", 1, store_dir=isolated_store)


def test_set_reminder_zero_days_raises(isolated_store):
    with pytest.raises(ReminderError, match="positive"):
        set_reminder("alpha", "msg", 0, store_dir=isolated_store)


def test_set_reminder_empty_message_raises(isolated_store):
    with pytest.raises(ReminderError, match="empty"):
        set_reminder("alpha", "   ", 2, store_dir=isolated_store)


def test_get_reminder_missing_returns_none(isolated_store):
    assert get_reminder("alpha", store_dir=isolated_store) is None


def test_remove_reminder_success(isolated_store):
    set_reminder("beta", "Sync remote", 4, store_dir=isolated_store)
    remove_reminder("beta", store_dir=isolated_store)
    assert get_reminder("beta", store_dir=isolated_store) is None


def test_remove_reminder_missing_raises(isolated_store):
    with pytest.raises(ReminderError, match="No reminder"):
        remove_reminder("alpha", store_dir=isolated_store)


def test_list_reminders_sorted_by_due(isolated_store):
    set_reminder("beta", "Later", 10, store_dir=isolated_store)
    set_reminder("alpha", "Sooner", 2, store_dir=isolated_store)
    rows = list_reminders(store_dir=isolated_store)
    assert rows[0]["project"] == "alpha"
    assert rows[1]["project"] == "beta"


def test_list_reminders_empty(isolated_store):
    assert list_reminders(store_dir=isolated_store) == []


def test_due_soon_returns_matching(isolated_store):
    set_reminder("alpha", "Near", 3, store_dir=isolated_store)
    set_reminder("beta", "Far", 30, store_dir=isolated_store)
    soon = due_soon(days=7, store_dir=isolated_store)
    projects = [r["project"] for r in soon]
    assert "alpha" in projects
    assert "beta" not in projects


def test_set_reminder_overwrites_existing(isolated_store):
    set_reminder("alpha", "First", 5, store_dir=isolated_store)
    set_reminder("alpha", "Second", 10, store_dir=isolated_store)
    r = get_reminder("alpha", store_dir=isolated_store)
    assert r["message"] == "Second"
