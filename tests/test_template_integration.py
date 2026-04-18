"""Integration: render template and store as a project, then load it back."""

import pytest
from unittest.mock import patch

from envoy.template import render_template
from envoy.storage import store_env, load_env


TEMPLATE = (
    "DB_HOST={{ DB_HOST }}\n"
    "DB_PORT={{ DB_PORT }}\n"
    "SECRET={{ SECRET }}\n"
)

VARS = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "s3cr3t"}
PASSWORD = "integration-pass"


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def test_render_and_store_roundtrip(isolated_store):
    rendered = render_template(TEMPLATE, VARS)
    store_env("myproject", rendered, PASSWORD)
    recovered = load_env("myproject", PASSWORD)
    assert "DB_HOST=localhost" in recovered
    assert "SECRET=s3cr3t" in recovered


def test_render_preserves_all_keys(isolated_store):
    rendered = render_template(TEMPLATE, VARS)
    for key, val in VARS.items():
        assert f"{key}={val}" in rendered


def test_render_and_store_wrong_password_raises(isolated_store):
    from envoy.crypto import DecryptionError  # may be ValueError
    rendered = render_template(TEMPLATE, VARS)
    store_env("proj2", rendered, PASSWORD)
    with pytest.raises(Exception):
        load_env("proj2", "wrong-password")
