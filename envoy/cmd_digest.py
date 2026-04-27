"""CLI commands for the digest feature."""

from __future__ import annotations

import sys
from pathlib import Path

from envoy.storage import get_store_dir
from envoy.digest import DigestError, generate_digest, list_digests, verify_digest, clear_digests


def cmd_digest_generate(args) -> None:
    store_dir = get_store_dir()
    try:
        record = generate_digest(store_dir, args.project, note=args.note or "")
    except DigestError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Digest generated: {record['fingerprint'][:16]}...  ({record['generated_at']})")


def cmd_digest_list(args) -> None:
    store_dir = get_store_dir()
    records = list_digests(store_dir, args.project)
    if not records:
        print(f"No digests for project '{args.project}'.")
        return
    for i, rec in enumerate(records):
        note = f"  # {rec['note']}" if rec.get("note") else ""
        print(f"[{i}] {rec['generated_at']}  {rec['fingerprint'][:16]}...{note}")


def cmd_digest_verify(args) -> None:
    store_dir = get_store_dir()
    try:
        index = int(args.index) if args.index is not None else -1
        ok = verify_digest(store_dir, args.project, index=index)
    except DigestError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    if ok:
        print(f"Digest verified: project '{args.project}' matches stored fingerprint.")
    else:
        print(f"Digest MISMATCH: project '{args.project}' has changed since digest was recorded.")
        sys.exit(2)


def cmd_digest_clear(args) -> None:
    store_dir = get_store_dir()
    clear_digests(store_dir, args.project)
    print(f"Cleared all digests for project '{args.project}'.")


def register_digest_parser(subparsers) -> None:
    p = subparsers.add_parser("digest", help="Manage project digests")
    sub = p.add_subparsers(dest="digest_cmd", required=True)

    gen = sub.add_parser("generate", help="Generate a digest for a project")
    gen.add_argument("project")
    gen.add_argument("--note", default="", help="Optional note to attach")
    gen.set_defaults(func=cmd_digest_generate)

    lst = sub.add_parser("list", help="List digests for a project")
    lst.add_argument("project")
    lst.set_defaults(func=cmd_digest_list)

    ver = sub.add_parser("verify", help="Verify current state against a stored digest")
    ver.add_argument("project")
    ver.add_argument("--index", default=None, help="Digest index (default: latest)")
    ver.set_defaults(func=cmd_digest_verify)

    clr = sub.add_parser("clear", help="Clear all digests for a project")
    clr.add_argument("project")
    clr.set_defaults(func=cmd_digest_clear)
