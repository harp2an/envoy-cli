"""Integration: rotation events are recorded in audit log."""

import pytest

from envoy.audit import load_events
from envoy.rotate import rotate_project
from envoy.storage import store_env


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    monkeypatch.setenv("ENVOY_AUDIT_PATH", str(tmp_path / "audit.jsonl"))
    return tmp_path


def test_rotate_via_cmd_records_audit(monkeypatch):
    import argparse
    from envoy.cmd_rotate import cmd_rotate

    store_env("svc", "TOKEN=xyz", "old")
    monkeypatch.setattr(
        "getpass.getpass",
        lambda prompt: {"Current password: ": "old", "New password: ": "new", "Confirm new password: ": "new"}.get(prompt, "new"),
    )
    args = argparse.Namespace(project="svc")
    cmd_rotate(args)

    events = load_events()
    assert any(e["action"] == "rotate" and e["project"] == "svc" for e in events)


def test_rotate_all_via_cmd_records_all(monkeypatch):
    import argparse
    from envoy.cmd_rotate import cmd_rotate

    store_env("a", "X=1", "pass")
    store_env("b", "Y=2", "pass")
    monkeypatch.setattr(
        "getpass.getpass",
        lambda prompt: {"Current password: ": "pass", "New password: ": "np", "Confirm new password: ": "np"}.get(prompt, "np"),
    )
    args = argparse.Namespace(project=None)
    cmd_rotate(args)

    events = load_events()
    projects = {e["project"] for e in events if e["action"] == "rotate"}
    assert "a" in projects
    assert "b" in projects
