"""CLI commands for policy management."""

from __future__ import annotations

import json
import sys

from envoy.policy import PolicyError, check_policy, get_policy, remove_policy, set_policy
from envoy.storage import get_store_dir


def cmd_policy_set(args) -> None:
    store_dir = get_store_dir()
    rules: dict = {}
    if args.required_keys:
        rules["required_keys"] = [k.strip() for k in args.required_keys.split(",")]
    if args.forbidden_keys:
        rules["forbidden_keys"] = [k.strip() for k in args.forbidden_keys.split(",")]
    if args.max_keys is not None:
        rules["max_keys"] = args.max_keys
    try:
        set_policy(store_dir, args.project, rules)
        print(f"Policy set for '{args.project}'.")
    except PolicyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_policy_get(args) -> None:
    store_dir = get_store_dir()
    policy = get_policy(store_dir, args.project)
    if policy is None:
        print(f"No policy set for '{args.project}'.")
    else:
        print(json.dumps(policy, indent=2))


def cmd_policy_remove(args) -> None:
    store_dir = get_store_dir()
    try:
        remove_policy(store_dir, args.project)
        print(f"Policy removed for '{args.project}'.")
    except PolicyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_policy_check(args) -> None:
    from envoy.storage import load_env
    from envoy.diff import parse_pairs
    store_dir = get_store_dir()
    try:
        raw = load_env(store_dir, args.project, args.password)
        pairs = parse_pairs(raw)
        violations = check_policy(store_dir, args.project, pairs)
    except PolicyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    if not violations:
        print("Policy check passed.")
    else:
        for v in violations:
            print(f"  VIOLATION: {v}")
        sys.exit(1)


def register_policy_parser(subparsers) -> None:
    p = subparsers.add_parser("policy", help="Manage project policies")
    sub = p.add_subparsers(dest="policy_cmd", required=True)

    ps = sub.add_parser("set", help="Set policy for a project")
    ps.add_argument("project")
    ps.add_argument("--required-keys", dest="required_keys", default="")
    ps.add_argument("--forbidden-keys", dest="forbidden_keys", default="")
    ps.add_argument("--max-keys", dest="max_keys", type=int, default=None)
    ps.set_defaults(func=cmd_policy_set)

    pg = sub.add_parser("get", help="Show policy for a project")
    pg.add_argument("project")
    pg.set_defaults(func=cmd_policy_get)

    pr = sub.add_parser("remove", help="Remove policy from a project")
    pr.add_argument("project")
    pr.set_defaults(func=cmd_policy_remove)

    pc = sub.add_parser("check", help="Check project env against its policy")
    pc.add_argument("project")
    pc.add_argument("--password", required=True)
    pc.set_defaults(func=cmd_policy_check)
