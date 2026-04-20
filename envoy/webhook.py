"""Webhook notification support for envoy events."""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any

from envoy.storage import get_store_dir

_WEBHOOK_FILE = "webhooks.json"


class WebhookError(Exception):
    pass


def _webhook_path(store_dir: str | None = None) -> str:
    base = store_dir or get_store_dir()
    import os
    return os.path.join(base, _WEBHOOK_FILE)


def _load_webhooks(store_dir: str | None = None) -> dict:
    import os
    path = _webhook_path(store_dir)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _save_webhooks(data: dict, store_dir: str | None = None) -> None:
    with open(_webhook_path(store_dir), "w") as f:
        json.dump(data, f, indent=2)


def register_webhook(name: str, url: str, events: list[str], store_dir: str | None = None) -> None:
    """Register a named webhook for given event types."""
    if not url.startswith(("http://", "https://")):
        raise WebhookError(f"Invalid URL: {url!r}")
    data = _load_webhooks(store_dir)
    data[name] = {"url": url, "events": events}
    _save_webhooks(data, store_dir)


def remove_webhook(name: str, store_dir: str | None = None) -> None:
    data = _load_webhooks(store_dir)
    if name not in data:
        raise WebhookError(f"Webhook not found: {name!r}")
    del data[name]
    _save_webhooks(data, store_dir)


def list_webhooks(store_dir: str | None = None) -> list[dict]:
    data = _load_webhooks(store_dir)
    return [{"name": k, **v} for k, v in data.items()]


def dispatch_event(event: str, payload: dict[str, Any], store_dir: str | None = None) -> list[str]:
    """Fire all webhooks subscribed to *event*. Returns list of failed names."""
    data = _load_webhooks(store_dir)
    failed: list[str] = []
    body = json.dumps({"event": event, **payload}).encode()
    for name, cfg in data.items():
        if event not in cfg.get("events", []):
            continue
        req = urllib.request.Request(
            cfg["url"],
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5):
                pass
        except (urllib.error.URLError, OSError):
            failed.append(name)
    return failed
