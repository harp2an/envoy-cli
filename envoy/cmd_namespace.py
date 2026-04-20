"""CLI commands for namespace management."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.namespace import (
    NamespaceError,
    add_to_namespace,
    delete_namespace,
    get_namespace_projects,
    list_namespaces,
    remove_from_namespace,
)


def cmd_namespace_add(args: Namespace) -> None:
    try:
        add_to_namespace(args.namespace, args.project)
        print(f"Added '{args.project}' to namespace '{args.namespace}'")
    except NamespaceError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_namespace_remove(args: Namespace) -> None:
    try:
        remove_from_namespace(args.namespace, args.project)
        print(f"Removed '{args.project}' from namespace '{args.namespace}'")
    except NamespaceError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_namespace_list(args: Namespace) -> None:
    if getattr(args, "namespace", None):
        try:
            projects = get_namespace_projects(args.namespace)
            if projects:
                for p in projects:
                    print(p)
            else:
                print(f"Namespace '{args.namespace}' is empty")
        except NamespaceError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        data = list_namespaces()
        if not data:
            print("No namespaces defined")
        else:
            for ns, members in data.items():
                print(f"{ns}: {', '.join(members) if members else '(empty)'}")


def cmd_namespace_delete(args: Namespace) -> None:
    try:
        delete_namespace(args.namespace)
        print(f"Deleted namespace '{args.namespace}'")
    except NamespaceError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_namespace_parser(subparsers) -> None:
    p = subparsers.add_parser("namespace", help="Manage project namespaces")
    sub = p.add_subparsers(dest="ns_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a project to a namespace")
    add_p.add_argument("namespace")
    add_p.add_argument("project")
    add_p.set_defaults(func=cmd_namespace_add)

    rm_p = sub.add_parser("remove", help="Remove a project from a namespace")
    rm_p.add_argument("namespace")
    rm_p.add_argument("project")
    rm_p.set_defaults(func=cmd_namespace_remove)

    ls_p = sub.add_parser("list", help="List namespaces or projects in a namespace")
    ls_p.add_argument("namespace", nargs="?", default=None)
    ls_p.set_defaults(func=cmd_namespace_list)

    del_p = sub.add_parser("delete", help="Delete a namespace")
    del_p.add_argument("namespace")
    del_p.set_defaults(func=cmd_namespace_delete)
