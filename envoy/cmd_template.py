"""CLI commands for template rendering."""

import argparse
import sys

from envoy.template import TemplateError, load_template_file, parse_template, render_template
from envoy.storage import store_env


def _parse_vars(var_list: list[str]) -> dict[str, str]:
    result = {}
    for item in var_list or []:
        if "=" not in item:
            print(f"Invalid variable assignment: {item!r}", file=sys.stderr)
            sys.exit(1)
        k, v = item.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def cmd_template_render(args: argparse.Namespace) -> None:
    try:
        template_text = load_template_file(args.template)
    except TemplateError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    variables = _parse_vars(args.var)

    try:
        rendered = render_template(template_text, variables, strict=not args.loose)
    except TemplateError as e:
        print(f"Template error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.project:
        password = args.password or input("Password: ")
        store_env(args.project, rendered, password)
        print(f"Stored rendered template as project '{args.project}'.")
    else:
        print(rendered, end="")


def cmd_template_vars(args: argparse.Namespace) -> None:
    try:
        template_text = load_template_file(args.template)
    except TemplateError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    variables = parse_template(template_text)
    if variables:
        for v in variables:
            print(v)
    else:
        print("No variables found in template.")


def register_template_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("template", help="Render .env templates")
    sub = p.add_subparsers(dest="template_cmd", required=True)

    render_p = sub.add_parser("render", help="Render a template to stdout or a project")
    render_p.add_argument("template", help="Path to template file")
    render_p.add_argument("-v", "--var", action="append", metavar="KEY=VALUE", help="Variable substitution")
    render_p.add_argument("--project", help="Store result as this project")
    render_p.add_argument("--password", help="Encryption password")
    render_p.add_argument("--loose", action="store_true", help="Leave unresolved variables as-is")
    render_p.set_defaults(func=cmd_template_render)

    vars_p = sub.add_parser("vars", help="List variables in a template")
    vars_p.add_argument("template", help="Path to template file")
    vars_p.set_defaults(func=cmd_template_vars)
