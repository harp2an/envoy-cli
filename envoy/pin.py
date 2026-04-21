"""Pin a project to a specific snapshot or version label."""

from __future__ import annotations

import json
from pathlib import Path
from envoy.storage import get_store_dir

PIN_FILE = "pins.json"


class PinError(Exception):
    pass


def _pin_path() -> Path:
    return get_store_dir() / PIN_FILE


def _load_pins() -> dict:
    p = _pin_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise PinError(f"Pin file is corrupt and could not be parsed: {exc}") from exc


def _save_pins(pins: dict) -> None:
    _pin_path().write_text(json.dumps(pins, indent=2))


def pin_project(project: str, label: str) -> None:
    """Pin *project* to *label* (snapshot tag or version id)."""
    if not project:
        raise PinError("Project name must not be empty.")
    if not label:
        raise PinError("Label must not be empty.")
    pins = _load_pins()
    pins[project] = label
    _save_pins(pins)


def unpin_project(project: str) -> None:
    """Remove the pin for *project*."""
    pins = _load_pins()
    if project not in pins:
        raise PinError(f"Project '{project}' is not pinned.")
    del pins[project]
    _save_pins(pins)


def get_pin(project: str) -> str | None:
    """Return the label pinned to *project*, or None."""
    return _load_pins().get(project)


def list_pins() -> dict:
    """Return all pinned projects as {project: label}."""
    return _load_pins()
