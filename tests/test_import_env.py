"""Tests for envoy.import_env."""

import pytest
from pathlib import Path

from envoy.import_env import import_dotenv_file, ImportError as EnvImportError
from envoy.storage import load_env, get_store_dir
from envoy.audit import load_events, get_audit_path


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setenv("ENVOY_AUDIT_PATH", str(tmp_path / "audit.jsonl"))
    yield tmp_path


def _write_env(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_import_simple_file(isolated_store):
    fp = _write_env(isolated_store, ".env", "FOO=bar\nBAZ=qux\n")
    count = import_dotenv_file("myproject", fp, "secret")
    assert count == 2


def test_import_stores_content(isolated_store):
    fp = _write_env(isolated_store, ".env", "KEY=value\n")
    import_dotenv_file("proj", fp, "pass")
    content = load_env("proj", "pass")
    assert "KEY=value" in content


def test_import_missing_file_raises(isolated_store):
    with pytest.raises(EnvImportError, match="not found"):
        import_dotenv_file("proj", "/nonexistent/.env", "pass")


def test_import_invalid_content_raises(isolated_store):
    fp = _write_env(isolated_store, "bad.env", "NOTVALID\n")
    with pytest.raises(EnvImportError, match="Parse error"):
        import_dotenv_file("proj", fp, "pass")


def test_import_records_audit(isolated_store):
    fp = _write_env(isolated_store, ".env", "A=1\nB=2\n")
    import_dotenv_file("auditproj", fp, "pw")
    events = load_events()
    assert any(e["action"] == "import" and e["project"] == "auditproj" for e in events)


def test_import_audit_has_key_count(isolated_store):
    fp = _write_env(isolated_store, ".env", "X=1\nY=2\nZ=3\n")
    import_dotenv_file("proj2", fp, "pw")
    events = load_events()
    ev = next(e for e in events if e["project"] == "proj2")
    assert ev["meta"]["keys"] == 3
