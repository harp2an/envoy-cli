"""CLI sub-commands for alias management."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.alias import (
    AliasError,
    add_alias,
    list_aliases,
    remove_alias,
    resolve_alias,
    update_alias,
)


def cmd_alias_add(args: Namespace) -> None:
    try:
        add_alias(args.alias, args.project)
        print(f"Alias '{args.alias}' -> '{args.project}' created.")
    except AliasError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_alias_update(args: Namespace) -> None:
    update_alias(args.alias, args.project)
    print(f"Alias '{args.alias}' updated to '{args.project}'.")


def cmd_alias_remove(args: Namespace) -> None:
    try:
        remove_alias(args.alias)
        print(f"Alias '{args.alias}' removed.")
    except AliasError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_alias_resolve(args: Namespace) -> None:
    project = resolve_alias(args.alias)
    if project is None:
        print(f"Alias '{args.alias}' not found.", file=sys.stderr)
        sys.exit(1)
    print(project)


def cmd_alias_list(args: Namespace) -> None:  # noqa: ARG001
    aliases = list_aliases()
    if not aliases:
        print("No aliases defined.")
        return
    for alias, project in sorted(aliases.items()):
        print(f"{alias} -> {project}")


def register_alias_parser(subparsers) -> None:
    p = subparsers.add_parser("alias", help="Manage project aliases")
    sub = p.add_subparsers(dest="alias_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a new alias")
    add_p.add_argument("alias")
    add_p.add_argument("project")
    add_p.set_defaults(func=cmd_alias_add)

    upd_p = sub.add_parser("update", help="Create or overwrite an alias")
    upd_p.add_argument("alias")
    upd_p.add_argument("project")
    upd_p.set_defaults(func=cmd_alias_update)

    rm_p = sub.add_parser("remove", help="Remove an alias")
    rm_p.add_argument("alias")
    rm_p.set_defaults(func=cmd_alias_remove)

    res_p = sub.add_parser("resolve", help="Print the project an alias points to")
    res_p.add_argument("alias")
    res_p.set_defaults(func=cmd_alias_resolve)

    ls_p = sub.add_parser("list", help="List all aliases")
    ls_p.set_defaults(func=cmd_alias_list)
