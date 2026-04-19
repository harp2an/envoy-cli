"""CLI commands for merging env projects."""

import sys
from getpass import getpass

from envoy.merge import MergeError, merge_projects, STRATEGIES


def cmd_merge(args):
    src_password = getpass(f"Password for '{args.src}': ")
    dst_password = getpass(f"Password for '{args.dst}': ")
    try:
        merged = merge_projects(
            args.src,
            args.dst,
            src_password,
            dst_password,
            strategy=args.strategy,
        )
    except MergeError as exc:
        print(f"Merge error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Merged '{args.src}' into '{args.dst}' using strategy '{args.strategy}'.")
    print(f"{len(merged)} key(s) in result.")


def register_merge_parser(subparsers):
    p = subparsers.add_parser("merge", help="Merge one project's env into another")
    p.add_argument("src", help="Source project name")
    p.add_argument("dst", help="Destination project name")
    p.add_argument(
        "--strategy",
        choices=STRATEGIES,
        default="ours",
        help="Conflict resolution strategy (default: ours)",
    )
    p.set_defaults(func=cmd_merge)
    return p
