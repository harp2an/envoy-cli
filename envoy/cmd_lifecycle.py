"""CLI commands for project lifecycle management."""

import sys
from envoy.lifecycle import LifecycleError, set_state, get_state, list_states, remove_state, VALID_STATES


def cmd_lifecycle_set(args) -> None:
    try:
        entry = set_state(args.project, args.state)
        print(f"Project '{args.project}' state set to '{args.state}' at {entry['updated_at']}.")
    except LifecycleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_lifecycle_get(args) -> None:
    entry = get_state(args.project)
    if entry is None:
        print(f"No lifecycle state set for '{args.project}'.")
    else:
        state = entry.get("state", "unknown")
        updated = entry.get("updated_at", "n/a")
        created = entry.get("created_at", "n/a")
        print(f"Project: {args.project}")
        print(f"  State:      {state}")
        print(f"  Created:    {created}")
        print(f"  Updated:    {updated}")


def cmd_lifecycle_list(args) -> None:
    entries = list_states()
    if not entries:
        print("No lifecycle states recorded.")
        return
    for project, entry in sorted(entries.items()):
        state = entry.get("state", "unknown")
        updated = entry.get("updated_at", "n/a")
        print(f"  {project:<30} {state:<12} {updated}")


def cmd_lifecycle_remove(args) -> None:
    removed = remove_state(args.project)
    if removed:
        print(f"Lifecycle state removed for '{args.project}'.")
    else:
        print(f"No lifecycle state found for '{args.project}'.")


def register_lifecycle_parser(subparsers) -> None:
    p = subparsers.add_parser("lifecycle", help="Manage project lifecycle states")
    sub = p.add_subparsers(dest="lifecycle_cmd", required=True)

    p_set = sub.add_parser("set", help="Set lifecycle state for a project")
    p_set.add_argument("project")
    p_set.add_argument("state", choices=VALID_STATES)
    p_set.set_defaults(func=cmd_lifecycle_set)

    p_get = sub.add_parser("get", help="Get lifecycle state for a project")
    p_get.add_argument("project")
    p_get.set_defaults(func=cmd_lifecycle_get)

    p_list = sub.add_parser("list", help="List all lifecycle states")
    p_list.set_defaults(func=cmd_lifecycle_list)

    p_rm = sub.add_parser("remove", help="Remove lifecycle tracking for a project")
    p_rm.add_argument("project")
    p_rm.set_defaults(func=cmd_lifecycle_remove)
