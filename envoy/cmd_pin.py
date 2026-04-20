"""CLI commands for pinning projects to specific versions."""
import argparse
import sys

from envoy.pin import PinError, pin_project, unpin_project, get_pin, list_pins


def cmd_pin_set(args):
    """Pin a project to a specific version label."""
    try:
        pin_project(args.project, args.version, store_dir=args.store_dir)
        print(f"Pinned '{args.project}' to version '{args.version}'.")
    except PinError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pin_get(args):
    """Show the pinned version for a project."""
    entry = get_pin(args.project, store_dir=args.store_dir)
    if entry is None:
        print(f"No pin found for '{args.project}'.")
    else:
        print(f"{args.project}: {entry['version']} (pinned at {entry['pinned_at']})")


def cmd_pin_remove(args):
    """Remove the pin for a project."""
    try:
        unpin_project(args.project, store_dir=args.store_dir)
        print(f"Removed pin for '{args.project}'.")
    except PinError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pin_list(args):
    """List all pinned projects."""
    pins = list_pins(store_dir=args.store_dir)
    if not pins:
        print("No pinned projects.")
        return
    for project, entry in sorted(pins.items()):
        print(f"{project}: {entry['version']} (pinned at {entry['pinned_at']})")


def register_pin_parser(subparsers, default_store):
    p = subparsers.add_parser("pin", help="Manage project version pins")
    p.add_argument("--store-dir", default=default_store)
    sub = p.add_subparsers(dest="pin_cmd", required=True)

    ps = sub.add_parser("set", help="Pin a project to a version")
    ps.add_argument("project")
    ps.add_argument("version")
    ps.set_defaults(func=cmd_pin_set)

    pg = sub.add_parser("get", help="Show pin for a project")
    pg.add_argument("project")
    pg.set_defaults(func=cmd_pin_get)

    pr = sub.add_parser("remove", help="Remove pin for a project")
    pr.add_argument("project")
    pr.set_defaults(func=cmd_pin_remove)

    pl = sub.add_parser("list", help="List all pinned projects")
    pl.set_defaults(func=cmd_pin_list)

    return p
