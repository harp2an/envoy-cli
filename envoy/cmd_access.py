"""CLI sub-commands for access control management."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.access import AccessError, grant_access, revoke_access, list_access, check_access


def cmd_access_grant(args: Namespace) -> None:
    try:
        grant_access(args.project, args.identity, args.permission)
        print(f"Granted '{args.permission}' to '{args.identity}' on '{args.project}'.")
    except AccessError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_access_revoke(args: Namespace) -> None:
    try:
        revoke_access(args.project, args.identity, args.permission)
        print(f"Revoked '{args.permission}' from '{args.identity}' on '{args.project}'.")
    except AccessError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_access_list(args: Namespace) -> None:
    acl = list_access(args.project)
    if not acl:
        print(f"No access rules for project '{args.project}'.")
        return
    for identity, perms in sorted(acl.items()):
        print(f"  {identity}: {', '.join(sorted(perms))}")


def cmd_access_check(args: Namespace) -> None:
    allowed = check_access(args.project, args.identity, args.permission)
    status = "ALLOWED" if allowed else "DENIED"
    print(f"{status}: '{args.identity}' / '{args.permission}' on '{args.project}'")


def register_access_parser(subparsers) -> None:
    p = subparsers.add_parser("access", help="Manage per-project access control")
    sub = p.add_subparsers(dest="access_cmd", required=True)

    # grant
    pg = sub.add_parser("grant", help="Grant a permission")
    pg.add_argument("project")
    pg.add_argument("identity", help="User or role name")
    pg.add_argument("permission", choices=["read", "write", "admin"])
    pg.set_defaults(func=cmd_access_grant)

    # revoke
    pr = sub.add_parser("revoke", help="Revoke a permission")
    pr.add_argument("project")
    pr.add_argument("identity")
    pr.add_argument("permission", choices=["read", "write", "admin"])
    pr.set_defaults(func=cmd_access_revoke)

    # list
    pl = sub.add_parser("list", help="List access rules for a project")
    pl.add_argument("project")
    pl.set_defaults(func=cmd_access_list)

    # check
    pc = sub.add_parser("check", help="Check if an identity has a permission")
    pc.add_argument("project")
    pc.add_argument("identity")
    pc.add_argument("permission", choices=["read", "write", "admin"])
    pc.set_defaults(func=cmd_access_check)
