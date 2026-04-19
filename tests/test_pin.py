"""Tests for envoy.pin."""

import pytest
from unittest.mock import patch
from pathlib import Path
import json
import tempfile
import os

import envoy.pin as pin_mod
from envoy.pin import pin_project, unpin_project, get_pin, list_pins, PinError


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(pin_mod, "_pin_path", lambda: tmp_path / "pins.json")
    yield tmp_path


def test_pin_project_creates_entry():
    pin_project("alpha", "v1")
    assert get_pin("alpha") == "v1"


def test_pin_project_overwrites_existing():
    pin_project("alpha", "v1")
    pin_project("alpha", "v2")
    assert get_pin("alpha") == "v2"


def test_get_pin_missing_returns_none():
    assert get_pin("ghost") is None


def test_list_pins_empty():
    assert list_pins() == {}


def test_list_pins_multiple():
    pin_project("a", "snap-1")
    pin_project("b", "snap-2")
    result = list_pins()
    assert result == {"a": "snap-1", "b": "snap-2"}


def test_unpin_project_removes_entry():
    pin_project("alpha", "v1")
    unpin_project("alpha")
    assert get_pin("alpha") is None


def test_unpin_missing_project_raises():
    with pytest.raises(PinError, match="not pinned"):
        unpin_project("nonexistent")


def test_pin_empty_project_raises():
    with pytest.raises(PinError, match="Project name"):
        pin_project("", "v1")


def test_pin_empty_label_raises():
    with pytest.raises(PinError, match="Label"):
        pin_project("alpha", "")
