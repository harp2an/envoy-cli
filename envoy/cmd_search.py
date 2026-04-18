"""CLI subcommand: search env projects for a key or value pattern."""

import getpass
import sys

from envoy.search import search_key, search_value


def cmd_search(args):
    password = getpass.getpass("Password: ")

    if args.mode == "key":
        results = search_key(args.query, password)
        if not results:
            print(f"Key '{args.query}' not found in any project.")
            return
        for project, value in sorted(results.items()):
            print(f"{project}: {args.query}={value}")

    elif args.mode == "value":
        results = search_value(args.query, password)
        if not results:
            print(f"Pattern '{args.query}' not found in any project.")
            return
        for project, matches in sorted(results.items()):
            for k, v in sorted(matches.items()):
                print(f"{project}: {k}={v}")

    else:
        print(f"Unknown search mode: {args.mode}", file=sys.stderr)
        sys.exit(1)


def register_search_parser(subparsers):
    p = subparsers.add_parser("search", help="Search projects for a key or value")
    p.add_argument(
        "mode",
        choices=["key", "value"],
        help="Search by exact key name or value substring",
    )
    p.add_argument("query", help="Key name or value pattern to search for")
    p.set_defaults(func=cmd_search)
    return p
