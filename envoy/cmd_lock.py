"""CLI commands for managing project locks."""

import sys

from envoy.lock import LockError, acquire_lock, is_locked, release_lock
from envoy.storage import load_manifest


def cmd_lock_acquire(args):
    try:
        acquire_lock(args.project, owner=args.owner or "envoy")
        print(f"Lock acquired for '{args.project}'.")
    except LockError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_lock_release(args):
    if not is_locked(args.project):
        print(f"No active lock for '{args.project}'.")
        return
    release_lock(args.project)
    print(f"Lock released for '{args.project}'.")


def cmd_lock_status(args):
    manifest = load_manifest()
    projects = list(manifest.keys()) if not args.project else [args.project]
    if not projects:
        print("No projects found.")
        return
    for proj in projects:
        status = "LOCKED" if is_locked(proj) else "unlocked"
        print(f"  {proj}: {status}")


def register_lock_parser(subparsers):
    lock_p = subparsers.add_parser("lock", help="Manage project locks")
    lock_sub = lock_p.add_subparsers(dest="lock_cmd", required=True)

    acq = lock_sub.add_parser("acquire", help="Acquire a lock on a project")
    acq.add_argument("project")
    acq.add_argument("--owner", default="envoy")
    acq.set_defaults(func=cmd_lock_acquire)

    rel = lock_sub.add_parser("release", help="Release a lock on a project")
    rel.add_argument("project")
    rel.set_defaults(func=cmd_lock_release)

    st = lock_sub.add_parser("status", help="Show lock status")
    st.add_argument("project", nargs="?", default=None)
    st.set_defaults(func=cmd_lock_status)
