"""CLI sub-commands for audit log management."""

import argparse
from envoy.audit import load_events, clear_events
from envoy.storage import get_store_dir


def cmd_audit_list(args: argparse.Namespace) -> None:
    store_dir = get_store_dir()
    events = load_events(store_dir)
    if not events:
        print("No audit events recorded.")
        return
    project_filter = getattr(args, "project", None)
    for e in events:
        if project_filter and e["project"] != project_filter:
            continue
        remote = f" -> {e['remote']}" if e["remote"] else ""
        details = f" ({e['details']})" if e["details"] else ""
        print(f"[{e['timestamp']}] {e['action'].upper():6s} {e['project']}{remote}{details}")


def cmd_audit_clear(args: argparse.Namespace) -> None:
    store_dir = get_store_dir()
    clear_events(store_dir)
    print("Audit log cleared.")


def register_audit_parser(subparsers: argparse._SubParsersAction) -> None:
    audit_parser = subparsers.add_parser("audit", help="Manage the audit log")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd", required=True)

    ls_parser = audit_sub.add_parser("list", help="List audit events")
    ls_parser.add_argument(
        "--project", "-p", default=None, help="Filter events by project name"
    )
    ls_parser.set_defaults(func=cmd_audit_list)

    clear_parser = audit_sub.add_parser("clear", help="Clear all audit events")
    clear_parser.set_defaults(func=cmd_audit_clear)
