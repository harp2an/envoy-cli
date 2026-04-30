"""CLI commands for compliance checking."""

from __future__ import annotations

import sys

from envoy.compliance import (
    ComplianceError,
    STANDARDS,
    check_compliance,
    get_compliance,
    list_compliance,
    remove_compliance,
)


def cmd_compliance_check(args) -> None:
    try:
        present_keys = args.keys.split(",") if args.keys else []
        result = check_compliance(
            project=args.project,
            standard=args.standard,
            key_count=args.key_count,
            present_keys=present_keys,
        )
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.project} against '{result.standard}'")
        for v in result.violations:
            print(f"  - {v}")
    except ComplianceError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_compliance_get(args) -> None:
    record = get_compliance(args.project)
    if record is None:
        print(f"No compliance record for '{args.project}'")
        return
    status = "PASS" if record["passed"] else "FAIL"
    print(f"[{status}] {record['project']} / {record['standard']}")
    for v in record.get("violations", []):
        print(f"  - {v}")


def cmd_compliance_list(args) -> None:
    records = list_compliance()
    if not records:
        print("No compliance records found.")
        return
    for project, rec in records.items():
        status = "PASS" if rec["passed"] else "FAIL"
        print(f"  {project}: [{status}] {rec['standard']}")


def cmd_compliance_remove(args) -> None:
    try:
        remove_compliance(args.project)
        print(f"Removed compliance record for '{args.project}'.")
    except ComplianceError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def register_compliance_parser(subparsers) -> None:
    p = subparsers.add_parser("compliance", help="Compliance checking commands")
    sub = p.add_subparsers(dest="compliance_cmd")

    chk = sub.add_parser("check", help="Check project compliance")
    chk.add_argument("project")
    chk.add_argument("--standard", default="basic", choices=list(STANDARDS))
    chk.add_argument("--key-count", type=int, default=0, dest="key_count")
    chk.add_argument("--keys", default="", help="Comma-separated list of present keys")
    chk.set_defaults(func=cmd_compliance_check)

    gt = sub.add_parser("get", help="Get last compliance result for a project")
    gt.add_argument("project")
    gt.set_defaults(func=cmd_compliance_get)

    ls = sub.add_parser("list", help="List all compliance records")
    ls.set_defaults(func=cmd_compliance_list)

    rm = sub.add_parser("remove", help="Remove compliance record for a project")
    rm.add_argument("project")
    rm.set_defaults(func=cmd_compliance_remove)
