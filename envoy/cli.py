"""CLI entry point for envoy-cli."""

import argparse
import getpass
import sys

from envoy.storage import store_env, load_env, list_projects, delete_env
from envoy.sync import push_env, pull_env, list_remote_projects, SyncError


def cmd_set(args):
    """Read .env from stdin or file and store it."""
    password = getpass.getpass("Password: ")
    if args.file:
        with open(args.file) as fh:
            content = fh.read()
    else:
        print("Paste .env content (Ctrl-D to finish):")
        content = sys.stdin.read()
    store_env(args.project, content, password)
    print(f"Stored env for '{args.project}'.")


def cmd_get(args):
    """Decrypt and print env to stdout."""
    password = getpass.getpass("Password: ")
    try:
        content = load_env(args.project, password)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(content)


def cmd_push(args):
    password = getpass.getpass("Password: ")
    try:
        url = push_env(args.project, password, remote_url=args.remote)
        print(f"Pushed to {url}")
    except SyncError as exc:
        print(f"Sync error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pull(args):
    password = getpass.getpass("Password: ")
    try:
        pull_env(args.project, password, remote_url=args.remote)
        print(f"Pulled env for '{args.project}'.")
    except SyncError as exc:
        print(f"Sync error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_ls(args):
    projects = list_projects()
    if not projects:
        print("No local projects stored.")
    for p in projects:
        print(p)


def cmd_remote_ls(args):
    try:
        projects = list_remote_projects(remote_url=args.remote)
    except SyncError as exc:
        print(f"Sync error: {exc}", file=sys.stderr)
        sys.exit(1)
    for p in projects:
        print(p)


def build_parser():
    parser = argparse.ArgumentParser(prog="envoy", description="Manage .env files")
    sub = parser.add_subparsers(dest="command", required=True)

    for cmd_name, help_text in [("set", "Store an env"), ("get", "Retrieve an env")]:
        p = sub.add_parser(cmd_name, help=help_text)
        p.add_argument("project")
        if cmd_name == "set":
            p.add_argument("--file", "-f", default=None)

    for cmd_name in ("push", "pull", "remote-ls"):
        p = sub.add_parser(cmd_name)
        if cmd_name != "remote-ls":
            p.add_argument("project")
        p.add_argument("--remote", default=None)

    sub.add_parser("ls", help="List local projects")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {
        "set": cmd_set, "get": cmd_get, "push": cmd_push,
        "pull": cmd_pull, "ls": cmd_ls, "remote-ls": cmd_remote_ls,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
