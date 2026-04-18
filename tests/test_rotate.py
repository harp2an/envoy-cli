"""Tests for envoy.rotate."""

import pytest

from envoy.rotate import RotationError, rotate_all, rotate_project
from envoy.storage import load_env, store_env


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def test_rotate_project_roundtrip():
    store_env("myapp", "KEY=value\nSECRET=abc", "oldpass")
    rotate_project("myapp", "oldpass", "newpass")
    result = load_env("myapp", "newpass")
    assert result == "KEY=value\nSECRET=abc"


def test_rotate_project_old_password_fails():
    store_env("myapp", "KEY=value", "oldpass")
    rotate_project("myapp", "oldpass", "newpass")
    with pytest.raises(Exception):
        load_env("myapp", "oldpass")


def test_rotate_project_wrong_old_password_raises():
    store_env("myapp", "KEY=value", "correctpass")
    with pytest.raises(RotationError, match="old password"):
        rotate_project("myapp", "wrongpass", "newpass")


def test_rotate_all_empty():
    result = rotate_all("old", "new")
    assert result == []


def test_rotate_all_multiple_projects():
    store_env("app1", "A=1", "pass")
    store_env("app2", "B=2", "pass")
    rotated = rotate_all("pass", "newpass")
    assert set(rotated) == {"app1", "app2"}
    assert load_env("app1", "newpass") == "A=1"
    assert load_env("app2", "newpass") == "B=2"


def test_rotate_all_partial_failure_raises():
    store_env("ok", "X=1", "pass")
    store_env("bad", "Y=2", "otherpass")
    with pytest.raises(RotationError, match="failed rotation"):
        rotate_all("pass", "newpass")
