"""CLI sub-command: compare two projects."""
from __future__ import annotations
import sys
from envoy.compare import compare_projects, format_compare, CompareError


def cmd_compare(args) -> None:
    import getpass

    password_a = getpass.getpass(f"Password for {args.project_a}: ")
    if args.same_password:
        password_b = password_a
    else:
        password_b = getpass.getpass(f"Password for {args.project_b}: ")

    try:
        result = compare_projects(args.project_a, password_a, args.project_b, password_b)
    except CompareError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = format_compare(result, args.project_a, args.project_b)
    print(output)

    if args.exit_code and not result.is_equal:
        sys.exit(2)


def register_compare_parser(subparsers) -> None:
    p = subparsers.add_parser("compare", help="Compare env contents of two projects")
    p.add_argument("project_a", help="First project name")
    p.add_argument("project_b", help="Second project name")
    p.add_argument(
        "--same-password",
        action="store_true",
        default=False,
        help="Use the same password for both projects",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 2 if projects differ",
    )
    p.set_defaults(func=cmd_compare)
