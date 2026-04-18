"""CLI command for importing .env files."""

import argparse
import getpass
import sys

from envoy.import_env import import_dotenv_file, ImportError as EnvImportError


def cmd_import(args: argparse.Namespace) -> None:
    """Handle the 'import' subcommand.

    Prompts the user for a password, then imports variables from a .env file
    into the specified project's envoy storage.
    """
    password = getpass.getpass(f"Password for '{args.project}': ")
    try:
        count = import_dotenv_file(args.project, args.file, password)
        print(f"Imported {count} variable(s) into project '{args.project}'.")
    except FileNotFoundError:
        print(f"Import failed: file '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    except EnvImportError as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        sys.exit(1)


def register_import_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'import' subcommand with the given subparsers."""
    p = subparsers.add_parser(
        "import",
        help="Import a .env file into envoy storage",
    )
    p.add_argument("project", help="Project name")
    p.add_argument("file", help="Path to the .env file to import")
    p.set_defaults(func=cmd_import)
