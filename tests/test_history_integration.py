"""Integration tests: history records real encrypted values."""
from __future__ import annotations

import pytest

from envoy.crypto import encrypt, decrypt
from envoy.history import record_version, get_version, list_versions


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.history.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.audit.get_audit_path", lambda: tmp_path / "audit.jsonl")
    return tmp_path


def test_record_and_decrypt_roundtrip(isolated_store):
    password = "s3cret"
    plaintext = "KEY=value\nOTHER=123"
    cipher = encrypt(plaintext, password)
    record_version("proj", cipher, label="initial")

    stored = get_version("proj", 0)
    assert decrypt(stored, password) == plaintext


def test_multiple_versions_independent(isolated_store):
    pw = "pass"
    c1 = encrypt("A=1", pw)
    c2 = encrypt("A=2", pw)
    record_version("proj", c1, label="v1")
    record_version("proj", c2, label="v2")

    assert decrypt(get_version("proj", 0), pw) == "A=1"
    assert decrypt(get_version("proj", 1), pw) == "A=2"


def test_versions_isolated_per_project(isolated_store):
    pw = "pw"
    record_version("alpha", encrypt("X=1", pw))
    record_version("beta", encrypt("Y=2", pw))

    assert len(list_versions("alpha")) == 1
    assert len(list_versions("beta")) == 1
    assert decrypt(get_version("alpha", 0), pw) == "X=1"
    assert decrypt(get_version("beta", 0), pw) == "Y=2"
