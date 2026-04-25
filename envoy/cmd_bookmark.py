"""CLI commands for bookmark management."""

import sys
from envoy.storage import get_store_dir
from envoy.bookmark import (
    BookmarkError,
    add_bookmark,
    remove_bookmark,
    get_bookmark,
    list_bookmarks,
)


def cmd_bookmark_add(args) -> None:
    store_dir = get_store_dir()
    try:
        add_bookmark(store_dir, args.name, args.project, args.key)
        print(f"Bookmark '{args.name}' -> {args.project}:{args.key}")
    except BookmarkError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_bookmark_remove(args) -> None:
    store_dir = get_store_dir()
    try:
        remove_bookmark(store_dir, args.name)
        print(f"Bookmark '{args.name}' removed")
    except BookmarkError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_bookmark_get(args) -> None:
    store_dir = get_store_dir()
    entry = get_bookmark(store_dir, args.name)
    if entry is None:
        print(f"Bookmark '{args.name}' not found", file=sys.stderr)
        sys.exit(1)
    print(f"{entry['project']}:{entry['key']}")


def cmd_bookmark_list(args) -> None:
    store_dir = get_store_dir()
    entries = list_bookmarks(store_dir)
    if not entries:
        print("No bookmarks defined")
        return
    for e in entries:
        print(f"{e['name']:20s}  {e['project']}:{e['key']}")


def register_bookmark_parser(subparsers) -> None:
    p = subparsers.add_parser("bookmark", help="Manage bookmarks")
    sub = p.add_subparsers(dest="bookmark_cmd", required=True)

    pa = sub.add_parser("add", help="Add a bookmark")
    pa.add_argument("name")
    pa.add_argument("project")
    pa.add_argument("key")
    pa.set_defaults(func=cmd_bookmark_add)

    pr = sub.add_parser("remove", help="Remove a bookmark")
    pr.add_argument("name")
    pr.set_defaults(func=cmd_bookmark_remove)

    pg = sub.add_parser("get", help="Get a bookmark")
    pg.add_argument("name")
    pg.set_defaults(func=cmd_bookmark_get)

    pl = sub.add_parser("list", help="List all bookmarks")
    pl.set_defaults(func=cmd_bookmark_list)
