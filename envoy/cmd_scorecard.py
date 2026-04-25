"""CLI commands for project scorecards."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from envoy.scorecard import ScorecardError, compute_score, get_scorecard, list_scorecards, remove_scorecard


def cmd_scorecard_compute(args: Namespace) -> None:
    try:
        result = compute_score(args.project)
    except ScorecardError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Score for '{result['project']}': {result['score']}/100")
    for check, passed in result["checks"].items():
        mark = "✓" if passed else "✗"
        print(f"  {mark} {check}")


def cmd_scorecard_get(args: Namespace) -> None:
    result = get_scorecard(args.project)
    if result is None:
        print(f"No scorecard found for '{args.project}'.")
        return
    print(f"Score for '{result['project']}': {result['score']}/100")
    for check, passed in result["checks"].items():
        mark = "✓" if passed else "✗"
        print(f"  {mark} {check}")


def cmd_scorecard_list(args: Namespace) -> None:
    cards = list_scorecards()
    if not cards:
        print("No scorecards recorded.")
        return
    for card in sorted(cards, key=lambda c: c["score"], reverse=True):
        print(f"{card['project']}: {card['score']}/100")


def cmd_scorecard_remove(args: Namespace) -> None:
    try:
        remove_scorecard(args.project)
        print(f"Scorecard for '{args.project}' removed.")
    except ScorecardError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_scorecard_parser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser("scorecard", help="Project scorecards")
    sub = p.add_subparsers(dest="scorecard_cmd", required=True)

    pc = sub.add_parser("compute", help="Compute score for a project")
    pc.add_argument("project")
    pc.set_defaults(func=cmd_scorecard_compute)

    pg = sub.add_parser("get", help="Show cached scorecard")
    pg.add_argument("project")
    pg.set_defaults(func=cmd_scorecard_get)

    pl = sub.add_parser("list", help="List all scorecards")
    pl.set_defaults(func=cmd_scorecard_list)

    pr = sub.add_parser("remove", help="Remove a scorecard")
    pr.add_argument("project")
    pr.set_defaults(func=cmd_scorecard_remove)
