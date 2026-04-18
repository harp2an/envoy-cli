"""Tests for envoy.audit module."""

import pytest
import os
from envoy.audit import record_event, load_events, clear_events, get_audit_path


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_load_events_empty_when_no_file(store):
    assert load_events(store) == []


def test_record_event_creates_file(store):
    record_event(store, "push", "myproject", remote="https://example.com")
    assert os.path.exists(get_audit_path(store))


def test_record_event_fields(store):
    record_event(store, "pull", "alpha", remote="https://r.io", details="ok")
    events = load_events(store)
    assert len(events) == 1
    e = events[0]
    assert e["action"] == "pull"
    assert e["project"] == "alpha"
    assert e["remote"] == "https://r.io"
    assert e["details"] == "ok"
    assert "timestamp" in e


def test_multiple_events_appended(store):
    record_event(store, "push", "p1")
    record_event(store, "pull", "p2")
    record_event(store, "push", "p3")
    events = load_events(store)
    assert len(events) == 3
    assert events[0]["project"] == "p1"
    assert events[2]["project"] == "p3"


def test_clear_events_removes_file(store):
    record_event(store, "push", "x")
    clear_events(store)
    assert not os.path.exists(get_audit_path(store))


def test_clear_events_no_file_ok(store):
    # Should not raise if file doesn't exist
    clear_events(store)


def test_load_events_returns_dicts(store):
    record_event(store, "push", "proj", remote="http://host")
    events = load_events(store)
    assert isinstance(events[0], dict)
