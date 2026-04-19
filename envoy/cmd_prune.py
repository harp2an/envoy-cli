"""CLI commands for pruning stale project data."""

from __future__ import annotations

import argparse
import sys

from envoy.prune import PruneError, list_orphaned, prune_orphaned, prune_project


def cmd_prune(args: argparse.Namespace) -> None:
    store = getattr(args, "store", None)
    if args.project:
        try:
            prune_project(args.project, store_dir=store)
            print(f"Pruned project '{args.project}'.")
        except PruneError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
    elif args.dry_run:
        orphaned = list_orphaned(store_dir=store)
        if not orphaned:
            print("No orphaned projects found.")
        else:
            print("Orphaned projects:")
            for name in orphaned:
                print(f"  {name}")
    else:
        removed = prune_orphaned(store_dir=store)
        if not removed:
            print("Nothing to prune.")
        else:
            for name in removed:
                print(f"Pruned orphaned project '{name}'.")


def register_prune_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("prune", help="Remove stale or orphaned project data")
    p.add_argument("--project", "-p", default=None, help="Prune a specific project")
    p.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        dest="dry_run",
        help="List orphaned projects without removing them",
    )
    p.set_defaults(func=cmd_prune)
