"""CLI commands for cloning projects."""

import sys
from envoy.clone import CloneError, clone_project, clone_with_rename


def cmd_clone(args) -> None:
    try:
        clone_with_rename(
            src=args.src,
            dst=args.dst,
            password=args.password,
            new_password=args.new_password,
            prefix=args.prefix or "",
            suffix=args.suffix or "",
        )
        print(f"Cloned '{args.src}' -> '{args.dst}'")
    except CloneError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_clone_parser(subparsers) -> None:
    p = subparsers.add_parser("clone", help="Clone a project env to a new project")
    p.add_argument("src", help="Source project name")
    p.add_argument("dst", help="Destination project name")
    p.add_argument("--password", required=True, help="Password for source project")
    p.add_argument("--new-password", dest="new_password", default=None,
                   help="Password for destination project (default: same as source)")
    p.add_argument("--prefix", default=None, help="Prefix to add to all keys")
    p.add_argument("--suffix", default=None, help="Suffix to add to all keys")
    p.set_defaults(func=cmd_clone)
