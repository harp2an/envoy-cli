"""CLI sub-commands for key rotation."""

from __future__ import annotations

import argparse
import getpass
import sys

from envoy.audit import record_event
from envoy.rotate import RotationError, rotate_all, rotate_project


def cmd_rotate(args: argparse.Namespace) -> None:
    old_password = getpass.getpass("Current password: ")
    new_password = getpass.getpass("New password: ")
    confirm = getpass.getpass("Confirm new password: ")

    if new_password != confirm:
        print("Error: new passwords do not match.", file=sys.stderr)
        sys.exit(1)

    try:
        if args.project:
            rotate_project(args.project, old_password, new_password)
            record_event("rotate", args.project, {"scope": "single"})
            print(f"Rotated key for project '{args.project}'.")
        else:
            rotated = rotate_all(old_password, new_password)
            for p in rotated:
                record_event("rotate", p, {"scope": "all"})
            print(f"Rotated {len(rotated)} project(s).")
    except RotationError as exc:
        print(f"Rotation failed: {exc}", file=sys.stderr)
        sys.exit(1)


def register_rotate_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("rotate", help="Re-encrypt env(s) with a new password")
    p.add_argument(
        "project",
        nargs="?",
        default=None,
        help="Project name to rotate (omit to rotate all)",
    )
    p.set_defaults(func=cmd_rotate)
