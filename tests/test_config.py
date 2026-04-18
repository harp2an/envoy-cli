"""Tests for envoy.config module."""

import json
import pytest
from pathlib import Path

import envoy.config as cfg


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    monkeypatch.setenv("ENVOY_CONFIG", str(config_file))
    yield config_file


def test_load_config_defaults_when_no_file():
    config = cfg.load_config()
    assert config["remote_url"] is None
    assert config["default_project"] is None
    assert config["store_dir"] is None


def test_set_and_get_config_value():
    cfg.set_config_value("remote_url", "https://example.com")
    assert cfg.get_config_value("remote_url") == "https://example.com"


def test_set_unknown_key_raises():
    with pytest.raises(KeyError, match="Unknown config key"):
        cfg.set_config_value("nonexistent", "value")


def test_unset_config_value():
    cfg.set_config_value("default_project", "myapp")
    cfg.unset_config_value("default_project")
    assert cfg.get_config_value("default_project") is None


def test_unset_unknown_key_raises():
    with pytest.raises(KeyError):
        cfg.unset_config_value("bad_key")


def test_save_creates_parent_dirs(tmp_path, monkeypatch):
    nested = tmp_path / "a" / "b" / "config.json"
    monkeypatch.setenv("ENVOY_CONFIG", str(nested))
    cfg.set_config_value("remote_url", "http://x.com")
    assert nested.exists()


def test_existing_file_merged_with_defaults(isolated_config):
    isolated_config.parent.mkdir(parents=True, exist_ok=True)
    isolated_config.write_text(json.dumps({"remote_url": "http://stored.com"}))
    config = cfg.load_config()
    assert config["remote_url"] == "http://stored.com"
    assert config["default_project"] is None
