"""CLI commands for retention policy management."""
from __future__ import annotations

import sys

from envoy.retention import RetentionError, get_retention, list_retention, remove_retention, set_retention
from envoy.storage import get_store_dir


def cmd_retention_set(args) -> None:
    store_dir = get_store_dir()
    try:
        result = set_retention(store_dir, args.project, args.max_versions, args.max_snapshots)
        print(f"Retention set for '{args.project}': max_versions={result['max_versions']}, max_snapshots={result['max_snapshots']}")
    except RetentionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_retention_get(args) -> None:
    store_dir = get_store_dir()
    policy = get_retention(store_dir, args.project)
    if policy is None:
        print(f"No retention policy set for '{args.project}'")
    else:
        print(f"max_versions={policy['max_versions']}  max_snapshots={policy['max_snapshots']}")


def cmd_retention_remove(args) -> None:
    store_dir = get_store_dir()
    try:
        remove_retention(store_dir, args.project)
        print(f"Retention policy removed for '{args.project}'")
    except RetentionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_retention_list(args) -> None:
    store_dir = get_store_dir()
    policies = list_retention(store_dir)
    if not policies:
        print("No retention policies configured.")
        return
    for project, policy in sorted(policies.items()):
        print(f"{project}: max_versions={policy['max_versions']}, max_snapshots={policy['max_snapshots']}")


def register_retention_parser(subparsers) -> None:
    p = subparsers.add_parser("retention", help="Manage retention policies")
    sub = p.add_subparsers(dest="retention_cmd", required=True)

    ps = sub.add_parser("set", help="Set retention policy")
    ps.add_argument("project")
    ps.add_argument("--max-versions", type=int, default=10, dest="max_versions")
    ps.add_argument("--max-snapshots", type=int, default=5, dest="max_snapshots")
    ps.set_defaults(func=cmd_retention_set)

    pg = sub.add_parser("get", help="Get retention policy")
    pg.add_argument("project")
    pg.set_defaults(func=cmd_retention_get)

    pr = sub.add_parser("remove", help="Remove retention policy")
    pr.add_argument("project")
    pr.set_defaults(func=cmd_retention_remove)

    pl = sub.add_parser("list", help="List all retention policies")
    pl.set_defaults(func=cmd_retention_list)
