"""Notification dispatch for envoy events."""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir


class NotifyError(Exception):
    pass


@dataclass
class NotifyRule:
    project: str
    event: str
    channel: str          # "webhook" | "stdout"
    target: str = ""      # URL for webhook, empty for stdout
    extra: dict = field(default_factory=dict)


def _notify_path(store_dir: Path | None = None) -> Path:
    return (store_dir or get_store_dir()) / "notify_rules.json"


def _load_rules(store_dir: Path | None = None) -> list[dict]:
    p = _notify_path(store_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_rules(rules: list[dict], store_dir: Path | None = None) -> None:
    _notify_path(store_dir).write_text(json.dumps(rules, indent=2))


VALID_CHANNELS = {"webhook", "stdout"}
VALID_EVENTS = {"push", "pull", "rotate", "snapshot", "restore", "delete"}


def add_rule(
    project: str,
    event: str,
    channel: str,
    target: str = "",
    store_dir: Path | None = None,
) -> NotifyRule:
    if event not in VALID_EVENTS:
        raise NotifyError(f"Unknown event '{event}'. Valid: {sorted(VALID_EVENTS)}")
    if channel not in VALID_CHANNELS:
        raise NotifyError(f"Unknown channel '{channel}'. Valid: {sorted(VALID_CHANNELS)}")
    if channel == "webhook" and not target.startswith(("http://", "https://")):
        raise NotifyError("Webhook target must be a valid http/https URL.")
    rules = _load_rules(store_dir)
    rules.append({"project": project, "event": event, "channel": channel, "target": target})
    _save_rules(rules, store_dir)
    return NotifyRule(project=project, event=event, channel=channel, target=target)


def remove_rule(
    project: str, event: str, store_dir: Path | None = None
) -> None:
    rules = _load_rules(store_dir)
    new_rules = [r for r in rules if not (r["project"] == project and r["event"] == event)]
    if len(new_rules) == len(rules):
        raise NotifyError(f"No rule found for project '{project}' event '{event}'.")
    _save_rules(new_rules, store_dir)


def list_rules(
    project: str | None = None, store_dir: Path | None = None
) -> list[NotifyRule]:
    rules = _load_rules(store_dir)
    result = []
    for r in rules:
        if project is None or r["project"] == project:
            result.append(NotifyRule(**{k: v for k, v in r.items() if k in NotifyRule.__dataclass_fields__}))
    return result


def dispatch(
    project: str, event: str, payload: dict[str, Any] | None = None, store_dir: Path | None = None
) -> list[str]:
    """Fire all matching rules; return list of dispatched channel descriptions."""
    rules = list_rules(project, store_dir)
    dispatched: list[str] = []
    for rule in rules:
        if rule.event != event:
            continue
        if rule.channel == "stdout":
            print(f"[envoy notify] {project} {event}: {payload}")
            dispatched.append("stdout")
        elif rule.channel == "webhook":
            body = json.dumps({"project": project, "event": event, "payload": payload or {}}).encode()
            req = urllib.request.Request(
                rule.target,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                urllib.request.urlopen(req, timeout=5)
            except Exception as exc:
                raise NotifyError(f"Webhook delivery failed: {exc}") from exc
            dispatched.append(f"webhook:{rule.target}")
    return dispatched
