"""CLI commands for project rating management."""

import sys
from envoy.rating import set_rating, get_rating, remove_rating, list_ratings, RatingError


def cmd_rating_set(args) -> None:
    try:
        entry = set_rating(args.project, args.score, note=args.note or "")
        print(f"Rated '{args.project}': {entry['score']}/5", end="")
        if entry["note"]:
            print(f" — {entry['note']}", end="")
        print()
    except RatingError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_rating_get(args) -> None:
    entry = get_rating(args.project)
    if entry is None:
        print(f"No rating for '{args.project}'")
    else:
        note_part = f" — {entry['note']}" if entry.get("note") else ""
        print(f"{args.project}: {entry['score']}/5{note_part}")


def cmd_rating_remove(args) -> None:
    try:
        remove_rating(args.project)
        print(f"Rating removed for '{args.project}'")
    except RatingError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_rating_list(args) -> None:
    ratings = list_ratings()
    if not ratings:
        print("No ratings recorded.")
        return
    for project, entry in sorted(ratings.items()):
        note_part = f" — {entry['note']}" if entry.get("note") else ""
        print(f"{project}: {entry['score']}/5{note_part}")


def register_rating_parser(subparsers) -> None:
    p = subparsers.add_parser("rating", help="Manage project ratings")
    sub = p.add_subparsers(dest="rating_cmd", required=True)

    ps = sub.add_parser("set", help="Set a rating for a project")
    ps.add_argument("project")
    ps.add_argument("score", type=int, choices=[1, 2, 3, 4, 5])
    ps.add_argument("--note", default="", help="Optional note")
    ps.set_defaults(func=cmd_rating_set)

    pg = sub.add_parser("get", help="Get rating for a project")
    pg.add_argument("project")
    pg.set_defaults(func=cmd_rating_get)

    pr = sub.add_parser("remove", help="Remove rating for a project")
    pr.add_argument("project")
    pr.set_defaults(func=cmd_rating_remove)

    pl = sub.add_parser("list", help="List all ratings")
    pl.set_defaults(func=cmd_rating_list)
