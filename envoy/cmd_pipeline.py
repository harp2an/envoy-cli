"""CLI sub-commands for pipeline management."""
from __future__ import annotations

import sys

from envoy.pipeline import (
    PipelineError,
    create_pipeline,
    delete_pipeline,
    get_pipeline,
    list_pipelines,
)


def cmd_pipeline_create(args) -> None:
    try:
        create_pipeline(args.name, args.steps)
        print(f"Pipeline '{args.name}' created with steps: {', '.join(args.steps)}")
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pipeline_show(args) -> None:
    try:
        steps = get_pipeline(args.name)
        print(f"Pipeline '{args.name}':")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pipeline_delete(args) -> None:
    try:
        delete_pipeline(args.name)
        print(f"Pipeline '{args.name}' deleted.")
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pipeline_list(args) -> None:
    pipelines = list_pipelines()
    if not pipelines:
        print("No pipelines defined.")
        return
    for name, steps in pipelines.items():
        print(f"{name}: {' -> '.join(steps)}")


def register_pipeline_parser(subparsers) -> None:
    p = subparsers.add_parser("pipeline", help="Manage reusable operation pipelines")
    sub = p.add_subparsers(dest="pipeline_cmd", required=True)

    pc = sub.add_parser("create", help="Create a new pipeline")
    pc.add_argument("name", help="Pipeline name")
    pc.add_argument("steps", nargs="+", help="Ordered list of steps")
    pc.set_defaults(func=cmd_pipeline_create)

    ps = sub.add_parser("show", help="Show steps of a pipeline")
    ps.add_argument("name", help="Pipeline name")
    ps.set_defaults(func=cmd_pipeline_show)

    pd = sub.add_parser("delete", help="Delete a pipeline")
    pd.add_argument("name", help="Pipeline name")
    pd.set_defaults(func=cmd_pipeline_delete)

    pl = sub.add_parser("list", help="List all pipelines")
    pl.set_defaults(func=cmd_pipeline_list)
