"""CLI commands for project reminders."""

import sys

from envoy.reminder import (
    ReminderError,
    set_reminder,
    get_reminder,
    remove_reminder,
    list_reminders,
    due_soon,
)


def cmd_reminder_set(args) -> None:
    try:
        due = set_reminder(args.project, args.message, args.days)
        print(f"Reminder set for '{args.project}' — due {due}.")
    except ReminderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_reminder_get(args) -> None:
    reminder = get_reminder(args.project)
    if reminder is None:
        print(f"No reminder set for '{args.project}'.")
    else:
        print(f"[{args.project}] {reminder['message']} (due {reminder['due']})")


def cmd_reminder_remove(args) -> None:
    try:
        remove_reminder(args.project)
        print(f"Reminder for '{args.project}' removed.")
    except ReminderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_reminder_list(args) -> None:
    reminders = list_reminders()
    if not reminders:
        print("No reminders set.")
        return
    for r in reminders:
        print(f"{r['due']}  {r['project']:20s}  {r['message']}")


def cmd_reminder_due(args) -> None:
    days = getattr(args, "days", 7)
    reminders = due_soon(days)
    if not reminders:
        print(f"No reminders due within {days} day(s).")
        return
    for r in reminders:
        print(f"{r['due']}  {r['project']:20s}  {r['message']}")


def register_reminder_parser(subparsers) -> None:
    p = subparsers.add_parser("reminder", help="Manage project reminders")
    sub = p.add_subparsers(dest="reminder_cmd", required=True)

    ps = sub.add_parser("set", help="Set a reminder for a project")
    ps.add_argument("project")
    ps.add_argument("message")
    ps.add_argument("--days", type=int, default=7, help="Days until due (default: 7)")
    ps.set_defaults(func=cmd_reminder_set)

    pg = sub.add_parser("get", help="Get reminder for a project")
    pg.add_argument("project")
    pg.set_defaults(func=cmd_reminder_get)

    pr = sub.add_parser("remove", help="Remove a reminder")
    pr.add_argument("project")
    pr.set_defaults(func=cmd_reminder_remove)

    pl = sub.add_parser("list", help="List all reminders")
    pl.set_defaults(func=cmd_reminder_list)

    pd = sub.add_parser("due", help="Show reminders due soon")
    pd.add_argument("--days", type=int, default=7)
    pd.set_defaults(func=cmd_reminder_due)
