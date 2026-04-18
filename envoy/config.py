"""User configuration management for envoy-cli."""

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "envoy" / "config.json"

DEFAULT_CONFIG = {
    "remote_url": None,
    "default_project": None,
    "store_dir": None,
}


def get_config_path() -> Path:
    return Path(os.environ.get("ENVOY_CONFIG", DEFAULT_CONFIG_PATH))


def load_config() -> dict:
    path = get_config_path()
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    with open(path) as f:
        data = json.load(f)
    return {**DEFAULT_CONFIG, **data}


def save_config(config: dict) -> None:
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def get_config_value(key: str) -> Optional[str]:
    return load_config().get(key)


def set_config_value(key: str, value: str) -> None:
    if key not in DEFAULT_CONFIG:
        raise KeyError(f"Unknown config key: {key!r}")
    config = load_config()
    config[key] = value
    save_config(config)


def unset_config_value(key: str) -> None:
    if key not in DEFAULT_CONFIG:
        raise KeyError(f"Unknown config key: {key!r}")
    config = load_config()
    config[key] = None
    save_config(config)
