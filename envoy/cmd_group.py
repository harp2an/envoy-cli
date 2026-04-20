"""CLI sub-commands for group management."""

from __future__ import annotations

import sys

from envoy.group import (
    GroupError,
    add_to_group,
    delete_group,
    find_by_group,
    list_groups,
    remove_from_group,
)


def cmd_group_add(args) -> None:
    try:
        add_to_group(args.group, args.project)
        print(f"Added '{args.project}' to group '{args.group}'")
    except GroupError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_group_remove(args) -> None:
    try:
        remove_from_group(args.group, args.project)
        print(f"Removed '{args.project}' from group '{args.group}'")
    except GroupError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_group_list(args) -> None:
    groups = list_groups()
    if not groups:
        print("No groups defined.")
        return
    if getattr(args, "group", None):
        try:
            members = find_by_group(args.group)
        except GroupError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        for m in members:
            print(m)
    else:
        for name, members in sorted(groups.items()):
            print(f"{name}: {', '.join(members)}")


def cmd_group_delete(args) -> None:
    try:
        delete_group(args.group)
        print(f"Deleted group '{args.group}'")
    except GroupError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_group_parser(subparsers) -> None:
    p = subparsers.add_parser("group", help="Manage project groups")
    sub = p.add_subparsers(dest="group_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a project to a group")
    add_p.add_argument("group")
    add_p.add_argument("project")
    add_p.set_defaults(func=cmd_group_add)

    rm_p = sub.add_parser("remove", help="Remove a project from a group")
    rm_p.add_argument("group")
    rm_p.add_argument("project")
    rm_p.set_defaults(func=cmd_group_remove)

    ls_p = sub.add_parser("list", help="List groups or members of a group")
    ls_p.add_argument("group", nargs="?", default=None)
    ls_p.set_defaults(func=cmd_group_list)

    del_p = sub.add_parser("delete", help="Delete an entire group")
    del_p.add_argument("group")
    del_p.set_defaults(func=cmd_group_delete)
