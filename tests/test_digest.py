"""Tests for envoy.digest."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envoy.storage import save_manifest
from envoy.digest import (
    DigestError,
    generate_digest,
    list_digests,
    verify_digest,
    clear_digests,
    _digest_path,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage._STORE_DIR", None)
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    manifest = {"alpha": {"file": "alpha.env.enc", "tags": []}}
    save_manifest(tmp_path, manifest)
    return tmp_path


def test_generate_digest_returns_record(isolated_store):
    rec = generate_digest(isolated_store, "alpha")
    assert "fingerprint" in rec
    assert "generated_at" in rec
    assert len(rec["fingerprint"]) == 64  # sha256 hex


def test_generate_digest_persists(isolated_store):
    generate_digest(isolated_store, "alpha", note="first")
    records = list_digests(isolated_store, "alpha")
    assert len(records) == 1
    assert records[0]["note"] == "first"


def test_multiple_digests_appended(isolated_store):
    generate_digest(isolated_store, "alpha")
    generate_digest(isolated_store, "alpha")
    records = list_digests(isolated_store, "alpha")
    assert len(records) == 2


def test_list_digests_empty_when_none(isolated_store):
    records = list_digests(isolated_store, "alpha")
    assert records == []


def test_generate_digest_missing_project_raises(isolated_store):
    with pytest.raises(DigestError, match="not found"):
        generate_digest(isolated_store, "ghost")


def test_verify_digest_matches(isolated_store):
    generate_digest(isolated_store, "alpha")
    assert verify_digest(isolated_store, "alpha") is True


def test_verify_digest_detects_change(isolated_store):
    generate_digest(isolated_store, "alpha")
    # Mutate the manifest to simulate a change
    manifest = {"alpha": {"file": "alpha.env.enc", "tags": ["changed"]}}
    save_manifest(isolated_store, manifest)
    assert verify_digest(isolated_store, "alpha") is False


def test_verify_digest_no_digests_raises(isolated_store):
    with pytest.raises(DigestError, match="No digests"):
        verify_digest(isolated_store, "alpha")


def test_verify_digest_by_index(isolated_store):
    generate_digest(isolated_store, "alpha")
    generate_digest(isolated_store, "alpha")
    assert verify_digest(isolated_store, "alpha", index=0) is True


def test_clear_digests_removes_all(isolated_store):
    generate_digest(isolated_store, "alpha")
    generate_digest(isolated_store, "alpha")
    clear_digests(isolated_store, "alpha")
    assert list_digests(isolated_store, "alpha") == []


def test_clear_digests_nonexistent_project_is_noop(isolated_store):
    clear_digests(isolated_store, "ghost")  # should not raise
    assert list_digests(isolated_store, "ghost") == []


def test_digests_file_created(isolated_store):
    generate_digest(isolated_store, "alpha")
    assert _digest_path(isolated_store).exists()
