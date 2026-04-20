"""Integration tests for pin + storage interaction."""
import pytest
from pathlib import Path

from envoy.storage import store_env, load_manifest
from envoy.pin import pin_project, unpin_project, get_pin, list_pins, PinError


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(store_dir, name, password="pw", content="KEY=val"):
    store_env(name, content, password, store_dir=str(store_dir))


def test_pin_and_retrieve(isolated_store):
    _seed(isolated_store, "alpha")
    pin_project("alpha", "v1.0", store_dir=str(isolated_store))
    entry = get_pin("alpha", store_dir=str(isolated_store))
    assert entry is not None
    assert entry["version"] == "v1.0"
    assert "pinned_at" in entry


def test_pin_overwrite(isolated_store):
    _seed(isolated_store, "alpha")
    pin_project("alpha", "v1.0", store_dir=str(isolated_store))
    pin_project("alpha", "v2.0", store_dir=str(isolated_store))
    entry = get_pin("alpha", store_dir=str(isolated_store))
    assert entry["version"] == "v2.0"


def test_unpin_removes_entry(isolated_store):
    _seed(isolated_store, "alpha")
    pin_project("alpha", "v1.0", store_dir=str(isolated_store))
    unpin_project("alpha", store_dir=str(isolated_store))
    assert get_pin("alpha", store_dir=str(isolated_store)) is None


def test_unpin_not_pinned_raises(isolated_store):
    _seed(isolated_store, "alpha")
    with pytest.raises(PinError, match="not pinned"):
        unpin_project("alpha", store_dir=str(isolated_store))


def test_list_pins_multiple(isolated_store):
    _seed(isolated_store, "alpha")
    _seed(isolated_store, "beta")
    pin_project("alpha", "v1", store_dir=str(isolated_store))
    pin_project("beta", "v3", store_dir=str(isolated_store))
    pins = list_pins(store_dir=str(isolated_store))
    assert "alpha" in pins
    assert "beta" in pins
    assert pins["alpha"]["version"] == "v1"
    assert pins["beta"]["version"] == "v3"


def test_pin_missing_project_raises(isolated_store):
    with pytest.raises(PinError, match="not found"):
        pin_project("ghost", "v1", store_dir=str(isolated_store))
