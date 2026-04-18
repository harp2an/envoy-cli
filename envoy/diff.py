"""Diff two versions of a project's env variables."""
from typing import Dict, List, Tuple
from envoy.storage import load_env
from envoy.crypto import decrypt


class DiffError(Exception):
    pass


def parse_pairs(text: str) -> Dict[str, str]:
    """Parse key=value lines into a dict, ignoring comments and blanks."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def diff_envs(
    old: Dict[str, str], new: Dict[str, str]
) -> List[Tuple[str, str, str, str]]:
    """
    Compare two env dicts.
    Returns list of (status, key, old_value, new_value).
    status is one of: 'added', 'removed', 'changed', 'unchanged'.
    """
    results = []
    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        if key not in old:
            results.append(("added", key, "", new[key]))
        elif key not in new:
            results.append(("removed", key, old[key], ""))
        elif old[key] != new[key]:
            results.append(("changed", key, old[key], new[key]))
        else:
            results.append(("unchanged", key, old[key], new[key]))
    return results


def diff_projects(
    project_a: str,
    password_a: str,
    project_b: str,
    password_b: str,
) -> List[Tuple[str, str, str, str]]:
    """Load and diff two stored projects."""
    try:
        cipher_a = load_env(project_a)
    except FileNotFoundError:
        raise DiffError(f"Project not found: {project_a}")
    try:
        cipher_b = load_env(project_b)
    except FileNotFoundError:
        raise DiffError(f"Project not found: {project_b}")

    text_a = decrypt(cipher_a, password_a)
    text_b = decrypt(cipher_b, password_b)
    return diff_envs(parse_pairs(text_a), parse_pairs(text_b))


def format_diff(diff: List[Tuple[str, str, str, str]], show_unchanged: bool = False) -> str:
    """Render diff as human-readable text."""
    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    for status, key, old_val, new_val in diff:
        if status == "unchanged" and not show_unchanged:
            continue
        sym = symbols[status]
        if status == "changed":
            lines.append(f"{sym} {key}: {old_val!r} -> {new_val!r}")
        elif status == "added":
            lines.append(f"{sym} {key}={new_val}")
        elif status == "removed":
            lines.append(f"{sym} {key}={old_val}")
        else:
            lines.append(f"{sym} {key}={old_val}")
    return "\n".join(lines)
