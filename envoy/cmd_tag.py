"""CLI commands for tag management."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.tag import TagError, add_tag, remove_tag, list_tags, find_by_tag


def cmd_tag_add(args: Namespace) -> None:
    try:
        add_tag(args.project, args.tag)
        print(f"Tag '{args.tag}' added to '{args.project}'")
    except TagError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_remove(args: Namespace) -> None:
    try:
        remove_tag(args.project, args.tag)
        print(f"Tag '{args.tag}' removed from '{args.project}'")
    except TagError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_list(args: Namespace) -> None:
    try:
        tags = list_tags(args.project)
        if not tags:
            print(f"No tags for '{args.project}'")
        else:
            for t in tags:
                print(t)
    except TagError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_find(args: Namespace) -> None:
    projects = find_by_tag(args.tag)
    if not projects:
        print(f"No projects tagged '{args.tag}'")
    else:
        for p in projects:
            print(p)


def register_tag_parser(subparsers) -> None:
    p = subparsers.add_parser("tag", help="Manage project tags")
    sub = p.add_subparsers(dest="tag_cmd", required=True)

    add_p = sub.add_parser("add", help="Add tag to project")
    add_p.add_argument("project")
    add_p.add_argument("tag")
    add_p.set_defaults(func=cmd_tag_add)

    rm_p = sub.add_parser("remove", help="Remove tag from project")
    rm_p.add_argument("project")
    rm_p.add_argument("tag")
    rm_p.set_defaults(func=cmd_tag_remove)

    ls_p = sub.add_parser("list", help="List tags for project")
    ls_p.add_argument("project")
    ls_p.set_defaults(func=cmd_tag_list)

    find_p = sub.add_parser("find", help="Find projects by tag")
    find_p.add_argument("tag")
    find_p.set_defaults(func=cmd_tag_find)
