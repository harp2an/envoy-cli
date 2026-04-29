"""CLI commands for trend tracking."""

from __future__ import annotations

import sys
import argparse
from typing import Any

from envoy.trend import record_trend, get_trend, summarise_trend, clear_trends, TrendError


def cmd_trend_record(args: Any) -> None:
    try:
        entry = record_trend(args.project, args.metric, float(args.value))
        print(f"Recorded: {args.metric}={entry['value']} at {entry['timestamp']}")
    except (TrendError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_trend_list(args: Any) -> None:
    try:
        points = get_trend(args.project, args.metric)
        if not points:
            print(f"No data for metric '{args.metric}' in '{args.project}'.")
            return
        for p in points:
            print(f"  {p['timestamp']}  {p['metric']}={p['value']}")
    except TrendError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_trend_summary(args: Any) -> None:
    try:
        s = summarise_trend(args.project, args.metric)
        print(
            f"Project: {s['project']}  Metric: {s['metric']}\n"
            f"  Count: {s['count']}  Min: {s['min']}  Max: {s['max']}  "
            f"Avg: {s['avg']}  Direction: {s['direction']}"
        )
    except TrendError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_trend_clear(args: Any) -> None:
    try:
        n = clear_trends(args.project)
        print(f"Cleared {n} trend entries for '{args.project}'.")
    except TrendError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_trend_parser(subparsers: Any) -> None:
    p = subparsers.add_parser("trend", help="Track metric trends for projects")
    sub = p.add_subparsers(dest="trend_cmd", required=True)

    rec = sub.add_parser("record", help="Record a metric value")
    rec.add_argument("project")
    rec.add_argument("metric")
    rec.add_argument("value", type=float)
    rec.set_defaults(func=cmd_trend_record)

    lst = sub.add_parser("list", help="List recorded values for a metric")
    lst.add_argument("project")
    lst.add_argument("metric")
    lst.set_defaults(func=cmd_trend_list)

    summ = sub.add_parser("summary", help="Summarise trend for a metric")
    summ.add_argument("project")
    summ.add_argument("metric")
    summ.set_defaults(func=cmd_trend_summary)

    clr = sub.add_parser("clear", help="Clear all trend data for a project")
    clr.add_argument("project")
    clr.set_defaults(func=cmd_trend_clear)
