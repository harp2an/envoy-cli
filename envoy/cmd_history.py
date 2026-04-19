"""CLI commands for env change history."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.history import HistoryError, list_versions, get_version, clear_history
from envoy.storage import load_env, store_env
from envoy.crypto import decrypt


def cmd_history_list(args: Namespace) -> None:
    versions = list_versions(args.project)
    if not versions:
        print(f"No history for '{args.project}'.")
        return
    for i, entry in enumerate(versions):
        label = f"  [{entry['label']}]" if entry.get("label") else ""
        print(f"  {i}: <version>{label}")


def cmd_history_restore(args: Namespace) -> None:
    try:
        ciphertext = get_version(args.project, args.index)
    except HistoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    try:
        decrypt(ciphertext, args.password)
    except Exception:
        print("Error: wrong password.", file=sys.stderr)
        sys.exit(1)
    store_env(args.project, ciphertext)
    print(f"Restored version {args.index} for '{args.project}'.")


def cmd_history_clear(args: Namespace) -> None:
    clear_history(args.project)
    print(f"History cleared for '{args.project}'.")


def register_history_parser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser("history", help="Manage env change history")
    sub = p.add_subparsers(dest="history_cmd", required=True)

    ls = sub.add_parser("list", help="List versions")
    ls.add_argument("project")
    ls.set_defaults(func=cmd_history_list)

    rs = sub.add_parser("restore", help="Restore a version")
    rs.add_argument("project")
    rs.add_argument("index", type=int)
    rs.add_argument("--password", required=True)
    rs.set_defaults(func=cmd_history_restore)

    cl = sub.add_parser("clear", help="Clear history")
    cl.add_argument("project")
    cl.set_defaults(func=cmd_history_clear)
