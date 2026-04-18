"""CLI handlers for the `envoy config` subcommand."""

import argparse
from envoy.config import (
    load_config,
    set_config_value,
    unset_config_value,
    DEFAULT_CONFIG,
)

VALID_KEYS = list(DEFAULT_CONFIG.keys())


def cmd_config_set(args: argparse.Namespace) -> None:
    try:
        set_config_value(args.key, args.value)
        print(f"Set {args.key} = {args.value}")
    except KeyError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_config_get(args: argparse.Namespace) -> None:
    from envoy.config import get_config_value
    value = get_config_value(args.key)
    if value is None:
        print(f"{args.key} is not set")
    else:
        print(f"{args.key} = {value}")


def cmd_config_unset(args: argparse.Namespace) -> None:
    try:
        unset_config_value(args.key)
        print(f"Unset {args.key}")
    except KeyError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


def cmd_config_list(_args: argparse.Namespace) -> None:
    config = load_config()
    for key, value in config.items():
        display = value if value is not None else "(not set)"
        print(f"{key} = {display}")


def register_config_parser(subparsers) -> None:
    p = subparsers.add_parser("config", help="Manage envoy configuration")
    sub = p.add_subparsers(dest="config_cmd", required=True)

    p_set = sub.add_parser("set", help="Set a config value")
    p_set.add_argument("key", choices=VALID_KEYS)
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_config_set)

    p_get = sub.add_parser("get", help="Get a config value")
    p_get.add_argument("key", choices=VALID_KEYS)
    p_get.set_defaults(func=cmd_config_get)

    p_unset = sub.add_parser("unset", help="Unset a config value")
    p_unset.add_argument("key", choices=VALID_KEYS)
    p_unset.set_defaults(func=cmd_config_unset)

    p_list = sub.add_parser("list", help="List all config values")
    p_list.set_defaults(func=cmd_config_list)
