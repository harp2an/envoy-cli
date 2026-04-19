"""CLI commands for managing share tokens."""

import sys
from envoy.share import create_share, revoke_share, resolve_share, list_shares, ShareError


def cmd_share_create(args) -> None:
    note = getattr(args, "note", "") or ""
    token = create_share(args.project, note=note)
    print(f"Share token created: {token}")


def cmd_share_revoke(args) -> None:
    try:
        revoke_share(args.token)
        print(f"Token revoked: {args.token}")
    except ShareError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_share_resolve(args) -> None:
    meta = resolve_share(args.token)
    if meta is None:
        print("Token not found.", file=sys.stderr)
        sys.exit(1)
    print(f"Project: {meta['project']}")
    if meta.get("note"):
        print(f"Note: {meta['note']}")


def cmd_share_list(args) -> None:
    shares = list_shares()
    if not shares:
        print("No active shares.")
        return
    for s in shares:
        note = f"  # {s['note']}" if s.get("note") else ""
        print(f"{s['token']}  ->  {s['project']}{note}")


def register_share_parser(subparsers) -> None:
    p = subparsers.add_parser("share", help="Manage share tokens")
    sp = p.add_subparsers(dest="share_cmd", required=True)

    pc = sp.add_parser("create", help="Create a share token")
    pc.add_argument("project")
    pc.add_argument("--note", default="")
    pc.set_defaults(func=cmd_share_create)

    pr = sp.add_parser("revoke", help="Revoke a share token")
    pr.add_argument("token")
    pr.set_defaults(func=cmd_share_revoke)

    ps = sp.add_parser("resolve", help="Resolve a share token")
    ps.add_argument("token")
    ps.set_defaults(func=cmd_share_resolve)

    pl = sp.add_parser("list", help="List all share tokens")
    pl.set_defaults(func=cmd_share_list)
