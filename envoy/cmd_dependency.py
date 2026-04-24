"""CLI commands for managing project dependencies."""
from __future__ import annotations

import argparse
import sys

from envoy.dependency import (
    DependencyError,
    add_dependency,
    list_dependencies,
    list_dependents,
    remove_dependency,
)


def cmd_dep_add(args: argparse.Namespace) -> None:
    try:
        add_dependency(args.project, args.depends_on)
        print(f"Added dependency: {args.project} -> {args.depends_on}")
    except DependencyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_dep_remove(args: argparse.Namespace) -> None:
    try:
        remove_dependency(args.project, args.depends_on)
        print(f"Removed dependency: {args.project} -> {args.depends_on}")
    except DependencyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_dep_list(args: argparse.Namespace) -> None:
    deps = list_dependencies(args.project)
    if not deps:
        print(f"No dependencies for '{args.project}'.")
    else:
        for dep in deps:
            print(dep)


def cmd_dep_dependents(args: argparse.Namespace) -> None:
    dependents = list_dependents(args.project)
    if not dependents:
        print(f"No projects depend on '{args.project}'.")
    else:
        for dep in dependents:
            print(dep)


def register_dependency_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("dependency", help="Manage project dependencies")
    sub = p.add_subparsers(dest="dep_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a dependency")
    add_p.add_argument("project")
    add_p.add_argument("depends_on")
    add_p.set_defaults(func=cmd_dep_add)

    rm_p = sub.add_parser("remove", help="Remove a dependency")
    rm_p.add_argument("project")
    rm_p.add_argument("depends_on")
    rm_p.set_defaults(func=cmd_dep_remove)

    ls_p = sub.add_parser("list", help="List dependencies of a project")
    ls_p.add_argument("project")
    ls_p.set_defaults(func=cmd_dep_list)

    dep_p = sub.add_parser("dependents", help="List projects that depend on a project")
    dep_p.add_argument("project")
    dep_p.set_defaults(func=cmd_dep_dependents)
