"""CLI commands for managing project quotas."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from typing import Optional
from pathlib import Path

from envoy.quota import QuotaError, set_quota, get_quota, remove_quota, DEFAULT_MAX_KEYS, DEFAULT_MAX_BYTES


def cmd_quota_set(args: Namespace, store_dir: Optional[Path] = None) -> None:
    try:
        set_quota(
            args.project,
            max_keys=args.max_keys,
            max_bytes=args.max_bytes,
            store_dir=store_dir,
        )
        print(f"Quota set for '{args.project}': max_keys={args.max_keys or DEFAULT_MAX_KEYS}, "
              f"max_bytes={args.max_bytes or DEFAULT_MAX_BYTES}")
    except QuotaError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_quota_get(args: Namespace, store_dir: Optional[Path] = None) -> None:
    quota = get_quota(args.project, store_dir=store_dir)
    print(f"Project : {args.project}")
    print(f"max_keys: {quota['max_keys']}")
    print(f"max_bytes: {quota['max_bytes']}")


def cmd_quota_remove(args: Namespace, store_dir: Optional[Path] = None) -> None:
    try:
        remove_quota(args.project, store_dir=store_dir)
        print(f"Custom quota removed for '{args.project}' (defaults restored)")
    except QuotaError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_quota_parser(subparsers) -> None:
    quota_p = subparsers.add_parser("quota", help="Manage per-project quotas")
    quota_sub = quota_p.add_subparsers(dest="quota_cmd", required=True)

    # set
    p_set = quota_sub.add_parser("set", help="Set quota limits for a project")
    p_set.add_argument("project")
    p_set.add_argument("--max-keys", type=int, dest="max_keys", default=None)
    p_set.add_argument("--max-bytes", type=int, dest="max_bytes", default=None)
    p_set.set_defaults(func=cmd_quota_set)

    # get
    p_get = quota_sub.add_parser("get", help="Show quota limits for a project")
    p_get.add_argument("project")
    p_get.set_defaults(func=cmd_quota_get)

    # remove
    p_rm = quota_sub.add_parser("remove", help="Remove custom quota for a project")
    p_rm.add_argument("project")
    p_rm.set_defaults(func=cmd_quota_remove)
