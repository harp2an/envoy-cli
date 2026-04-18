"""CLI subcommands for snapshot management."""

import argparse
import getpass
import sys

from envoy.snapshot import SnapshotError, create_snapshot, delete_snapshot, list_snapshots, restore_snapshot


def cmd_snapshot_create(args: argparse.Namespace) -> None:
    password = getpass.getpass("Password: ")
    try:
        tag = create_snapshot(args.project, password, label=getattr(args, "label", None))
        print(f"Snapshot created: {tag}")
    except SnapshotError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot_list(args: argparse.Namespace) -> None:
    tags = list_snapshots(args.project)
    if not tags:
        print(f"No snapshots for project '{args.project}'.")
    else:
        for t in tags:
            print(t)


def cmd_snapshot_restore(args: argparse.Namespace) -> None:
    password = getpass.getpass("Password: ")
    try:
        restore_snapshot(args.project, args.tag, password)
        print(f"Restored snapshot '{args.tag}' to project '{args.project}'.")
    except SnapshotError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot_delete(args: argparse.Namespace) -> None:
    try:
        delete_snapshot(args.project, args.tag)
        print(f"Deleted snapshot '{args.tag}' from project '{args.project}'.")
    except SnapshotError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def register_snapshot_parser(subparsers) -> None:
    p = subparsers.add_parser("snapshot", help="Manage env snapshots")
    sp = p.add_subparsers(dest="snapshot_cmd", required=True)

    c = sp.add_parser("create", help="Create a snapshot")
    c.add_argument("project")
    c.add_argument("--label", default=None)
    c.set_defaults(func=cmd_snapshot_create)

    ls = sp.add_parser("list", help="List snapshots")
    ls.add_argument("project")
    ls.set_defaults(func=cmd_snapshot_list)

    r = sp.add_parser("restore", help="Restore a snapshot")
    r.add_argument("project")
    r.add_argument("tag")
    r.set_defaults(func=cmd_snapshot_restore)

    d = sp.add_parser("delete", help="Delete a snapshot")
    d.add_argument("project")
    d.add_argument("tag")
    d.set_defaults(func=cmd_snapshot_delete)
