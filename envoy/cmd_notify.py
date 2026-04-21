"""CLI commands for notification rules."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.notify import NotifyError, add_rule, list_rules, remove_rule


def cmd_notify_add(args: Namespace) -> None:
    try:
        rule = add_rule(
            project=args.project,
            event=args.event,
            channel=args.channel,
            target=getattr(args, "target", "") or "",
        )
        print(f"Added rule: {rule.project} / {rule.event} -> {rule.channel} {rule.target}".strip())
    except NotifyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_notify_remove(args: Namespace) -> None:
    try:
        remove_rule(project=args.project, event=args.event)
        print(f"Removed rule for '{args.project}' event '{args.event}'.")
    except NotifyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_notify_list(args: Namespace) -> None:
    project = getattr(args, "project", None)
    rules = list_rules(project=project)
    if not rules:
        print("No notification rules.")
        return
    for r in rules:
        target_str = f" -> {r.target}" if r.target else ""
        print(f"  {r.project:20s}  {r.event:12s}  {r.channel}{target_str}")


def register_notify_parser(subparsers) -> None:
    p = subparsers.add_parser("notify", help="Manage notification rules")
    sub = p.add_subparsers(dest="notify_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a notification rule")
    add_p.add_argument("project")
    add_p.add_argument("event", choices=["push", "pull", "rotate", "snapshot", "restore", "delete"])
    add_p.add_argument("channel", choices=["webhook", "stdout"])
    add_p.add_argument("--target", default="", help="Webhook URL (required for webhook channel)")
    add_p.set_defaults(func=cmd_notify_add)

    rm_p = sub.add_parser("remove", help="Remove a notification rule")
    rm_p.add_argument("project")
    rm_p.add_argument("event")
    rm_p.set_defaults(func=cmd_notify_remove)

    ls_p = sub.add_parser("list", help="List notification rules")
    ls_p.add_argument("--project", default=None)
    ls_p.set_defaults(func=cmd_notify_list)
