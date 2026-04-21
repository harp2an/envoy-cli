"""CLI commands for project badge management."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.badge import BadgeError, generate_badge, get_badge, list_badges, remove_badge
from envoy.storage import get_store_dir


def cmd_badge_generate(args: Namespace) -> None:
    store_dir = get_store_dir()
    try:
        badge = generate_badge(args.project, store_dir)
    except BadgeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Badge generated for '{badge['project']}':")
    print(f"  status  : {badge['status']}")
    print(f"  keys    : {badge['keys']}")
    print(f"  updated : {badge['updated']}")


def cmd_badge_get(args: Namespace) -> None:
    store_dir = get_store_dir()
    badge = get_badge(args.project, store_dir)
    if badge is None:
        print(f"No badge found for '{args.project}'.")
        return
    print(f"project : {badge['project']}")
    print(f"status  : {badge['status']}")
    print(f"keys    : {badge['keys']}")
    print(f"updated : {badge['updated']}")


def cmd_badge_remove(args: Namespace) -> None:
    store_dir = get_store_dir()
    try:
        remove_badge(args.project, store_dir)
    except BadgeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Badge for '{args.project}' removed.")


def cmd_badge_list(args: Namespace) -> None:
    store_dir = get_store_dir()
    badges = list_badges(store_dir)
    if not badges:
        print("No badges stored.")
        return
    for b in badges:
        print(f"{b['project']:20s}  status={b['status']}  keys={b['keys']}  updated={b['updated']}")


def register_badge_parser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser("badge", help="Manage project status badges.")
    sub = p.add_subparsers(dest="badge_cmd", required=True)

    gen = sub.add_parser("generate", help="Generate a badge for a project.")
    gen.add_argument("project")
    gen.set_defaults(func=cmd_badge_generate)

    get_p = sub.add_parser("get", help="Show the stored badge for a project.")
    get_p.add_argument("project")
    get_p.set_defaults(func=cmd_badge_get)

    rm = sub.add_parser("remove", help="Remove the badge for a project.")
    rm.add_argument("project")
    rm.set_defaults(func=cmd_badge_remove)

    ls = sub.add_parser("list", help="List all stored badges.")
    ls.set_defaults(func=cmd_badge_list)
