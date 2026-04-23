"""CLI commands for managing trigger rules."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, _SubParsersAction

from envoy.trigger import TriggerError, add_trigger, remove_trigger, list_triggers


def cmd_trigger_add(args) -> None:
    try:
        rule = add_trigger(
            project=args.project,
            key_pattern=args.key_pattern,
            event=args.event,
            action=args.action,
            action_target=args.target,
        )
        print(
            f"Trigger added for '{args.project}': "
            f"on {rule['event']} of '{rule['key_pattern']}' -> "
            f"{rule['action']}:{rule['action_target']}"
        )
    except TriggerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_trigger_remove(args) -> None:
    try:
        remove_trigger(project=args.project, index=args.index)
        print(f"Trigger {args.index} removed from '{args.project}'.")
    except TriggerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_trigger_list(args) -> None:
    rules = list_triggers(project=args.project)
    if not rules:
        print(f"No triggers for '{args.project}'.")
        return
    for i, rule in enumerate(rules):
        print(
            f"[{i}] event={rule['event']} key_pattern={rule['key_pattern']} "
            f"action={rule['action']} target={rule['action_target']}"
        )


def register_trigger_parser(subparsers: _SubParsersAction) -> None:
    p: ArgumentParser = subparsers.add_parser("trigger", help="Manage trigger rules")
    sub = p.add_subparsers(dest="trigger_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a trigger rule")
    add_p.add_argument("project")
    add_p.add_argument("key_pattern", help="Key pattern (supports globs, e.g. DB_*)")
    add_p.add_argument("event", choices=["set", "delete", "rotate"])
    add_p.add_argument("action", choices=["log", "webhook", "export"])
    add_p.add_argument("target", help="Action target (URL for webhook, path for export, label for log)")
    add_p.set_defaults(func=cmd_trigger_add)

    rm_p = sub.add_parser("remove", help="Remove a trigger rule by index")
    rm_p.add_argument("project")
    rm_p.add_argument("index", type=int)
    rm_p.set_defaults(func=cmd_trigger_remove)

    ls_p = sub.add_parser("list", help="List trigger rules for a project")
    ls_p.add_argument("project")
    ls_p.set_defaults(func=cmd_trigger_list)
