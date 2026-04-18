import sys
import argparse
from envoy.diff import diff_projects, format_diff, DiffError


def cmd_diff(args):
    try:
        password_a = args.password_a or args.password
        password_b = args.password_b or args.password
        results = diff_projects(
            args.project_a,
            args.project_b,
            password_a,
            password_b,
        )
        output = format_diff(results)
        if not output.strip():
            print("No differences found.")
        else:
            print(output)
    except DiffError as e:
        print(f"diff error: {e}", file=sys.stderr)
        sys.exit(1)


def register_diff_parser(subparsers):
    p = subparsers.add_parser(
        "diff",
        help="Show differences between two stored .env projects",
    )
    p.add_argument("project_a", help="First project name")
    p.add_argument("project_b", help="Second project name")
    p.add_argument(
        "--password",
        default="",
        help="Shared password for both projects (if identical)",
    )
    p.add_argument(
        "--password-a",
        dest="password_a",
        default=None,
        help="Password for first project",
    )
    p.add_argument(
        "--password-b",
        dest="password_b",
        default=None,
        help="Password for second project",
    )
    p.set_defaults(func=cmd_diff)
    return p
