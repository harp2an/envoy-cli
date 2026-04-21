"""CLI commands for profile management."""
from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace

from envoy.profile import ProfileError, get_profile, list_profiles, remove_profile, set_profile


def cmd_profile_set(args: Namespace) -> None:
    try:
        overrides: dict = {}
        for pair in (args.override or []):
            if "=" not in pair:
                print(f"Invalid override '{pair}' — expected KEY=VALUE", file=sys.stderr)
                sys.exit(1)
            k, v = pair.split("=", 1)
            overrides[k] = v
        set_profile(args.project, args.profile, overrides)
        print(f"Profile '{args.profile}' set for project '{args.project}'")
    except ProfileError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_profile_get(args: Namespace) -> None:
    result = get_profile(args.project, args.profile)
    if result is None:
        print(f"No profile '{args.profile}' for project '{args.project}'")
    else:
        print(json.dumps(result, indent=2))


def cmd_profile_remove(args: Namespace) -> None:
    try:
        remove_profile(args.project, args.profile)
        print(f"Profile '{args.profile}' removed from project '{args.project}'")
    except ProfileError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_profile_list(args: Namespace) -> None:
    profiles = list_profiles(args.project)
    if not profiles:
        print(f"No profiles for project '{args.project}'")
    else:
        for name in profiles:
            print(name)


def register_profile_parser(subparsers) -> None:
    p = subparsers.add_parser("profile", help="Manage named env profiles")
    sub = p.add_subparsers(dest="profile_cmd", required=True)

    ps = sub.add_parser("set", help="Create or replace a profile")
    ps.add_argument("project")
    ps.add_argument("profile")
    ps.add_argument("override", nargs="*", metavar="KEY=VALUE")
    ps.set_defaults(func=cmd_profile_set)

    pg = sub.add_parser("get", help="Show a profile's overrides")
    pg.add_argument("project")
    pg.add_argument("profile")
    pg.set_defaults(func=cmd_profile_get)

    pr = sub.add_parser("remove", help="Delete a profile")
    pr.add_argument("project")
    pr.add_argument("profile")
    pr.set_defaults(func=cmd_profile_remove)

    pl = sub.add_parser("list", help="List profiles for a project")
    pl.add_argument("project")
    pl.set_defaults(func=cmd_profile_list)
