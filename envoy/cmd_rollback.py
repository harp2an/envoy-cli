"""CLI sub-commands for rollback."""

from __future__ import annotations

import sys
from getpass import getpass

from envoy.rollback import RollbackError, rollback_to_version, list_rollback_points


def cmd_rollback_list(args) -> None:
    """List available rollback points for a project."""
    points = list_rollback_points(args.project)
    if not points:
        print(f"No rollback points found for '{args.project}'.")
        return
    for i, entry in enumerate(points):
        label = entry.get("label") or ""
        label_str = f"  [{label}]" if label else ""
        print(f"  {i}: {entry['timestamp']}{label_str}")


def cmd_rollback_restore(args) -> None:
    """Restore a project to a specific version index."""
    password = getpass(f"Password for '{args.project}': ")
    try:
        ts = rollback_to_version(args.project, args.index, password)
        print(f"Rolled back '{args.project}' to version at {ts}.")
    except RollbackError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_rollback_parser(subparsers) -> None:
    """Attach rollback sub-commands to *subparsers*."""
    rb = subparsers.add_parser("rollback", help="Rollback project env to a previous version")
    rb_sub = rb.add_subparsers(dest="rollback_cmd", required=True)

    # list
    p_list = rb_sub.add_parser("list", help="List available rollback points")
    p_list.add_argument("project", help="Project name")
    p_list.set_defaults(func=cmd_rollback_list)

    # restore
    p_restore = rb_sub.add_parser("restore", help="Restore to a rollback point")
    p_restore.add_argument("project", help="Project name")
    p_restore.add_argument("index", type=int, help="Version index (from list)")
    p_restore.set_defaults(func=cmd_rollback_restore)
