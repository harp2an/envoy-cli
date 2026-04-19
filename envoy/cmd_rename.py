"""CLI sub-command: rename a project."""

import sys
from envoy.rename import rename_project, RenameError
from envoy.audit import record_event


def cmd_rename(args) -> None:
    try:
        rename_project(args.old_name, args.new_name)
        record_event("rename", args.old_name, extra={"new_name": args.new_name})
        print(f"Renamed '{args.old_name}' -> '{args.new_name}'.")
    except RenameError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_rename_parser(subparsers) -> None:
    p = subparsers.add_parser("rename", help="Rename a project in the local store.")
    p.add_argument("old_name", help="Current project name.")
    p.add_argument("new_name", help="New project name.")
    p.set_defaults(func=cmd_rename)
