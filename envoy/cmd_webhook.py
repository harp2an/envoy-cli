"""CLI commands for managing webhooks."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.webhook import (
    WebhookError,
    register_webhook,
    remove_webhook,
    list_webhooks,
)


def cmd_webhook_add(args: Namespace) -> None:
    events = [e.strip() for e in args.events.split(",") if e.strip()]
    try:
        register_webhook(args.name, args.url, events)
        print(f"Webhook '{args.name}' registered for events: {events}")
    except WebhookError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_webhook_remove(args: Namespace) -> None:
    try:
        remove_webhook(args.name)
        print(f"Webhook '{args.name}' removed.")
    except WebhookError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_webhook_list(args: Namespace) -> None:
    hooks = list_webhooks()
    if not hooks:
        print("No webhooks registered.")
        return
    for h in hooks:
        events = ", ".join(h["events"]) or "(none)"
        print(f"  {h['name']:20s}  {h['url']}  [{events}]")


def register_webhook_parser(sub) -> None:
    p: ArgumentParser = sub.add_parser("webhook", help="Manage webhooks")
    ws = p.add_subparsers(dest="webhook_cmd", required=True)

    add_p = ws.add_parser("add", help="Register a webhook")
    add_p.add_argument("name", help="Webhook name")
    add_p.add_argument("url", help="Target URL")
    add_p.add_argument("--events", default="push,pull", help="Comma-separated event list")
    add_p.set_defaults(func=cmd_webhook_add)

    rm_p = ws.add_parser("remove", help="Remove a webhook")
    rm_p.add_argument("name", help="Webhook name")
    rm_p.set_defaults(func=cmd_webhook_remove)

    ls_p = ws.add_parser("list", help="List webhooks")
    ls_p.set_defaults(func=cmd_webhook_list)
