"""Tests for envoy.history."""
from __future__ import annotations

import pytest
from unittest.mock import patch

from envoy.history import (
    record_version, list_versions, get_version, clear_history, HistoryError
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.history.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.audit.get_audit_path", lambda: tmp_path / "audit.jsonl")
    return tmp_path


def test_list_versions_empty(isolated_store):
    assert list_versions("myproject") == []


def test_record_and_list(isolated_store):
    record_version("myproject", "cipher1", label="v1")
    record_version("myproject", "cipher2")
    entries = list_versions("myproject")
    assert len(entries) == 2
    assert entries[0]["ciphertext"] == "cipher1"
    assert entries[0]["label"] == "v1"
    assert entries[1]["ciphertext"] == "cipher2"


def test_get_version(isolated_store):
    record_version("proj", "aaa")
    record_version("proj", "bbb")
    assert get_version("proj", 0) == "aaa"
    assert get_version("proj", 1) == "bbb"


def test_get_version_no_history_raises(isolated_store):
    with pytest.raises(HistoryError):
        get_version("ghost", 0)


def test_get_version_out_of_range_raises(isolated_store):
    record_version("proj", "x")
    with pytest.raises(HistoryError):
        get_version("proj", 99)


def test_history_capped_at_max(isolated_store):
    for i in range(15):
        record_version("proj", f"c{i}")
    entries = list_versions("proj")
    assert len(entries) == 10
    assert entries[0]["ciphertext"] == "c5"


def test_clear_history(isolated_store):
    record_version("proj", "x")
    clear_history("proj")
    assert list_versions("proj") == []
